import requests
from bs4 import BeautifulSoup
import time


class SamsScraper:
    def __init__(self):
        pass

    def run_test(self):
        times = []
        for i in range(0, 10):
            start_time = time.time()
            info = self.full_scrape("Chip Pack Doritos")
            print(f"Started scraping... + {i + 1}/10")
            for res in info:
                print(res)
            end_time = time.time()
            times.append(end_time - start_time)
        return sum(times) / len(times)

    def download_image(self, url, filename):
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Image successfully downloaded: {filename}")
        else:
            print("Failed to retrieve the image")

    def get_certain_order(self, item_name, specific_order, download_image_check=False):
        responses = []
        url = f"https://www.samsclub.com/s/{item_name}"
        print("Starting...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        div = soup.find("div", {"class": "sc-infinite-loader undefined"})
        # Then find the ul
        ul = div.find("ul")
        # Get all the li's
        lis = ul.findAll("li")

        if len(lis) == 0:
            print("No results")
            return ["No results", 0.00]


        new_div = lis[specific_order].find("div", {"class": "sc-pc-title-medium title-medium-desktop-canary"})
        # Title
        h3 = new_div.find("h3")
        title = h3.text

        # Price
        try:
            div = lis[specific_order].find("div", {"class": "sc-pc-medium-desktop-moneybox"})

            span = div.find("span", {"class": "sc-price"})
            price = span.find("span", {"class": "visuallyhidden"}).text.replace("current price: ", "")
        except Exception as e:
            print(f"Error: {e.with_traceback(e.__traceback__)}")
            text = lis[specific_order].text
            if "$0.00" in text:
                price = "$0.00"

        # Image
        div = lis[specific_order].find("div", {"class": "sc-pc-image sc-pc-medium-desktop-card-canary-image-canary"})
        img = div.find("img")
        # Get the src
        src = img.get("src")
        new_title = title.replace(" ", "").replace('.', '').replace("\"", '').replace("\\",'').replace('/','').replace(",","")

        if download_image_check: self.download_image(src, "static/images/groceries/" + new_title + ".png")

        return [title, price.replace("$", "").replace(",", "")]

    def full_scrape(self, item_name, download_image_check=False):
        responses = []
        url = f"https://www.samsclub.com/s/{item_name}"
        print("Starting...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        div = soup.find("div", {"class": "sc-infinite-loader undefined"})
        # Then find the ul
        ul = div.find("ul")
        # Get all the li's
        lis = ul.findAll("li")

        if len(lis) == 0:
            print("No results")
            return ["No results", 0.00]
        num = 0
        for li in lis:
            num += 1
            print(num)
            new_div = li.find("div", {"class": "sc-pc-title-medium title-medium-desktop-canary"})
            # Title
            h3 = new_div.find("h3")
            title = h3.text

            # Price
            try:
                div = li.find("div", {"class": "sc-pc-medium-desktop-moneybox"})

                span = div.find("span", {"class": "sc-price"})
                price = span.find("span", {"class": "visuallyhidden"}).text.replace("current price: ", "")
            except Exception as e:
                print(f"Error: {e.with_traceback(e.__traceback__)}")
                text = li.text
                if "$0.00" in text:
                    price = "$0.00"

            # Image
            div = li.find("div", {"class": "sc-pc-image sc-pc-medium-desktop-card-canary-image-canary"})
            img = div.find("img")
            # Get the src
            src = img.get("src")
            new_title = title.replace(" ", "").replace('.', '').replace("\"", '').replace("\\",'').replace('/','')
            print(new_title)
            if download_image_check: self.download_image(src, "static/images/groceries/" + new_title + ".png")

            responses += [f"{num}. {title} {price}"]

            if num == 15:
                break
        return responses
