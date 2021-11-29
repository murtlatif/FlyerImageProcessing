from googlesearch import search
import pandas as pd
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import RegexpTokenizer
import numpy as np
from nltk.stem import *

wnLem = WordNetLemmatizer()

N = 5
tokenizer = RegexpTokenizer(r"\w+")
#                0         1       2         3          4        5            6
categories = ["produce", "deli", "grocery", "bakery", "dairy", "household"]

items = pd.read_csv("../product_classification_data/products_by_name.csv")[
    ["text", "label"]
]

bakery = (
    pd.read_csv("../product_classification_data/bakery.csv").to_numpy().flatten()[:58]
)
dairy = (
    pd.read_csv("../product_classification_data/dairy.csv").to_numpy().flatten()[:58]
)
meat = pd.read_csv("../product_classification_data/meat.csv").to_numpy().flatten()[:58]
grocery = (
    pd.read_csv("../product_classification_data/grocery.csv").to_numpy().flatten()[:58]
)
fruit = (
    pd.read_csv("../product_classification_data/fruit.csv").to_numpy().flatten()[:58]
)
veg = (
    pd.read_csv("../product_classification_data/vegetable.csv")
    .to_numpy()
    .flatten()[:58]
)
produce = (
    pd.read_csv("../product_classification_data/produce.csv").to_numpy().flatten()[:58]
)
household = (
    pd.read_csv("../product_classification_data/household.csv")
    .to_numpy()
    .flatten()[:58]
)
# print(len(bakery), len(dairy), len(meat), len(grocery), len(fruit), len(veg))


def get_pred(query):
    prediction = {"category_idx": None, "category": None, "max_score": -1}
    failed_url_count = 0
    for i, url in enumerate(
        search(query.lower(), tld="com", lang="en", num=N, stop=N, pause=2)
    ):
        # print("url", url)
        try:
            r = requests.get(url, timeout=5)
        except:
            failed_url_count += 1
            continue
        if r.status_code > 399:
            failed_url_count += 1
            continue
        if (
            url
            == "https://www.freshdirect.com/pdp.jsp?productId=orgveg_leek_bnch&catId=lk"
        ):
            print("r.content", r.content)
        soup = BeautifulSoup(r.content, "html5lib")

        table = soup.find("body")
        for tag in [
            "body",
            "script",
            "noscript",
            "iframe",
            "style",
            "header",
            "footer",
        ]:
            for s in table.select(tag):
                s.extract()

        tokenized_words = set()

        prev_word, prev_prev_word = "", ""
        for word in tokenizer.tokenize(table.text):
            word = wnLem.lemmatize(word.lower())
            tokenized_words.add(word)
            if prev_word != "":
                tokenized_words.add(prev_word + " " + word)
            if prev_prev_word != "":
                tokenized_words.add(prev_prev_word + " " + prev_word + " " + word)
            prev_prev_word, prev_word = prev_word, word

        scores = np.array([])

        for category in [produce, meat, grocery, bakery, dairy, household]:
            score = np.mean(
                np.array([1 if word in tokenized_words else 0 for word in category])
            )
            # print("------")
            # for word in tokenized_words:
            #     if word in category:
            #         print(word)
            # print("------")
            scores = np.append(scores, score)

        if np.amax(scores) > prediction["max_score"]:
            prediction = {
                "category_idx": np.argmax(scores),
                "category": categories[np.argmax(scores)],
                "max_score": np.amax(scores),
            }
        # print("scores", scores)

    return None if failed_url_count == N else prediction


cnt = 0
no_search_results = 0
for i, row in items.iterrows():
    item = row.text
    label = row.label
    predicted = get_pred(item)
    print("predicted", predicted)
    if predicted == None:
        no_search_results += 1
        continue
    if predicted["max_score"] > 0:
        cnt += label == predicted["category_idx"]

    print(
        f"\n---{item}, pred: {predicted['category'] if predicted['max_score'] > 0 else None}, actual: {categories[label]} ---\n"
    )
print(f"Number of items with no search results: {no_search_results}")
print(f"Accuracy: {cnt / (len(items) - no_search_results)}")
