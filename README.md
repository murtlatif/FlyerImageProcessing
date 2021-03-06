# Flyer Image Processing with Daisy Intelligence

## Capstone Project

_Created by Stephen Brade, Sandra Petkovic, Murtaza Latif and Lisa Li_

To setup the program, read the [Getting Started](docs/GettingStarted.md) documentation.

## How to Label Flyers to Train the Model on a New Grocer

### LabelImg

Please have a subset of the grocer's flyer page images (as `.png` files) in a folder called `data`.

The tool we used to annotate flyer images is called LabelImg. More details about the tool can be found at [https://github.com/tzutalin/labelImg](https://github.com/tzutalin/labelImg).

Installation

```bash
$ pip3 install labelImg
```

Running it

```bash
$ labelImg
```

Once the desktop app opens, select the "Open Dir" button on the lefthand side and select the directory where you've stored your flyer images.

On the right hand side, there is a field `[] Use default label ______`. Check the field and set the default label as `ad_block` (`[x] Use default label __ad_block__`). We will only be labelling ad blocks, and doing this step will save you the effort of manually labelling.

Press the key `w` on your keyboard. Drag to create a rectangle around an ad block; make sure all the information about the ad block is contained in the rectangle (such as the image, product codes, sale icons, if the ad blocks have these). Ignore blocks that may appear to be an ad block, but lack crucial details such as price (we have come across a couple edge cases like this).

After you label your first ad block, the desktop app should look like the example below:
![](README_images/labelImg1.png)

Now do this for every ad block on the page. Ensure that every rectangle is labelled with `ad_block`. Once you're done, click on "Save" on the left hand side. Save in the same folder and the same name as the flyer image. This will create a file called `<flyer_image_name>.xml` that will be processed later. Repeat this process for every individual flyer page image.

Once you are done labelling, you may close labelImg.

### Turning LabelImg xml files into training data

Your `data` folder should now contain an `.xml` file for every flyer image. Move the `data` folder to the `Segmentation/` directory is this repo.

To seperate the `.xml` and flyer image files into seperate folders, run

```bash
$ python3 organize_files.py
```

The `.xml` files are now in a folder called `Segmentation/annotation/` and the images are in `Segmentation/images/`. To turn the `.xml` files into `labels.csv`, run

```bash
$ python3 xml_to_csv.py
```

Should you change the directories or filename mentioned above, please change the routes of `dataset` in `train.py` here

```python
dataset = RaccoonDataset(
    root="./",
    data_file="./labels.csv",
    img_folder="./images",
    transforms=get_transform(train=True),
)
```

The saved model (use the cpu model if you do not have a gpu) will be passed through the -sm argument in the config for the Flyer Processing Pipeline.
