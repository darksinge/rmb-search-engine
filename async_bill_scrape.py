"""
This is the asyncronous version of bill_scraper. This should be used if possible, since it is significantly faster,
and doesn't get 'stuck' if the server takes too long retrieving a request.
"""

import os, glob, aiohttp, asyncio
from bs4 import BeautifulSoup
import pandas as pd
import string


def get_changes(soup):
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


async def parse_bill_page(session, year, bill, house):
    with aiohttp.Timeout(10, loop=session.loop):
        async with session.get("http://le.utah.gov/~{}/bills/{}/{}.htm".format(year,house,bill)) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'lxml')
            #sponsors = get_sponsor(soup)
            #changes = get_changes(soup)
            full_text = soup.body.text
            # split_text = [split_number_words(full_text, i) for i in range(len(full_text))]
            split_text = [just_letters(c) for c in full_text]
            # return full_text, sponsors, changes
            return ''.join(split_text)


def extract_year(filename):
    end = os.path.split(filename)[1]
    year = end[1:5]
    return year


def right_character(c):
    if 0 < ord(c) < 127:
        return c
    else:
        return ' '

def just_letters(c):
    ascii_code = ord(c)
    if 65 <= ascii_code <= 90:
        return c
    elif 97 <= ascii_code <= 122:
        return c
    elif ascii_code == 46 or ascii_code == 44:
        return c
    else:
        return ' '

def split_number_words(word, index):
    ascii_l = string.ascii_letters
    digits = string.digits
    if index < len(word) - 1:
        if word[index] in ascii_l and word[index+1] in digits:
            return word[index] + ' '
    return right_character(word[index])


def clean_characters(content):
    stripped = [right_character(c) for c in content]
    return ''.join(stripped)


def make_txt_of(content_dict, bill, year):
    file_name = '{bill}_{year}.txt'.format(bill=bill, year=year)
    if 'The resource you are looking for has been removed, had its name changed, or is temporarily unavailable.'\
        not in content_dict['full']:
        f = open(os.path.join("bill_files", file_name), 'w')
        # f.write('Sponsors: {sponsors}'.format(sponsors=content_dict['sponsors']))
        # f.write('Modifications: {mods}'.format(mods=content_dict['mods']))
        # f.write('Full text:\n')
        try:
            f.write(clean_characters(content_dict['full']))
        except UnicodeEncodeError:
            f.write(clean_characters(content_dict['full']))
        f.close()
    else:
        print(bill, ' was not found, unable to save.')


async def search_bills(loop, year, bill_list):
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
            error_msg = 'The resource you are looking for has been removed, had its name changed, or is temporarily ' \
                        'unavailable.'
            if error_msg in bill_text:
                print('bill: ', bill, ' year: ', year, ' not found')
                house = house[0] + 'billenr'
                # sponsors, changes,
                bill_text = await parse_bill_page(session, year, bill, house)
            # 'sponsors': sponsors, 'mods': changes,
            make_txt_of({'full': bill_text}, bill, year)


def get_bill_names():
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
    bill = str(num).split()
    bill_len = len(bill[0])
    while bill_len < 4:
        bill.insert(0, '0')
        bill_len += 1
    bill.insert(0, house)
    return ''.join(bill)


def go_by_year():
    year_range = [x for x in range(1997, 2011)]
    hbs = [make_bill_title(x, 'HB') for x in range(1, 515)]
    # senatebs = [make_bill_title(x, 'SB') for x in range(1, 300)]
    loop = asyncio.get_event_loop()
    f = asyncio.wait([search_bills(loop, year, hbs) for year in year_range])
    loop.run_until_complete(f)
    #loop2 = asyncio.get_event_loop()
    #f2 = asyncio.wait([search_bills(loop2, year, senatebs) for year in year_range])
    #loop.run_until_complete(f2)


def main():
    # If you would like to search by going through the data files with the actual names, uncomment:
    get_bill_names()
    go_by_year()


if __name__ == '__main__':
    main()