from bs4 import BeautifulSoup
import url_config as cfg
import fake_useragent
import multiprocessing
import requests
import json
import csv


def download_items_links() -> None:
    """
    Get all links and put them in json file
    """

    url = cfg.download_url

    all_links_ = list()
    for page_number in range(1, 10):
        headers = {
            'User-Agent': fake_useragent.UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }

        src = requests.get(f'{url}/?PAGEN_1={page_number}', headers=headers).text
        soup = BeautifulSoup(src, 'lxml')

        all_href = [f'{cfg.base_url}{a.get("href")}' for a in soup.find_all('a', class_='catalog-item-link')]
        all_links_ += all_href

    with open('all_links.json', 'w') as file:
        json.dump(all_links_, file, indent=4, ensure_ascii=False)


def handler(link: str) -> None:
    """
    Get information about product and put it in csv file
    """

    headers = {
        'User-Agent': fake_useragent.UserAgent().random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }

    src = requests.get(link, headers=headers).text
    soup = BeautifulSoup(src, 'lxml')

    article = soup.find('div', class_='product-article').text.replace('арт. ', '')
    name = soup.find('div', class_='product-description').text
    price = soup.find('span', class_='product-price-current').text.replace('\xa0', ' ')
    photo_links = [f'{cfg.base_url}{image.get("src")}' for image in
                   soup.find('div', class_='product-photos').find_all('img')]
    qualities = [article, name, price, " | ".join(photo_links)]

    with open('all_products.csv', 'a', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL, quotechar='!')
        writer.writerow(qualities)


if __name__ == "__main__":
    download_items_links()

    with open('all_links.json', encoding='utf-8-sig') as file:
        all_links = json.load(file)

    with open('all_products.csv', 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Артикул', 'Название', 'Цена', 'Ссылки на фото'])

    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        pool.map(handler, all_links)
