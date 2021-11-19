import pycocotools
import os
import numpy as np
import torch
import torch.utils.data
from PIL import Image, ImageDraw
import pandas as pd
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from engine import train_one_epoch, evaluate
from RaccoonDataset import RaccoonDataset
import utils
import transforms as T
import torchvision

def get_transform(train):
   transforms = []
   # converts the image, a PIL image, into a PyTorch Tensor
   transforms.append(T.ToTensor())
   if train:
        # during training, randomly flip the training images
        # and ground-truth for data augmentation
        transforms.append(T.RandomHorizontalFlip(0.5))
   return T.Compose(transforms)

class GetBoxes():
    def __init__(self, num_classes, model_file, device, data_folder):
        self.num_classes = num_classes
        self.model_file = model_file
        self.device = device
        self.data_folder = data_folder
        self.getModel()
        self.getData()

    def getModel(self):
        # load an object detection model pre-trained on COCO
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        # get the number of input features for the classifier
        in_features = self.model.roi_heads.box_predictor.cls_score.in_features
        # replace the pre-trained head with a new on
        self.model.roi_heads.box_predictor = FastRCNNPredictor(in_features, self.num_classes)
        self.model.load_state_dict(torch.load(self.model_file))
        self.model.to(self.device)

    def getData(self):
        self.dataset = RaccoonDataset(root=self.data_folder, data_file=None, transforms = get_transform(train=False))
        print(len(self.dataset))


    def getBoxes(self, img_folder):
        for i in range(0, len(self.dataset)):
            self.boxes_dict = {}
            img, target = self.dataset[i]

            #put the model in evaluation mode and get boxes
            self.model.eval()
            with torch.no_grad():
                prediction = self.model([img.to(device)])

            # Get the image and initialize drawing
            image = Image.fromarray(img.mul(255).permute(1, 2,0).byte().numpy())
            draw = ImageDraw.Draw(image)
            name = target["name"]
            # get ready to store a list of lists where the sublists are vertices for one box
            self.boxes_dict[name] = []
            # Go through all boxes the model predicted
            for element in range(len(prediction[0]["boxes"])):
                boxes = prediction[0]["boxes"][element].cpu().numpy()
                score = np.round(prediction[0]["scores"][element].cpu().numpy(),decimals= 4)
                # Only select boxes the model is confident about
                if score > 0.8:
                    self.boxes_dict[name] += [[(boxes[0], boxes[1]), (boxes[2], boxes[1]), (boxes[0], boxes[3]), (boxes[2], boxes[3])]]
                    draw.rectangle([(boxes[0], boxes[1]), (boxes[2], boxes[3])], outline ="red", width =3)
                    draw.text((boxes[0], boxes[1]), text = str(score))
                    
            # Uncomment if you want to see how the model is doing
            # image.save('things/test_{}.png'.format(i))
    
    def retBoxes(self):
        return self.boxes_dict[name]

# Example use
# device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
# getboxes = GetBoxes(2, 'models/mymodel', device, '/home/stephen/Segmentation/test')
# getboxes.getBoxes('test')
# print(getboxes.boxes_dict)