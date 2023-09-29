import requests

url = "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html"
r = requests.get(url)
response = r.text
print(response)
