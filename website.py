import requests
from bs4 import BeautifulSoup
import os
import json
import threading

PROXY = {
    'http': 'http://127.0.0.1:4392',
    'https': 'https:/127.0.0.1:443'
}
URL = "https://unsplash.com"

def get_links():
    response = requests.get(URL, proxies=PROXY)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for img in soup.find_all('img', {'srcset': True}):
        links.append(img['src'])
    return links

def download(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

def download_and_save_image(link, idx):
    image_id = f'image_{idx}'
    save_path = os.path.join("tasavir", image_id + '.jpg') # 'tasvir image_1.jpg' 
    metadata_path = os.path.join("tasavir", image_id + '.json')

    download(link, save_path)
    save_metadata(image_id, "Unknown", "Uncategorized", metadata_path)

def get_t(image_path):
    URL = "https://server.phototag.ai/api/keywords"
    HEADERS = {
        "Authorization": f'Bearer YOUR_API_KEY_HERE'
    }

    with open(image_path, 'rb') as image:
        payload = {
            "language": "en",
            "MacKeys": 4,
            "Keys": "",
            "cCON": ""
        }
        files = {'file': image}

        response = requests.post(URL, headers=HEADERS, data=payload, files=files)
        if response.status_code == 200:
            data = response.json()
            keywords = data.get('keywords')
            return keywords
        else:
            return []

def main():
    image_links = get_links()

    threads = []
    for idx, link in enumerate(image_links):
        thread = threading.Thread(target=download_and_save_image, args=(link, idx))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for filename in os.listdir("tasavir"):
        if filename.endswith('.jpg'):
            image_path = os.path.join("tasavir", filename)
            tags = get_tags(image_path)
            print(f'Tags for {filename}: {tags}')

if __name__ == '__main__':
    main()
