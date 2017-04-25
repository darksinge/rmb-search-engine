"""
This is created by Bradley Robinson.

Asynchronously goes through the bills available on le.utah.gov, and saves them as html files.
"""

import os, glob, aiohttp, asyncio
from bs4 import BeautifulSoup
import pandas as pd
from default_path import default_path


def check_bill(content):
    """
    Simply checks to see if the html response has information or not. That way we don't save useless files.

    Parameters:
        content: String of the html file

    Returns:
         bool: Whether or not the file is useful.
    """
    if 'The resource you are looking for has been removed, had its name changed, or is temporarily unavailable.' in\
        content:
        return False
    else:
        return True


def create_raw_html(year, house, bill, html):
    """
    Saves the current html file in a designated folder so scraping can be done offline. Also allows us to fix errors

    Parameters:
        year: String or integer of the year
        house: String representing house
        bill: String of the name of the bill
        html: The full document.

    Returns:
        string: a string of content without non-unicode characters
    """
    raw_files_folder = os.path.join(default_path,'bill_files', 'raw', str(year))
    if not os.path.exists(raw_files_folder):
        os.mkdir(raw_files_folder)
    if check_bill(html):
        file = open(os.path.join(raw_files_folder, '{}{}{}.html'.format(year, house, bill)), 'w',
                    encoding='utf-8')
        file.write(html)
        file.close()
        return html
    else:
        return None


def get_clean_contents(file_contents):
    """

    Parameters:
        file_contents:

    Returns:
        A string with just words for indexing purposes
    """
    soup = BeautifulSoup(file_contents, 'lxml')
    full_text = soup.body.text
    split_text = [just_letters(c) for c in full_text]
    return ''.join(split_text)


async def parse_bill_page(session, year, bill, house):
    """
    Searches for a bill page and gets information from it.

    Parameters:
        session: The session to be searched
        year: Year of the session, integer or character
        bill: String of the bill name
        house: String representing the house.

    Returns:
         The parsed text
    """
    with aiohttp.Timeout(10, loop=session.loop):
        async with session.get("http://le.utah.gov/~{}/bills/{}/{}.htm".format(year, house, bill)) as response:
            content = await response.text()
            cleaned_content = create_raw_html(year, house, bill, content)
            if cleaned_content:
                return "great"
                # return get_clean_contents(cleaned_content)
            else:
                return 'error'


def extract_year(filename):
    """
    Finds the year of a given csv filename that has been produced by vote_scraper.py.

    Parameters:
        filename: A string of the full filename (including the folder). Most follow the pattern set in vote_scraper.py,
        otherwise it will not return the proper year

    Returns:
        A string for the year that the csv file represents
    """
    end = os.path.split(filename)[1]
    year = end[1:5]
    return year


def right_character(c):
    """
    Simply checks to see if the character is unicode to allow the page to be saved.

    Parameters:
        c: A character

    Returns:
        A unicode character
    """
    if 0 < ord(c) < 127:
        return c
    else:
        return ' '


def just_letters(c):
    """
    Used to check if a character is an ASCII letter and just returns it as is if that is the case.
    Parameters:
        c: a character

    Returns:
         A single character.
    """
    ascii_code = ord(c)
    if 65 <= ascii_code <= 90:
        return c
    elif 97 <= ascii_code <= 122:
        return c
    else:
        return ' '


def clean_characters(content):
    """
    Takes in a string, removes any non-unicode characters as well as unimportant punctuation.
    Parameters:
        content: A string from a web page that needs to be cleaned
    Returns:
        string: A string that joins a web page.
    """
    stripped = [right_character(c) for c in content]
    return ''.join(stripped)


def make_txt_of(content_dict, bill, year, text=None):
    """
    Creates a filtered text file of the bill and saves it to a data folder. This file can be used for term indexing.

    Parameters:
        content_dict: A dictionary with the contents of the bill. Later we might try to extract more information, hence
        the dictionary
        bill: A string name of the bill
        year: An integer value for the year
        text: To save it just from text, give a string

    Returns:
        None
    """
    folders = os.path.join(default_path, "bill_files", "filtered", year)
    if not os.path.exists(folders):
        os.mkdir(folders)
    f = open(os.path.join(folders, '{}.txt'.format(bill)), 'w')
    if text:
        f.write(text)
    else:
        # f.write('Sponsors: {sponsors}'.format(sponsors=content_dict['sponsors']))
        # f.write('Modifications: {mods}'.format(mods=content_dict['mods']))
        # f.write('Full text:\n')
        try:
            f.write(clean_characters(content_dict['full']))
        except UnicodeEncodeError:
            f.write(clean_characters(content_dict['full']))
    f.close()


async def search_bills(loop, year, bill_list):
    """
    Asynchronous function to search for bills. Goes through each value in the bill list and tries to find its
    corresponding bill, and scrapes it if the file is found. Note that this function lacks any way to limit the numbers
    of requests. However, since some functions that are called use the hard drive, there is an implicit limit. This,
    however, should be explicit.

    Calls functions to save a txt file for each bill found.

    Parameters:
        loop: An aiohttp event loop that has been initialized.
        year: What year will you be searching for the bill information?
        bill_list: An iterable (list) that contains the names of all the bills to be searched.

    """
    async with aiohttp.ClientSession(loop=loop) as session:
        for bill in bill_list:
            if 'HB' or 'HJR' in bill:
                house = 'hbillint'
            elif 'SB' in bill:
                house = 'sbillint'
            else:
                house = 'sbillint'
            # sponsors, changes,
            bill_text = await parse_bill_page(session, year, bill, house)
            if bill_text == 'error':
                print('bill: ', bill, ' year: ', year, ' not found')
                house = house[0] + 'billenr'
                # sponsors, changes,
                bill_text = await parse_bill_page(session, year, bill, house)
            # 'sponsors': sponsors, 'mods': changes,
            if bill_text != 'error':
                pass
                # make_txt_of({'full': bill_text}, bill, year)


def go_by_bills_from_csv(house=True, senate=True, year=None):
    """
    Used to extract known names of bills from voting records that have already been scraped. Used for years following
    2011. Some sessions the scraping failed, so there might be a need to scrape by year manually if there are few bills
    in the list. Functionality will be added for that.

    Parameters:
        house: bool, if true it will find the voting csv for the house
        senate: bool, if true, will find the voting csv for the senate
        year: int/str, if there is a year, it will be limited to that year

    Returns:
        None
    """
    if senate and house:
        files = glob.glob(os.path.join(default_path, "voting", "*.csv"))
    elif house:
        files = glob.glob(os.path.join(default_path, "voting", "H*.csv"))
    elif senate:
        files = glob.glob(os.path.join(default_path, "voting", "S*.csv"))
    else:
        files = glob.glob(os.path.join(default_path, "voting", "*.csv"))
    bill_names = {}
    for file in files:
        if year:
            if str(year) in file:
                df = pd.read_csv(file)
                year = extract_year(file)
                bill_names[year] = df.columns[2:]
        else:
            df = pd.read_csv(file)
            year = extract_year(file)
            bill_names[year] = df.columns[2:]
    loop = asyncio.get_event_loop()
    f = asyncio.wait([search_bills(loop, year, bill_list) for year, bill_list in bill_names.items()])
    loop.run_until_complete(f)


def make_bill_title(num, house):
    """
    Used to generate numbers that follow the proper format to scrape the website guessing at possible bill names

    Args:
        num: The bill number that you would like to create a formated name for
        house: Which house would you create the name for. Takes 'SB' or 'HB'

    Returns:
        string: A properly formatted bill name to search for. Example: 'HB0205' or 'SB0003'
    """
    bill = str(num).split()
    bill_len = len(bill[0])
    while bill_len < 4:
        bill.insert(0, '0')
        bill_len += 1
    bill.insert(0, house)
    return ''.join(bill)


def go_by_year(start=1997, end=2012, senate=True, house=True):
    """
    Searches for bills for the years 1997-2011. Calls functions to parse and save the files.

    While there is information about bills organized nicely in CSVs for the yars following 2011, voting information
    has not been collected for years before that.

    Args:
        start: int, the year that the search/scraping will start
        end: int, the end year
        senate: bool, if true will scrape bills in the senate
        house: bool, if true will scrape bills in the house

    Returns:
        None
    """
    year_range = [x for x in range(start, end - 1)]
    if house:
        hbs = [make_bill_title(x, 'HB') for x in range(1, 515)]
        loop = asyncio.get_event_loop()
        f = asyncio.wait([search_bills(loop, year, hbs) for year in year_range])
        loop.run_until_complete(f)
    if senate:
        sbs = [make_bill_title(x, 'SB') for x in range(1, 300)]
        loop = asyncio.get_event_loop()
        f = asyncio.wait([search_bills(loop, year, sbs) for year in year_range])
        loop.run_until_complete(f)


def get_last_scrape_data():
    pass


def save_progress():
    """
    Saves information about the current scrape to ensure that previous work from scraping is not duplicated.

    """
    pass


def bill_scrape():
    """
    Goes through and scrapes all the bills. Note that the code inside here must be changed to scrape everything.
    Saves html files in the bill_files/raw/ folders, so that they can then be parsed with the offline_bill_scrape

    Returns:
         None
    """
    go_by_bills_from_csv(year=2017)
    #go_by_year()


if __name__ == '__main__':
    bill_scrape()