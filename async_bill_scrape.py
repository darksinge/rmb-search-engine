"""
This is created by Bradley Robinson.

TODO:
We need to try not to replicate any work that has been done already. That way we don't hit the servers too hard.
We need to save the files to html as is.
Then parse the information from the html files rather than the other server, that way we only do things once.


This is the asyncronous version of bill_scraper. This should be used if possible, since it is
significantly faster, and doesn't get 'stuck' if the server takes too long retrieving a request.
"""

import os, glob, aiohttp, asyncio
from bs4 import BeautifulSoup
import pandas as pd
import string


def get_changes(soup):
    """
    Supposed to find all the changes made to the text, but currently doesn't always work. Variable formatting is
    probably responsible.
    :param soup:
    :return:
    """
    changes = soup.find_all('u')
    change_list = [x.text for x in changes]
    return ''.join(change_list)


def get_sponsor(soup):
    b_divs = soup.find_all('b')
    sponsors = []
    # TODO: This doesn't give us anything, try again
    """for b in b_divs:
        if 'Sponsor' in b:
            b_text = b.text
            name = b_text.split('Sponsor: ')[1]
            sponsors.append(name)"""
    return sponsors


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
    if not os.path.exists(os.path.join('bill_files', 'raw', str(year))):
        os.mkdir(os.path.join('bill_files', 'raw', str(year)))
    if check_bill(html):
        file = open(os.path.join('bill_files', 'raw', str(year), '{}{}{}.html'.format(year, house, bill)), 'w')
        only_unicode = [right_character(c) for c in html]
        joined = ''.join(only_unicode)
        file.write(joined)
        file.close()
        return joined
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


def split_number_words(word, index):
    """
    Takes in words and does stuff. Currently unused, just a function for testing different ways of filtering content

    Parameters:
        word: A string of a word that needs to be filtered
        index: Where we will be checking values

    Returns:
        A character
    """
    # TODO: Replace with regular expressions instead of this slightly convoluted code
    ascii_l = string.ascii_letters
    digits = string.digits
    if index < len(word) - 1:
        if word[index] in ascii_l and word[index+1] in digits:
            return word[index] + ' '
    return right_character(word[index])


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
    file_name = '{bill}_{year}.txt'.format(bill=bill, year=year)
    folders = os.path.join("bill_files", "filtered", year)
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


def get_bill_names():
    """
    Used to extract known names of bills from voting records that have already been scraped. Used for years following
    2011. Some sessions the scraping failed, so there might be a need to scrape by year manually if there are few bills
    in the list. Functionality will be added for that.

    Parameters:
        None

    Returns:
        None
    """
    files = glob.glob(os.path.join("voting", 'S*.csv'))
    bill_names = {}
    for file in files:
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


def go_by_year():
    """
    Searches for bills for the years 1997-2011. Calls functions to parse and save the files.

    While there is information about bills organized nicely in CSVs for the yars following 2011, voting information
    has not been collected for years before that.

    Args:
        None

    Returns:
        None

    """
    year_range = [x for x in range(1997, 2011)]
    hbs = [make_bill_title(x, 'HB') for x in range(1, 515)]
    # senatebs = [make_bill_title(x, 'SB') for x in range(1, 300)]
    loop = asyncio.get_event_loop()
    f = asyncio.wait([search_bills(loop, year, hbs) for year in year_range])
    loop.run_until_complete(f)
    #loop2 = asyncio.get_event_loop()
    #f2 = asyncio.wait([search_bills(loop2, year, senatebs) for year in year_range])
    #loop.run_until_complete(f2)


def get_last_scrape_data():
    pass


def save_progress():
    """
    Saves information about the current scrape to ensure that previous work from scraping is not duplicated.
    :return:
    """
    pass


def bill_scrape():
    # If you would like to search by going through the data files with the actual names, uncomment:
    get_bill_names()
    go_by_year()


if __name__ == '__main__':
    # TODO: Actually get the URL for the bill document.
    bill_scrape()