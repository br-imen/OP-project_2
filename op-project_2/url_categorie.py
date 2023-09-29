import requests

url = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
r = requests.get(url)
response = r.text
print(response)
