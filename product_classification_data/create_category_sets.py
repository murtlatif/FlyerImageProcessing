import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.stem import *
import os

# nltk.download("wordnet")
wnLem = WordNetLemmatizer()


def create_produce(seperate_fruit_veggie=False):
    """
    Create a csv of produce items.

    Args:
        seperate_fruit_veggie: If set to true, fruits and vegetables will have a seperate
                               csv (needed for baseline), instead of being combined
    """
    # Produce
    produce = set()
    for i, url in enumerate(["fruits-a-z/", "veggies-a-z/"]):
        r = requests.get(f"https://www.halfyourplate.ca/fruits-and-veggies/{url}")
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
        if seperate_fruit_veggie:
            if i == 0:
                df = pd.DataFrame(sorted(list(produce)))
                df.columns = ["fruit"]
                df.to_csv("fruit.csv", index=None)
            elif i == 1:
                df = pd.DataFrame(sorted(list(produce)))
                df.columns = ["vegetable"]
                df.to_csv("vegetable.csv", index=None)
            produce = set()

    if not seperate_fruit_veggie:
        df = pd.DataFrame(sorted(list(produce)))
        df.columns = ["produce"]
        df.to_csv("produce.csv", index=None)


def create_meat():
    """
    Create a csv of meat items.
    """
    # Meat
    meat = set()
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
        meat.update(set(items))

    df = pd.DataFrame(sorted(list(meat)))
    df.columns = ["meat"]
    df.to_csv("meat.csv", index=None)


def create_bakery():
    """
    Create a csv of bakery items.
    """
    # Bakery
    bakery = set()
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

    bakery.update(
        set(pd.read_csv("suppliment/bakery_suppliment.csv").to_numpy().flatten())
    )

    df = pd.DataFrame(sorted(list(bakery)))
    df.columns = ["bakery"]
    df.to_csv("bakery.csv", index=None)


def create_dairy():
    """
    Create a csv of dairy items.
    """
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
                dairy.add(wnLem.lemmatize(item))

    df = pd.DataFrame(sorted(list(dairy)))
    df.columns = ["dairy"]
    df.to_csv("dairy.csv", index=None)


def create_household():
    """
    Create a csv of household items.
    """
    household = set()
    # household
    r = requests.get(
        "https://www.outofmilk.com/ideas/household-essentials-shopping-list/"
    )
    soup = BeautifulSoup(r.content, "html5lib")
    table = soup.find(
        "div", attrs={"class": "intro_text sectionWrap small-12 medium-12 columns"}
    )
    for row in table.findAll("li"):
        household.add(wnLem.lemmatize(row.text.lower().strip()))

    table = soup.find(
        "div", attrs={"class": "shopping_list sectionWrap small-12 medium-12 columns"}
    )
    for row in table.findAll("li"):
        household.add(wnLem.lemmatize(row.text.lower().strip()))

    r = requests.get(
        "https://updater.com/moving-tips/the-ultimate-new-home-grocery-shopping-list"
    )
    soup = BeautifulSoup(r.content, "html5lib")
    table = soup.find("ul", attrs={"class": "squares"})
    for rows in table:
        household.add(wnLem.lemmatize(rows.text.lower()))

    household.update(
        set(pd.read_csv("suppliment/household_suppliment.csv").to_numpy().flatten())
    )

    df = pd.DataFrame(sorted(list(household)))
    print("df", df)
    df.columns = ["household"]
    df.to_csv("household.csv", index=None)


def create_grocery():
    """
    Create a csv of grocery items. It will substract the sets of the other categories
    to ensure there's no overlap.
    """
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

    listdir = set(os.listdir())
    if "produce.csv" not in listdir:
        create_produce()
    elif "meat.csv" not in listdir:
        create_meat()
    elif "bakery.csv" not in listdir:
        create_bakery()
    elif "dairy.csv" not in listdir:
        create_dairy()

    bakery = set(pd.read_csv("bakery.csv").to_numpy().flatten())
    dairy = set(pd.read_csv("dairy.csv").to_numpy().flatten())
    meat = set(pd.read_csv("meat.csv").to_numpy().flatten())
    produce = set(pd.read_csv("produce.csv").to_numpy().flatten())

    grocery -= produce.union(meat, bakery, dairy)
    df = pd.DataFrame(sorted(list(grocery)))
    df.columns = ["grocery"]
    df.to_csv("grocery.csv", index=None)


if __name__ == "__main__":
    create_produce(seperate_fruit_veggie=False)
    create_meat()
    create_bakery()
    create_dairy()
    create_household()
    create_grocery()
