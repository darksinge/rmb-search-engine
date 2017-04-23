"""
Takes already saved html files, scrapes them, removes extra characters, and places them in the proper folder.
"""

import glob
import os
from async_bill_scrape import get_clean_contents, make_txt_of
from bs4 import BeautifulSoup
import re


def extract_name(raw_html):
    """
    Parses out the name of the bill. Has only been tested on bills from 2017. Unfortunately the bill pages lack
    formatting that makes it possible to easily parse through pages, so it takes a little bit of work to figure things
    out.

    Parameters:
        raw_html:

    Returns:
        BeautifulSoup: object that contains parsed page ready to use with other functions.
        str: text representing the name of the bill.
    """
    # TODO: Get the full name, it appears that this is sometimes split up
    soup = BeautifulSoup(open(raw_html, 'r'), 'lxml')
    return soup, soup.body.find('b').text.title()


def clean_description(unfiltered_description):
    """
    Takes a string of the description that has already been extracted and removes extra spaces and symbols.

    Parameters:
        unfiltered_description: string, the extracted description to be cleaned

    Returns:
        str: the full description of the bill, filtered.
    """
    remove_end = unfiltered_description.split('.')[0]
    # TODO: Fix this so it doesn't cut out a year
    no_numbers = re.sub('1[0-9]\\s*', ' ', remove_end)
    try:
        filtered = no_numbers[0].upper() + no_numbers[1:]
    except:
        filtered = "No description"
    return filtered


def extract_description(soup):
    """
    Takes a BeautifulSoup object and extracts the description of a bill.

    Parameters:
        soup: BeautifulSoup, the bill html parsed

    Returns:
        str: the bill description.

    """
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
    """
    Finds the correct link to the legislative website.

    Parameters:
        year: str or int, four digit year.
        bill: str, with the id of the bill, i.e. HB0001
    :return:
    """
    link = "http://le.utah.gov/~{year}/bills/static/{bill}.html".format(year=year, bill=bill)
    return link


def extract_bill_and_year(filename):
    """
    Finds the bill id and year and returns it

    Parameters:
        filename: str, created os.path.join, the path of the raw file.

    Returns:
        str: four digit string of the year the bill is from
        str: title of the bill, i.e. HB0001
    """
    just_file = os.path.split(filename)[-1]
    year = just_file[0:4]
    end_name = just_file.split('hbillint')[1]
    bill = end_name.split('.')[0]
    return year, bill


def get_bill_contents(soup):
    """
    Gets just the body of the bill and returns the html of it.

    Parameters:
        soup: BeautifulSoup, object of parsed bill page

    Returns:
        str: html code and content for just the bill page
    """
    tag = soup.body
    return tag.prettify()


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
    """
    Extracts all the information needed for the bills to be used on the page. Right now just set for 2017, later when
    parsing has improved this may change.

    Returns:
         None
    """
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
        bill_contents = get_bill_contents(soup)
        if not os.path.exists(os.path.join("www")):
            os.mkdir("www")
        if not os.path.exists(os.path.join("www", year)):
            os.mkdir(os.path.join("www", year))
        f = open(os.path.join("www", year, bill + '.html'), 'w', encoding="utf-8")
        f.write(bill_contents)
        f.close()
    pickle.dump(bill_details, open(os.path.join("analysis", "bill_information.pickle"), 'wb'))


def make_txt(year, bill, contents):
    """
    Gets just the text of the document, just for data analysis, not anything too serious.

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

    :return: None
    """
    raw_folders = glob.glob(os.path.join("bill_files", "raw", "*/"))
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