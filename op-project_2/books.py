import requests
from bs4 import BeautifulSoup
import csv
import urllib.request
import pathlib
import ssl


def main():
    url_page = "https://books.toscrape.com/index.html"
    list_url_categories = get_url_categories(url_page)
    for url_category in list_url_categories:
        data_books = []
        list_url_pages = get_url_pages(url_category)
        for page in list_url_pages:
            urls_books = extract_url_books(page)
            for url_book in urls_books:
                dict_book = extract_book(url_book)
                data_books.append(dict_book)
        category = data_books[0]["category"]
        load_book(data_books, category)


# Get a list of url all categories:
def get_url_categories(url_page):
    url_categories = []
    r = requests.get(url_page)
    if r:
        response = r.text
        soup = BeautifulSoup(response, "html.parser")
        parent = soup.find("ul", {"class": "nav nav-list"}).find("ul").find_all("a")
        for child in parent:
            href = "https://books.toscrape.com/" + child["href"]
            url_categories.append(href)

    return url_categories


# Get a list of urls all pages:
def get_url_pages(url):
    list_url_pages = [url]
    while True:
        r = requests.get(url)
        if r:
            response = r.text
            soup = BeautifulSoup(response, "html.parser")
            try:
                next = soup.find("li", {"class": "next"}).find("a")["href"]
                url_next_splited_page = url.rsplit("/", 1)
                url_next_page = url_next_splited_page[0] + "/" + next
                list_url_pages.append(url_next_page)
                url = url_next_page
                pass
            except AttributeError:
                break
    return list_url_pages


# Get a list of urls products of one page:
def extract_url_books(url):
    r = requests.get(url)
    list_books = []
    if r:
        response = r.text
        soup = BeautifulSoup(response, "html.parser")
        products = soup.find_all("div", attrs={"class": "image_container"})
        for div in products:
            href = div.find("a")["href"]
            new_href = href.replace("../../..", "https://books.toscrape.com/catalogue")
            list_books.append(new_href)
    return list_books


# Scrap one product, all data of one book in dict
def extract_book(url_book):
    r = requests.get(url_book)
    if r:
        response = r.text
        soup = BeautifulSoup(response, "html.parser")
        dict_book = {}

        # Url
        dict_book["product_page_url"] = url_book

        # title
        try:
            dict_book["title"] = soup.h1.string.strip()
        except AttributeError as e:
            print(e)
            dict_book["title"] = ""

        # Upc
        try:
            upc = soup.table.find("th", string="UPC").find_next_sibling("td").string
            dict_book["universal_product_code(upc)"] = upc
        except AttributeError as e:
            print(e)
            dict_book["universal_product_code(upc)"] = ""

        # Price including tax
        try:
            price_include_tax = (
                soup.table.find("th", string="Price (incl. tax)")
                .find_next_sibling("td")
                .string
            )
            dict_book["price_including_tax"] = price_include_tax
        except AttributeError as e:
            print(e)
            dict_book["price_including_tax"] = ""

        # Price excluding tax
        try:
            price_exclude_tax = (
                soup.table.find("th", string="Price (excl. tax)")
                .find_next_sibling("td")
                .string
            )
            dict_book["price_excluding_tax"] = price_exclude_tax
        except AttributeError as e:
            print(e)
            dict_book["price_excluding_tax"] = ""

        # Number available
        try:
            availabity = (
                soup.table.find("th", string="Availability")
                .find_next_sibling("td")
                .string
            )
            number_availability = ""
            for char in availabity:
                if char.isdigit():
                    number_availability += char
            dict_book["number_available"] = int(number_availability)
        except AttributeError as e:
            print(e)
            dict_book["number_available"] = ""

        # Description
        try:
            product_description = (
                soup.find("div", {"id": "product_description"})
                .find_next_sibling("p")
                .string
            )
            dict_book["product_description"] = product_description
        except AttributeError as e:
            print(e)
            dict_book["product_description"] = ""

        # Url image
        try:
            image = soup.find("img")["src"]
            dict_book["image_url"] = image
        except AttributeError as e:
            print(e)
            dict_book["image_url"] = ""

        # Star rating
        try:
            rating = soup.find("p", {"class": "instock availability"}).find_next("p")[
                "class"
            ]
            star = rating[1].lower()
            numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
            dict_book["review_rating"] = numbers[star]
        except AttributeError as e:
            print(e)
            dict_book["review_rating"] = ""

        # Category
        try:
            category = soup.find("li").find_next("li").find_next("li").text.strip()
            dict_book["category"] = category
        except AttributeError as e:
            print(e)
            dict_book["category"] = ""

    return dict_book


# Load data of one product in one file.csv:
def load_book(list, category):
    with open(
        f"/Users/joy/code/op-project_2/media/csv/{category}.csv", "w", newline=""
    ) as csvfile:
        fieldnames = []
        for key in list[0]:
            fieldnames.append(key)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for element in list:
            writer.writerow(element)
            url_image = element["image_url"].replace(
                "../..", "https://books.toscrape.com"
            )
            url_book = element["product_page_url"].rsplit("/", 2)
            name_book = url_book[1]
            image_extension = pathlib.Path(url_image).suffix
            ssl._create_default_https_context = ssl._create_unverified_context
            try:
                urllib.request.urlretrieve(
                    url_image,
                    f"/Users/joy/code/op-project_2/media/image/{category}_{name_book}{image_extension}",
                )
            except ValueError as e:
                print(e, name_book)

    return


if __name__ == "__main__":
    main()
