import pycocotools
import os
import numpy as np
import torch
import torch.utils.data
from PIL import Image, ImageDraw
import pandas as pd
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from engine import train_one_epoch, evaluate
import utils
import transforms as T
import torchvision.transforms.functional as TF
import torchvision
import numpy as np
import scipy.stats as st
import seaborn as sns
import pandas as pd

# This is a script which will take a CSV generated by xml_to_csv.py and a folder of the images corresponding to those labels
# to train an object detection model to segment ad blocks. The file outputted here is used in our pipeline.


def parse_one_annot(path_to_data_file, filename):
    data = pd.read_csv(path_to_data_file)
    boxes_array = data[data["filename"] == filename][
        ["xmin", "ymin", "xmax", "ymax"]
    ].values

    labels = data[data["filename"] == filename][["class"]].values.flatten()
    labels = np.where(labels == "ad_block", 1, 0)
    labels = torch.tensor(labels, dtype=torch.int64)

    return boxes_array, labels


class RaccoonDataset(torch.utils.data.Dataset):
    def __init__(self, root, data_file, img_folder, transforms=None):
        self.root = root
        self.transforms = transforms
        self.img_folder = img_folder
        self.imgs = sorted(os.listdir(img_folder))
        self.path_to_data_file = data_file

    def __getitem__(self, idx):
        # load images and bounding boxes
        img_path = os.path.join(self.root, self.img_folder, self.imgs[idx])
        img = Image.open(img_path).convert("RGB")
        box_list, labels = parse_one_annot(self.path_to_data_file, self.imgs[idx])
        boxes = torch.as_tensor(box_list, dtype=torch.float32)

        num_objs = len(box_list)
        # there is only one class
        labels = torch.ones((num_objs,), dtype=torch.int64)
        image_id = torch.tensor([idx])
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        # suppose all instances are not crowd
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)
        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd

        if self.transforms is not None:
            img, target = self.transforms(img, target)
        return img, target

    def __len__(self):
        return len(self.imgs)


def get_model(num_classes):
    # load an object detection model pre-trained on COCO
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    # get the number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new on
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model


def get_transform(train):
    transforms = []
    # converts the image, a PIL image, into a PyTorch Tensor
    transforms.append(T.ToTensor())
    # # Make black and white
    # transforms.append(T.BlackAndWhite(0))
    if train:
        # during training, randomly flip the training images
        # and ground-truth for data augmentation
        transforms.append(T.RandomHorizontalFlip(0.5))
    return T.Compose(transforms)


torch.cuda.is_available()

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
# our dataset has two classes only - ad block and not ad block
num_classes = 2
# get the model using our helper function
model = get_model(num_classes)
# move model to the right device
model.to(device)
# construct an optimizer
params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
# and a learning rate scheduler which decreases the learning rate by # 10x every 3 epochs
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

# let's train it for 10 epochs
max_p = 0
max_r = 0
# train test split
dataset = RaccoonDataset(
    root="./",
    data_file="./labels.csv",
    img_folder="./images",
    transforms=get_transform(train=True),
)
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
indices = torch.randperm(len(dataset)).tolist()
dataset_train = torch.utils.data.Subset(dataset, indices[:train_size])
dataset_test = torch.utils.data.Subset(dataset, indices[train_size:])
model = get_model(num_classes)
# move model to the right device
model.to(device)
# construct an optimizer
params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
# and a learning rate scheduler which decreases the learning rate by # 10x every 3 epochs
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
data_loader = torch.utils.data.DataLoader(
    dataset_train,
    batch_size=2,
    shuffle=True,
    num_workers=4,
    collate_fn=utils.collate_fn,
)
data_loader_test = torch.utils.data.DataLoader(
    dataset_test,
    batch_size=1,
    shuffle=False,
    num_workers=4,
    collate_fn=utils.collate_fn,
)
print(
    "We have: {} examples, {} are training and {} testing".format(
        len(dataset) + len(dataset_test), len(dataset), len(dataset_test)
    )
)
num_epochs = 10
for epoch in range(num_epochs):
    # train for one epoch, printing every 10 iterations
    train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq=10)
    # update the learning rate
    lr_scheduler.step()
    metrics = evaluate(model, data_loader_test, device=device)
    print(metrics.coco_eval["bbox"].stats[6])
    print(metrics.coco_eval["bbox"].stats[16])
    if metrics.coco_eval["bbox"].stats[6] > max_p:
        max_p = metrics.coco_eval["bbox"].stats[6]
        max_r = metrics.coco_eval["bbox"].stats[16]
        best_model = model


print(max_p, max_r)

torch.save(best_model.state_dict(), "models/color_lisa")
device = torch.device("cpu")
model.to(device)
torch.save(best_model.state_dict(), "models/color_lisa_cpu")
