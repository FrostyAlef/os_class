import requests
from bs4 import BeautifulSoup
import os
import json
import threading

PROXY = {
    'http': 'http://127.0.0.1:4392',
    'https': 'https:/127.0.0.1:443'
}
UNSPLASH_URL = "https://unsplash.com"
SAVE_DIR = "images"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def get_image_links():
    response = requests.get(UNSPLASH_URL, proxies=PROXY)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for img in soup.find_all('img', {'srcset': True}):
        links.append(img['src'])
    return links

def download_image(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

def save_metadata(image_id, photographer, category, save_path):
    metadata = {
        'image_id': image_id,
        'photographer': photographer,
        'category': category
    }
    with open(save_path, 'w') as file:
        json.dump(metadata, file, indent=4)

def download_and_save_image(link, idx):
    image_id = f'image_{idx}'
    save_path = os.path.join(SAVE_DIR, image_id + '.jpg')
    metadata_path = os.path.join(SAVE_DIR, image_id + '.json')

    download_image(link, save_path)
    save_metadata(image_id, "Unknown", "Uncategorized", metadata_path)

def get_tags(image_path):
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
    image_links = get_image_links()

    threads = []
    for idx, link in enumerate(image_links):
        thread = threading.Thread(target=download_and_save_image, args=(link, idx))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for filename in os.listdir(SAVE_DIR):
        if filename.endswith('.jpg'):
            image_path = os.path.join(SAVE_DIR, filename)
            tags = get_tags(image_path)
            print(f'Tags for {filename}: {tags}')

if __name__ == '__main__':
    main()
