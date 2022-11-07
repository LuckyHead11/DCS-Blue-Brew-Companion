import os
import shutil
def get_item_image(name, company):
    try:
        query = f"A photograph of {company} {name}"
        """Search a query on google"""
        import requests
        from bs4 import BeautifulSoup

        url = "https://www.google.com/search?q=" + query + "&source=lnms&tbm=isch"
        headers = {"user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        images = soup.find_all("img", class_="rg_i")
        count = 0

        os.mkdir("static/" + name)
        for image in images:
            
            
            image_url = image.get("data-src")
            if image_url is not None:
                count += 1
                r = requests.get(image_url)

                with open(f"static/{name}/{count}.png", "wb") as f:
                    f.write(r.content)

                if count >= 5:
                    break

        #Pick a random image from the folder and only save that image
        import random

        random_image = random.choice(os.listdir(f"static/{name}"))
        os.rename(f"static/{name}/{random_image}", f"static/{name}/choose.png")
        
    except:
        pass

