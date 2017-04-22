"""
Takes already saved html files, scrapes them, removes extra characters, and places them in the proper folder.
"""

import glob
import os
from async_bill_scrape import get_clean_contents, make_txt_of
from bs4 import BeautifulSoup
import re


def extract_name(raw_html):
    # TODO: Get the full name, it appears that this is sometimes split up
    soup = BeautifulSoup(open(raw_html, 'r'), 'lxml')
    return soup, soup.body.find('b').text.title()


def clean_description(unfiltered_description):
    remove_end = unfiltered_description.split('.')[0]
    # TODO: Fix this so it doesn't cut out a year
    no_numbers = re.sub('1[0-9]\\s*', ' ', remove_end)
    try:
        filtered = no_numbers[0].upper() + no_numbers[1:]
    except:
        filtered = "No description"
    return filtered


def extract_description(soup):
    text = soup.text.split(" ")
    description_range = [0, 0]
    for i in range(len(text) - 1):
        if 'general' in text[i].lower() and 'description' in text[i+1].lower():
            description_range[0] = i+2
        elif 'highlighted' in text[i].lower() and 'provisions' in text[i+1].lower():
            description_range[1] = i + 1
    unfiltered_description = " ".join(text[description_range[0]:description_range[1]])
    clean = clean_description(unfiltered_description)
    return clean


def extract_link(year, bill):
    link = "http://le.utah.gov/~{year}/bills/static/{bill}.html".format(year=year, bill=bill)
    return link


def extract_bill_and_year(filename):
    """
    Finds the bill id and year and returns it

    :param filename:
    :return:
    """
    just_file = os.path.split(filename)[-1]
    year = just_file[0:4]
    end_name = just_file.split('hbillint')[1]
    bill = end_name.split('.')[0]
    return year, bill


def print_information(year, bill, name, description, link):
    """
    Used for testing purposes only, prints information about the bill.

    :param year:
    :param bill:
    :param name:
    :param description:
    :param link:
    :return:
    """
    print('_____________________________________________________________')
    print("{bill}: {name}\n{year}".format(bill=bill, name=name,year=year))
    print('-------------------------------------------------------------')
    print("Description:\n{}".format(description))
    print("Link: {}".format(link))


def extract_files():
    import pickle
    # For now, just do the one folder:
    bill_details = {}
    for file in glob.glob(os.path.join("bill_files", "raw", "2017", "*")):
        year, bill = extract_bill_and_year(file)
        soup, name = extract_name(file)
        description = extract_description(soup)
        link = extract_link(year, bill)
        bill_details[(year, bill)] = {'year': year, 'bill': bill, 'name': name, 'description': description, 'link':
                                      link}
    pickle.dump(bill_details, open(os.path.join("analysis", "bill_information.pickle"), 'wb'))

def make_txt(year, bill, contents):
    """
    Gets just the text

    :param year:
    :param bill:
    :param contents:
    :return:
    """
    make_txt_of({}, bill, year, contents)


def get_files():
    """
    Goes through each folder and file in the raw folder, parses out just formated text from the bill for clustering
    algorithm.

    :return:
    """
    raw_folders = glob.glob(os.path.join("bill_files", "raw", "*/"))
    # TODO: Do this all asynchronously, so it doesn't take forever.
    for folder in raw_folders:
        files = glob.glob(os.path.join(folder, "*.html"))
        for f in files:
            year, bill = extract_bill_and_year(f)
            file_contents = open(f)
            file_cleaned = get_clean_contents(file_contents.read())
            make_txt(year, bill, file_cleaned)
            file_contents.close()


def main():
    extract_files()


if __name__ == '__main__':
    main()