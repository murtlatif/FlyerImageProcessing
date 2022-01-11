Hi

Training ad block detection model
- Create a CSV file from a folder of your labelled xml files (xml_to_csv will help)
- Use this csv and a folder of all flyer pages you've labelled as the data_file and img_folder in train.py respectively
- The saved model (use the cpu model if you do not have a gpu) will be passed through the -sm argument in the config for the
    Flyer Processing Pipeline