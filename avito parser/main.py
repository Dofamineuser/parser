import requests
import base64
import time
from bs4 import BeautifulSoup


headers = {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
           "accept": "text/html,application/xhtml+xml,app"}

url = "https://irr.ru/real-estate/rent/"
main_html = "main.html"


def test_request(url, retry=5):
    """send reques use requests return responce"""
    try:
        time.sleep(0.5)
        response = requests.get(url, headers=headers)
    except Exception:
        if retry:
            time.sleep(3)
            print(f"[INFO] retry={retry} => {url}")
            return test_request(url, retry=(retry - 1))
        else:
            raise
    else:
        return response


def _make_soup(response):
    """give response return data frame"""
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


# Возвращает все карточки с ссылками из страницы (Из рук в руки)
def _find_desired_cards(soup):
    """give category page data frame return tags contain hrefs"""
    desired_section = soup.find('div', {'class': 'js-listingContainer'})
    desired_cards = desired_section.find_all("div", {"class": "listing__itemTitleWrapper"})
    return desired_cards


# возвращает ссылки из набора дивов
def _get_hrefs(divs):
    """give desired_cards data frame return list links from items"""
    hrefs = []
    for div in divs:
        a = div.find("a", {'class': 'listing__itemTitle'}, href=True)
        hrefs.append(a["href"])
    return hrefs


# return int pagination pages
def _get_pagination_pages(category_link):
    """return count of pagination pages from category link"""
    pagination_pages = category_link.find("div", {"class": "pagination__pages"})
    try:
        a_count_pages = pagination_pages.find_all("a")
        count = a_count_pages[-1].text
        return int(count)
    except AttributeError:
        pass


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
    """give dataframe write html file by filename in current directory"""
    with open(f"{filename}", 'w', encoding="utf-8") as file:
        file.write(str(soup.prettify()))  # prettifies the HTML with proper indents and everything.


# write txt file by strings
def _write_txt(filename, iterable_object):
    """give list write txt file by strings in list"""
    try:
        with open(f"{filename}", "a", encoding="utf-8") as file:
            file.write(f"{iterable_object}\n")
    except TypeError:
        pass


# rewrite html file name = main.html
def _main_writer(url, filename):
    """create html file (filename.html) on main directory"""
    response = test_request(url)
    soup = _make_soup(response)
    _write_html(soup, filename)

    """Decoding functions pool"""


def _get_encrypted_value(page):
    """give desired page dataframe return encrypted phone number"""
    try:
        tag = page.find("input", {"name": "phoneBase64"})
        return tag["value"]
    except TypeError:
        print("number not found")
        pass


def _decoding_string(encrypted_string):
    """give encrypted phone number return decoded number"""
    try:
        base64_bytes = encrypted_string.encode("utf-8")
        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string = sample_string_bytes.decode("utf-8")
        return sample_string.replace(" ", "")
    except AttributeError:
        pass


# return phone numbers list from matherpage
def category_page(mather_url):
    """give category correct link return phone numbers list"""
    request = test_request(mather_url)
    soup = _make_soup(request)
    desired_cards = _find_desired_cards(soup)
    hrefs_from_page = _get_hrefs(desired_cards)
    phone_numbers = _desired_page_work(hrefs_from_page)
    return phone_numbers


# делает всю работу начиная с страницы категории
def _mainpage_worker(url, category, city):
    request = test_request(url)
    soup = BeautifulSoup(request.text)
    count_paginations = _get_pagination_pages(soup)
    if count_paginations:
        print(f"in {url} contain {count_paginations} pages")
        link = url
        phone_numbers = category_page(link)
        if category in nonwritting_categories:
            category = "final"
        for phone_number in phone_numbers:
            _write_txt(f"{city}{category}.txt", phone_number)
        for i in range(count_paginations - 1):
            link = f"{url}/page{i + 2}"
            phone_numbers = category_page(link)
            if category in nonwritting_categories:
                category = "final"
            for phone_number in phone_numbers:
                _write_txt(f"{city}{category}.txt", phone_number)

    else:
        phone_numbers = category_page(url)
        if category in nonwritting_categories:
            category = "final"
        for phone_number in phone_numbers:
            _write_txt(f"{city}{category}.txt", phone_number)


# return decoded phones list from desired(final item)  page
def _desired_page_work(list_hrefs):
    decoded_phones = []
    try:
        print("i am in desired page")
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
    except KeyboardInterrupt:
        for phone in decoded_phones:
            _write_txt(f"interupt.txt", phone)


categories =[
    "personal",
    "hobbies",
    "animals-plants",
    "otdam-darom",
    "jobs-education",
    "rapport",
    "real-estate/rent",
    "electronics-technics/kitchen",
    "business",
    "electronics-technics",
    "home",
]

cityes = [
    "krasnodar",
    "vladivostok",
    "yaroslavl"

]

nonwritting_categories = ["electronics-technics/kitchen", "jobs-education", "real-estate/rent"]


def _main():
    pass


def _test():
    city = "yaroslavl"

    for category in categories:
        main_link = f"https://{city}.irr.ru/{category}"
        print(main_link)
        _mainpage_worker(main_link, category, city)


if __name__ == "__main__":
    _test()