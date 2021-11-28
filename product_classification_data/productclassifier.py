import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from scipy import stats
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sn
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn import svm
from joblib import dump, load

class ProductClassifier():
  def __init__(self, model_path):
    self.model = load(model_path)
    self.BERT = SentenceTransformer('bert-base-nli-mean-tokens')
    self.categories = [
                        "produce", # fruits, vegetables 0
                        "deli",     # chicken, beef, eggs 1
                        "grocery",  # chips, pop, jello, baking, crackers, flour 2
                        "bakery",   # cakes, breads, cookies 3
                        "dairy",    # butter, milk, yoghurt 4
                      ]


  def classify(self, name):
    embedding = [self.BERT.encode(name).tolist()]
    category = int(self.model.predict(embedding))
    confidence = self.model.predict_proba(embedding)[0][category]
    return categories[category], confidence

