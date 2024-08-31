import requests
from bs4 import BeautifulSoup

def get_banana_prices():
    url = "https://www.walmart.com/search?q=bananas"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    prices = []
    for item in soup.find_all("div", class_="search-result-gridview-item-wrapper"):
        price = item.find("span", class_="price-characteristic")
        if price:
            prices.append(price.text)

    return prices

banana_prices = get_banana_prices()
for price in banana_prices:
    print(f"Banana price: ${price}")
