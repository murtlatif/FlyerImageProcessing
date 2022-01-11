import os
from shutil import copyfile

# Create directories necessary for storing images and annotations
image_path = os.path.join(os.getcwd(), 'data')
annotations = '/'.join((image_path.split('/')[:-1])) + '/annotations'
if not os.path.isdir(annotations):
    os.mkdir(annotations)
images = '/'.join(image_path.split('/')[:-1]) + '/images'
if not os.path.isdir(images):
    os.mkdir(images)

for root, dirs, files in os.walk(image_path):
    # Find all xml files and move them into folder with a unique name
    for filename in files:
        old_path = os.path.join(root, filename)
        new_name = '_'.join(os.path.join(root, filename).split('/')[-2:])
        new_path = os.path.join(annotations, new_name)
        if '.xml' in new_name:
            copyfile(old_path, new_path)
    
    # Find all png files with an xml file
    # Swap for other image tyep if necessary
    for filename in files:
        old_path = os.path.join(root, filename)
        new_name = '_'.join(os.path.join(root, filename).split('/')[-2:])
        new_path = os.path.join(annotations, new_name)
        if '.png' in new_name:
            annot = new_path.replace('.png', '.xml')
            if os.path.isfile(annot):
                new_path = os.path.join(images, new_name)
                copyfile(old_path, new_path)
        

