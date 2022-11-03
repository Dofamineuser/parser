import requests
import base64
import time
from bs4 import BeautifulSoup


headers = {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
           "accept": "text/html,application/xhtml+xml,app"}

url = "https://irr.ru/real-estate/rent/"
main_html = "main.html"


def _get_html(url):
    response = requests.get(url, headers=headers)
    return response


def test_request(url, retry=5):
    try:
        time.sleep(0.5)
        response = requests.get(url, headers=headers)
    except Exception as ex:
        if retry:
            time.sleep(3)
            print(f"[INFO] retry={retry} => {url}")
            return test_request(url, retry=(retry - 1))
        else:
            raise
    else:
        return response


def _make_soup(response):
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


# Возвращает все карточки с ссылками из страницы (Из рук в руки)
def _find_desired_cards(soup):
    desired_section = soup.find('div', {'class': 'js-listingContainer'})
    desired_cards = desired_section.find_all("div", {"class": "listing__itemTitleWrapper"})
    return desired_cards


# возвращает ссылки из набора дивов
def _get_hrefs(divs):
    hrefs = []
    for div in divs:
        a = div.find("a", {'class': 'listing__itemTitle'}, href=True)
        hrefs.append(a["href"])
    return hrefs


# return int pagination pages
def _get_pagination_pages(soup):
    pagination_pages = soup.find("div", {"class": "pagination__pages"})
    try:
        a_count_pages = pagination_pages.find_all("a")
        count = a_count_pages[-1].text
        return int(count)
    except AttributeError:
        pass


# appending hrefs.txt file
def _append_hrefs():
    count_of_pages = 0
    soup = _open_makesoupe(main_html)
    count_of_pages += _get_pagination_pages(soup)
    for i in range(count_of_pages):
        link = f'https://irr.ru/real-estate/rent/page{i+2}/'
        soup = _make_soup(_get_html(link))
        print(f'make soup page{i+2}')
        desired_cards = _find_desired_cards(soup)
        print("carsd find...")
        hrefs = _get_hrefs(desired_cards)
        with open("hrefs.txt", "a", encoding="utf-8") as file:
            for href in hrefs:
                file.write(f"{href}\n")
                print(f"write___ {href}")


"""Open functions pool"""


def _open_html(html):
    with open(html, 'r') as file:
        html = file.read()
        return html


def _open_makesoupe(path):
    soup = BeautifulSoup(open(path, encoding="utf8"), "html.parser")
    return soup


# return open txt file
def _open_txt(path):
    hrefs = []
    with open(path, "r", encoding="utf-8") as file:
        for i in file:
            hrefs.append(i)
        return hrefs


"""Writing functions pool"""


def _write_html(soup, filename):
    with open(f"{filename}", 'w', encoding="utf-8") as file:
        file.write(str(soup.prettify()))


def _write_new_page(url, filename):
    response = _get_html(url)
    soup = _make_soup(response)
    _write_html(soup, filename)


# write txt file by strings
def _write_txt(filename, iterable_object):
    try:
        with open(f"{filename}", "a", encoding="utf-8") as file:
            file.write(f"{iterable_object}\n")
    except TypeError:
        pass


# rewrite html file name = main.html
def _main_writer():
    html = _get_html(url)
    soup = _make_soup(html)
    _write_html(soup)

    """Decoding functions pool"""


# return encrypted phone number
def _get_encrypted_value(page):
    try:
        tag = page.find("input", {"name": "phoneBase64"})
        return tag["value"]
    except TypeError:
        print("number not found")
        pass


# return encoding value
def _decoding_string(encrypted_string):
    try:
        base64_bytes = encrypted_string.encode("utf-8")
        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string = sample_string_bytes.decode("utf-8")
        return sample_string.replace(" ", "")
    except AttributeError:
        pass


# return hrefs from mainpages
def _mainpage_worker(url):
    hrefs = []
    request = test_request(url)
    soup = BeautifulSoup(request.text)
    count_paginations = _get_pagination_pages(soup)
    if count_paginations:
        print(count_paginations)
        link = url
        request = test_request(link)
        soup = _make_soup(request)
        desired_cards = _find_desired_cards(soup)
        hrefs_from_page = _get_hrefs(desired_cards)
        for href in hrefs_from_page:
            hrefs.append(href)
        for i in range(count_paginations - 1):
            link = f"{url}/page{i + 2}"
            request = test_request(link)
            soup = _make_soup(request)
            desired_cards = _find_desired_cards(soup)
            hrefs_from_page = _get_hrefs(desired_cards)
            for i in hrefs_from_page:
                hrefs.append(i)

    else:
        link = url
        request = test_request(link)
        soup = _make_soup(request)
        desired_cards = _find_desired_cards(soup)
        hrefs_from_page = _get_hrefs(desired_cards)
        for href in hrefs_from_page:
            hrefs.append(href)
    print(f"получил {len(hrefs)} ссылок")
    return hrefs


# return decoded phon from desired page
def _desired_page_work(list_hrefs):
    decoded_phones = []
    for href in list_hrefs:
        request = test_request(href.strip())
        soup = BeautifulSoup(request.text)
        print(f"{soup.title.text}")
        encrypted_value = _get_encrypted_value(soup)
        if encrypted_value:
            decoding_string = _decoding_string(encrypted_value)
            decoded_phones.append(decoding_string)
            print(decoding_string)
    return decoded_phones


categories =[
    "electronics-technics",
    "personal",
    "home",
    "hobbies",
    "animals-plants",
    "otdam-darom",
    "jobs-education",
    "rapport",
    "real-estate/rent",
    "electronics-technics/kitchen",
    "business"
]

nonwritting_categories = ["electronics-technics/kitchen", "jobs-education", "real-estate/rent"]


def _main():
    city = "chelyabinsk"

    for category in categories:
        desired_links = _mainpage_worker(f"https://{city}.irr.ru/{category}")
        phone_numbers = _desired_page_work(desired_links)
        if category in nonwritting_categories:
            category = "final"
        for phone_number in phone_numbers:
            _write_txt(f"{city}{category}.txt", phone_number)


def _test():
    request = test_request("https://msk.kupiprodai.ru/auto/moscow_gruzoviki_filtr_7340268")
    soup = _make_soup(request)
    _write_html(soup, "cars.html")


if __name__ == "__main__":
    _main()