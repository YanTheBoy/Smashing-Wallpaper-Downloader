import requests
from bs4 import BeautifulSoup
import os
import urllib.request
import argparse
import re
import sys


def parse_args():
    command_line_parser = argparse.ArgumentParser()
    command_line_parser.add_argument(
        'date',
        type=str,
        help='Upload date of needed wallpaper pack (Example of correct date format: july-2015)'
    )
    command_line_parser.add_argument(
        'size',
        type=str,
        help='Image size, which you want to download (Example of correct size format: 100x100)'
    )
    return command_line_parser


def get_response(link):
    page = 2
    response = requests.get(link)
    yield response
    while response.ok:
        response = requests.get(link + 'page/{}'.format(page))
        if not response.ok:
            return None
        page += 1
        yield response


def find_all_wallpapers_packs(responses):
    for response in responses:
        soup = BeautifulSoup(response.content, 'lxml')
        pages_packs = soup.select('article > h1 > a')
        yield from pages_packs


def create_dataset_with_names_and_links(list_of_packs):
    main_page = 'https://www.smashingmagazine.com'
    data_set = set()
    for pack_link in list_of_packs:
        data_set.add(main_page+pack_link.attrs['href'])
    return data_set


def find_needed_pack_by_date(database, date):
    for page_url in database:
        if date in page_url:
            return page_url


def get_all_wallpapers_urls_from_pack(pack_url):
    response = get_response_from_wallpaper_pack_url(pack_url)
    soup = BeautifulSoup(response.content, 'lxml')
    all_li_elements = soup.find_all('li')
    for link in all_li_elements:
        if link.find(text=re.compile("without")):
            yield from link.find_all('a')


def get_response_from_wallpaper_pack_url(wp_pack_url):
    return requests.get(wp_pack_url)


def get_needed_size_wallpapers(tag_format_list_with_hrefs, size):
    for tag in tag_format_list_with_hrefs:
        if size in tag.attrs['href']:
            yield tag.attrs['href']


def download_wallpapers(list_of_urls):
    for pic_url in list_of_urls:
        pic_name = os.path.basename(pic_url)
        urllib.request.urlretrieve(pic_url, pic_name)


if __name__ == '__main__':
    parser = parse_args()
    image_size = parser.parse_args().size
    needed_date = parser.parse_args().date
    if re.match(r'\w+-\d+', needed_date) is None:
        sys.exit('Incorect format. Example of correct date format: july-2015')
    if re.match(r'\d+x\d+', image_size) is None:
        sys.exit('Incorrect format. Example of correct size format: 100x100')

    url = 'https://www.smashingmagazine.com/category/wallpapers/'
    list_of_responses = get_response(url)
    all_packs = find_all_wallpapers_packs(list_of_responses)
    dataset = create_dataset_with_names_and_links(all_packs)
    wallpaper_pack_url_to_download = find_needed_pack_by_date(dataset, needed_date)
    list_of_tags_with_urls = get_all_wallpapers_urls_from_pack(wallpaper_pack_url_to_download)
    list_of_wallpapers_urls = get_needed_size_wallpapers(list_of_tags_with_urls, image_size)
    try:
        download_wallpapers(list_of_wallpapers_urls)
    except requests.exceptions.MissingSchema:
        print('There are no wallpapers pack with specified date.')
        print('*hint: make sure, that your date match a format. Use -h for help.')
        sys.exit(0)

    print('Pics, which match to indicated size and date, saved in local folder.')
