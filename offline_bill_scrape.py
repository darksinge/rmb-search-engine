"""
Takes already saved html files, scrapes them, removes extra characters, and places them in the proper folder.
"""

import glob
import os
from async_bill_scrape import get_clean_contents, make_txt_of, right_character
from bs4 import BeautifulSoup
from configs import default_path
import re
import pickle


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
    organized_contents = tag.prettify()
    cleaned_contents = ''.join([right_character(c) for c in organized_contents])
    return cleaned_contents


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


def write_body_html(soup, year, bill):
    """
    Preserves only the body of the html file and saves it in www folder to allow access to the files from the webpage
    without the extra stuff.

    Parameters:
        soup: BeautifulSoup, parsed html file
        year: int/str, year the bill was looked at
        bill: str, the bill id

    Returns:
        None
    """
    bill_contents = get_bill_contents(soup)
    main_folder = os.path.join(default_path,"www")
    if not os.path.exists(main_folder):
        os.mkdir(main_folder)
    year_folder = os.path.join(main_folder, year)
    if not os.path.exists(year_folder):
        os.mkdir(year_folder)
    f = open(os.path.join(year_folder, bill + '.html'), 'w')
    f.write(bill_contents)
    f.close()


def get_id(file_path):
    f_split = file_path.split('html')[0]
    raw_id = f_split[-7:-1]
    return raw_id


def needs_updates(year='2017'):
    """
    Checks to see if updates are needed for the year given based on what has been scraped already. If we haven't created
    an uploaded.pickle, treat things like everything needs to be done, and to keep things simple, it just returns a
    dictionary with 'all' as a key.

    Parameters:
        year: str, the year to check. Currently just 2017 for simplicity sake

    Returns:
    """
    try:
        files_made = pickle.load(open(os.path.join(default_path, "analysis", "uploaded.pickle"), 'rb'))
        year_paths = glob.glob(os.path.join(default_path, "bill_files", "raw", year))
        years_only = [os.path.split(y)[-1] for y in year_paths]
        years_to_update = {}
        for key, values in files_made.items():
            year_made = os.path.split(key)[-1]
            files_raw = glob.glob(os.path.join(default_path, "bill_files", "raw", year_made, "*"))
            id_raw = [get_id(f) for f in files_raw]
            if year_made in years_only:
                id_made = [get_id(f) for f in values]
                for raw in id_raw:
                    if raw not in id_made:
                        if year_made not in years_to_update:
                            years_to_update[year_made] = [raw]
                        else:
                            years_to_update[year_made].append(raw)
            else:
                years_to_update[year_made] = id_raw

            if len(years_to_update) == 0:
                return {"none": []}
    except FileNotFoundError:
        return {"all": []}


def track_changes(make_new=False):
    """
    Creates or modifies a json to keep track of files that have already been changed so to not offline scrape things
    repeatedly

    :return:
    """
    if make_new:
        files_made = {}
    else:
        files_made = pickle.load(open(os.path.join(default_path, "analysis", "uploaded.pickle"), 'rb'))
        print(files_made)
    updated_years = glob.glob(os.path.join(default_path, "www", "*"))
    for y in updated_years:
        updated_files = glob.glob(os.path.join(y, "*"))
        if y in files_made:
            for f in updated_files:
                if f not in files_made[y]:
                    files_made[y].append(f)
        else:
            files_made[y] = updated_files
    pickle.dump(files_made, open(os.path.join(default_path, "analysis", "uploaded.pickle"), 'wb'))



def extract_files():
    """
    Extracts all the information needed for the bills to be used on the page. Right now just set for 2017, later when
    parsing has improved this may change.

    Returns:
         None
    """
    # For now, just do the one folder:
    bill_details = {}
    # TODO: make it take in a dictionary like from needs_updates to use as an updater instead of glob
    for file in glob.glob(os.path.join(default_path, "bill_files", "raw", "2017", "*")):
        year, bill = extract_bill_and_year(file)
        soup, name = extract_name(file)
        description = extract_description(soup)
        link = extract_link(year, bill)
        bill_details[(year, bill)] = {'year': year, 'bill': bill, 'name': name, 'description': description, 'link':
                                      link}
        write_body_html(soup, year, bill)
    if not (os.path.exists(os.path.join(default_path, "analysis", "uploaded.pickle"))):
        track_changes(make_new=True)
    else:
        track_changes()
    pickle.dump(bill_details, open(os.path.join(default_path, "analysis", "bill_information.pickle"), 'wb'))


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
    Goes through each folder and file in the raw folder, parses out just formatted text from the bill for clustering
    algorithm.

    :return: None
    """
    raw_folders = glob.glob(os.path.join(default_path, "bill_files", "raw", "*/"))
    for folder in raw_folders:
        files = glob.glob(os.path.join(folder, "*.html"))
        for f in files:
            year, bill = extract_bill_and_year(f)
            file_contents = open(f)
            file_cleaned = get_clean_contents(file_contents.read())
            make_txt(year, bill, file_cleaned)
            file_contents.close()


def main():
    #extract_files()
    needs_updates()



if __name__ == '__main__':
    main()