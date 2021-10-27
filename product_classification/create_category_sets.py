import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.stem import *

nltk.download("wordnet")

wnLem = WordNetLemmatizer()

# Produce
produce = set()
for j in [
    "https://www.halfyourplate.ca/fruits-and-veggies/fruits-a-z/",
    "https://www.halfyourplate.ca/fruits-and-veggies/veggies-a-z/",
]:
    r = requests.get(j)
    soup = BeautifulSoup(r.content, "html5lib")

    table = soup.find("ul", attrs={"class": "fv-list"})
    for row in table.findAll("a"):
        item = row.text.strip().strip("*").lower()
        if not item:
            continue
        elif ", " in item:
            item = item.split(", ")
            produce.add(wnLem.lemmatize(item[1] + " " + item[0]))
            produce.add(wnLem.lemmatize(item[0]))
        elif "(" in item:
            item = item.replace(")", "").split("(")
            produce.add(wnLem.lemmatize(item[1]))
            produce.add(wnLem.lemmatize(item[0]))
        else:
            produce.add(wnLem.lemmatize(item))


df = pd.DataFrame(list(produce))
df.columns = ["produce"]
df.to_csv("produce.csv", index=None)

deli = set()
# Meat
r = requests.get(
    "http://jamesburden.co.uk/products/meat-poultry-and-game/full-list-of-meat-products/"
)
soup = BeautifulSoup(r.content, "html5lib")
table = soup.find("section", attrs={"class": "entry"})
for row in table.findAll("div", attrs={"class": "fourcol-one"}):
    for s in row.select("strong"):
        s.extract()
    for s in row.select("em"):
        s.extract()
    items = row.text.strip().strip("*").lower().split("\n")
    items = [wnLem.lemmatize(word) for word in items if word]
    deli.update(set(items))

# Eggs
r = requests.get("https://eggs.ab.ca/healthy-eggs/types-of-eggs/")
soup = BeautifulSoup(r.content, "html5lib")
table = soup.findAll("div", attrs={"class": "col-12"})

for rows in table:
    if not rows:
        continue
    rows = rows.findAll("h3")
    for row in rows:
        item = row.text.lower()
        if "egg" in item:
            deli.add(wnLem.lemmatize(item))

df = pd.DataFrame(list(deli))
df.columns = ["deli"]
df.to_csv("deli.csv", index=None)


bakery = set()
# Bakery
r = requests.get("https://www.craftybaking.com/learn/baked-goods")
soup = BeautifulSoup(r.content, "html5lib")
table = soup.find("section", attrs={"class": "page-body"})
for row in table.findAll("strong"):
    item = (
        row.text.lower()
        .replace("\xa0", " ")
        .replace(", etc", "")
        .replace(",", "")
        .replace(" and", "")
    )
    if "vegan" not in item and "fat" not in item and item != "community":
        bakery.update(set([wnLem.lemmatize(word) for word in item.split(" ")]))

r = requests.get("https://www.leaf.tv/articles/types-of-bakery-products/")
soup = BeautifulSoup(r.content, "html5lib")
table = soup.find("div", attrs={"class": "freestyle-content"})
for row in table.findAll("h2"):
    bakery.add(wnLem.lemmatize(row.text.lower()))

df = pd.DataFrame(list(bakery))
df.columns = ["bakery"]
df.to_csv("bakery.csv", index=None)


dairy = set()
# Dairy
r = requests.get(
    "https://www.godairyfree.org/dairy-free-grocery-shopping-guide/dairy-ingredient-list-2"
)
soup = BeautifulSoup(r.content, "html5lib")
table = soup.find("div", attrs={"class": "row cf"})
for row in table.findAll("li"):
    for s in row.select("em"):
        s.extract()
    # remove parentheses
    row = row.text.lower().split("(")
    dairy.add(wnLem.lemmatize(row[0].strip()))

df = pd.DataFrame(list(dairy))
df.columns = ["dairy"]
df.to_csv("dairy.csv", index=None)


grocery = set()
r = requests.get("https://www.outofmilk.com/ideas/easy-snack-ideas-party-pantry/")
soup = BeautifulSoup(r.content, "html5lib")
table = soup.find("div", attrs={"class": "list_area row"})
for row in table.findAll("li"):
    grocery.add(row.text.lower())

r = requests.get(
    "https://www.foodnetwork.com/recipes/packages/cooking-from-the-pantry/pantry-essentials-checklist"
)
soup = BeautifulSoup(r.content, "html5lib")
table = soup.find("div", attrs={"class": "articleBody parsys"})
for row in table.findAll("li"):
    item = row.text.lower()
    # print("row", row)
    if (
        "fruit" in item
        or "vegetables" in item
        or "bread" in item
        or "chicken" in item
        or "beef" in item
        or "egg" in item
    ):
        continue
    if "(" in item:
        item = item.split("(")[0]
    elif ":" in item:
        item = item.split(":")[0]
    elif " or " in item:
        item = item.split(" or ")[0]
    if ", " in item:
        items = item.split(", ")
        grocery.update(set([wnLem.lemmatize(word.strip()) for word in items]))
    else:
        grocery.add(wnLem.lemmatize(item.strip()))

grocery -= produce.union(deli, bakery, dairy)
df = pd.DataFrame(list(grocery))
df.columns = ["grocery"]
df.to_csv("grocery.csv", index=None)
