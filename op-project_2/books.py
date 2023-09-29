import requests
from bs4 import BeautifulSoup
import csv


def main():
    url_page = "https://books.toscrape.com/index.html"
    list_url_categories = get_url_categories(url_page)
    for category in list_url_categories:
        #print("category: ",category)
        data_books = []
        list_url_pages = get_url_pages(category)
        for page in list_url_pages:
            #print("page : ", page)
            urls_books = extract_url_books(page)
            for book in urls_books:
                #print("book : ", book)
                dict_book = extract_book(book)
                data_books.append(dict_book)
        category = data_books[0]["category"]
        load_book(data_books,category)



# Get a list of url all categories:
def get_url_categories(url_page):
    url_categories = []
    r = requests.get(url_page)
    if r:
        response = r.text
        soup = BeautifulSoup(response,"html.parser")
        parent = soup.find("ul",{"class" : "nav nav-list"}).find("ul").find_all("a")
        for child in parent:
            href = "https://books.toscrape.com/" + child["href"]
            url_categories.append(href)
        
    return url_categories



# Get a list of urls all pages, loop over the list of urls pages to get books of every page:
def get_url_pages(url):
    list_url_pages = [url]
    while True:
        r = requests.get(url)
        if r:
            response = r.text
            soup = BeautifulSoup(response,"html.parser")
            try:
                next = soup.find("li", {"class" : "next"}).find("a")["href"]
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
        try: 
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
            dict_book["product_description"] = product_description

            # Url image
            image = soup.find("img")["src"]
            dict_book["image_url"] = image 

            # Star rating
            rating = soup.find("p", {"class": "instock availability"}).find_next("p")[
                "class"
            ]
            star = rating[1].lower()
            numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
            dict_book["review_rating"] = numbers[star]

            # Category
            category = soup.find("li").find_next("li").find_next("li").text.strip()
            dict_book["category"] = category

        except AttributeError as e:
            print(e)

    return dict_book


# Load data of one product in one file.csv:
def load_book(list,category):
    with open(f"{category}.csv", "w", newline="") as csvfile:
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
