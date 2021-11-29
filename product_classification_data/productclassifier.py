from joblib import load
from sentence_transformers import SentenceTransformer


class ProductClassifier():
    def __init__(self, model_path):
        self.model = load(model_path)
        self.BERT = SentenceTransformer('bert-base-nli-mean-tokens')
        self.categories = [
            "produce",   # fruits, vegetables 0
            "deli",      # chicken, beef, eggs 1
            "grocery",   # chips, pop, jello, baking, crackers, flour 2
            "bakery",    # cakes, breads, cookies 3
            "dairy",     # butter, milk, yoghurt 4
            "household",  # non-food items
        ]

    def classify(self, name):
        embedding = [self.BERT.encode(name).tolist()]
        category = int(self.model.predict(embedding))
        confidence = self.model.predict_proba(embedding)[0][category]
        return self.categories[category], confidence
