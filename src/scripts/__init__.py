import argparse
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

animals_url = "https://www.randomlists.com"
animals_download_folder = "images"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scripts for various things")
    parser.add_argument("--target", help="The target of the script", default="animals")
    args = parser.parse_args()

    if args.target == "animals":
        download_animals(150)

    return 0


def download_animals(amount: int):
    animals = list()

    # The page does some weird AJAX stuff on page load, the results are not actually rendered then, so we need to wait for the content to load in our target div
    driver = webdriver.Chrome()
    driver.get(
        "{}/random-animals?show_images=true&dup=false&qty={}".format(
            animals_url, amount
        )
    )

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.Rand-stage ol")))

    content = driver.page_source
    driver.quit()

    soup = BeautifulSoup(content, "html.parser")
    images_container = soup.find_all("div", class_="Rand-stage")
    if len(images_container) == 0:
        print("Images container not found!")
        return 1

    images = images_container[0].find_all("img")
    if len(images) == 0:
        print("Images not found!")
        return 1

    # create download folder if it doesn't exist
    if not os.path.exists(animals_download_folder):
        os.makedirs(animals_download_folder)

    for i in images:
        src = i["src"]
        filename = src.split("/")[-1]
        animal_name = filename.split(".")[0]
        animals.append(
            {
                "name": animal_name.replace("_", " "),
                "slugified_name": animal_name,
                "filename": filename,
            }
        )

        with open("{}/{}".format(animals_download_folder, filename), "wb") as f:
            f.write(requests.get(animals_url + src.replace(" ", "%20")).content)

    # write the image dictionary to a file as JSON
    with open("{}/animals.json".format(animals_download_folder), "w") as f:
        json.dump(animals, f)

    return 0
