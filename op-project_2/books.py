import requests
from bs4 import BeautifulSoup
import csv


def main():
    url_categorie = (
        "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
    )
    data_books = []
    list_url_pages = get_url_pages(url_categorie)
    for page in list_url_pages:
        urls_books = extract_url_books(page)
        for url in urls_books:
            dict_book = extract_book(url)
            data_books.append(dict_book)
    load_book(data_books)

# Get a list of url all pagees, loop over the list of urls pages to get books of every page:
def get_url_pages(url):
    list_url_pages = [url]
    while True:
        r = requests.get(url)
        if r:
            response = r.text
            soup = BeautifulSoup(response,"html.parser")
            next = soup.find("li",{"class" : "next"}).find_next("a")["href"]
            if next:
                url_next_page = url.rsplit("/", 1)
                url_next_page = url_next_page[0] + "/" + next
                print(url_next_page)
                list_url_pages.append(url_next_page) 
                url = url_next_page
                pass
            break
    return list_url_pages
                


# Get a list of Url products of one page:
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


# 1 Extraction of data of one product, all data of one book in dict
def extract_book(url_book):
    r = requests.get(url_book)
    if r:
        response = r.text
        soup = BeautifulSoup(response, "html.parser")
        dict_book = {}

        # Url
        dict_book["product_page_url"] = url_book 

        # title
        dict_book["title"] = soup.h1.string.strip() 

        # Upc
        upc = soup.table.find("th", string="UPC").find_next_sibling("td").string
        dict_book["universal_product_code(upc)"] = upc

        # Price including tax
        price_include_tax = (
            soup.table.find("th", string="Price (incl. tax)")
            .find_next_sibling("td")
            .string
        )
        dict_book["price_including_tax"] = price_include_tax

        # Price excluding tax
        price_exclude_tax = (
            soup.table.find("th", string="Price (excl. tax)")
            .find_next_sibling("td")
            .string
        )
        dict_book["price_excluding_tax"] = price_exclude_tax

        # Number available
        availabity = (
            soup.table.find("th", string="Availability").find_next_sibling("td").string
        )
        number_availability = ""
        for char in availabity:
            if char.isdigit():
                number_availability += char
        dict_book["number_available"] = int(number_availability)

        # Description
        product_description = (
            soup.find("div", {"id": "product_description"})
            .find_next_sibling("p")
            .string
        )
        dict_book["product_description"] = '"' + product_description + '"'

        # Url image
        image = soup.find("img")["src"]
        dict_book["image_url"] = '"' + image + '"'

        # Star rating
        rating = soup.find("p", {"class": "instock availability"}).find_next("p")[
            "class"
        ]
        star = rating[1].lower()
        numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        dict_book["review_rating"] = numbers[star]

        # Category
        category = soup.find("li").find_next("li").find_next("li").text.strip()
        dict_book["category"] = '"' + category + '"'

    return dict_book


# 2 Loading data of one product in one file.csv
def load_book(list):
    with open("category_allpage.csv", "w", newline="") as csvfile:
        fieldnames = []
        for key in list[0]:
            fieldnames.append(key)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for element in list:
            writer.writerow(element)

    return


if __name__ == "__main__":
    main()
