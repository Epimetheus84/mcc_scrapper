# coding: utf-8
import requests
import csv

from lxml import etree
from json import dump, loads, JSONEncoder, JSONDecoder
from bs4 import BeautifulSoup

# скрипт заточен только под этот url!
RUSSIAN_MCC_URL = 'https://mcc-codes.ru/code/'  # в конце должен быть слеш
OUTPUT_CSV_FILE = 'out.csv'

MINIMAL_MCC = 4000
MAXIMUM_MCC = 10000


def save_to_csv(data):
    keys = data[0].keys()

    with open(OUTPUT_CSV_FILE, 'w', encoding='utf-8-sig', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def parse_title(title_with_html):
    title_with_html = etree.tostring(title_with_html[0], encoding='unicode')
    title_delimiter = '</span>'
    title_first_index = title_with_html.find(title_delimiter) + len(title_delimiter)
    title = title_with_html[title_first_index:]
    h_end_tag = len('</h1>') + 1
    title = title[:-h_end_tag]
    return title.lstrip()


def parse_subtitle(english_subtitle_soup_block):
    return english_subtitle_soup_block[0].text.lstrip()


def parse_content(description_soup_block):
    description_with_html = etree.tostring(description_soup_block[0], encoding='unicode')
    open_tag = '<p class="mb-3"><b>Описание:</b>'
    close_tag = '</p>'
    description_with_html = description_with_html[len(open_tag):]
    description_with_html = description_with_html[:-(len(close_tag) + 1)]
    return description_with_html.lstrip()


def parse_group(group_soup_block):
    group_with_html = etree.tostring(group_soup_block[0], encoding='unicode')
    open_tag = '<p><b>Группа:</b>'
    close_tag = '</p>'
    group_with_html = group_with_html[len(open_tag):]
    group_with_html = group_with_html[:-(len(close_tag) + 1)]
    return group_with_html.lstrip()


# получаем данные об mcc коде
def parse_page(soup):
    dom = etree.HTML(str(soup))
    title_soup_block = dom.xpath('/html/body/section/div[1]/div[1]/h1')
    title_soup_block_content = parse_title(title_soup_block)

    english_subtitle_soup_block = dom.xpath('/html/body/section/div[1]/div[1]/div[1]')
    english_subtitle_soup_block_content = parse_subtitle(english_subtitle_soup_block)

    description_soup_block = dom.xpath('/html/body/section/div[2]/div[1]/div[1]/p[1]')
    description_soup_block_content = parse_content(description_soup_block)

    group_soup_block = dom.xpath('/html/body/section/div[2]/div[1]/div[1]/p[2]')
    group_soup_block_content = parse_group(group_soup_block)

    page_data = {
        'title': title_soup_block_content,
        'english_subtitle': english_subtitle_soup_block_content,
        'description': description_soup_block_content,
        'group': group_soup_block_content
    }

    return page_data


if __name__ == '__main__':
    # циклом проходимся по всем возможным MCC,
    # закладываем диапозон от 1000-ого до 10000-ого
    # (по факту их меньше и диапозон на момент 2022 - от 4814 до 9950, но лучше заложимся на будущее)
    mcc_data = []
    for mcc in range(MINIMAL_MCC, MAXIMUM_MCC):
        print(mcc)
        page = requests.get(RUSSIAN_MCC_URL + str(mcc))

        # если такого mcc не существует, не парсим о нем данные
        if page.status_code != 200:
            continue

        page_soup = BeautifulSoup(page.content, "html.parser")
        page_data = parse_page(page_soup)
        page_data['mcc'] = mcc
        mcc_data.append(page_data)

    print(mcc_data)
    save_to_csv(mcc_data)
