from .productclassifier import ProductClassifier
from config import Config

product_classifier = ProductClassifier(Config.args.classifier_model_state)
