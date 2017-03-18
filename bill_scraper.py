import requests, os, glob
from bs4 import BeautifulSoup
import pandas as pd


def get_changes(soup):
    changes = soup.find_all('u')
    change_list = [x.text for x in changes]
    return ''.join(change_list)


def get_sponsor(soup):
    b_divs = soup.find_all('b')
    sponsors = []
    for b in b_divs:
        if 'Sponsor' in b:
            b_text = b.text
            name = b_text.split('Sponsor: ')[1]
            sponsors.append(name)
    return sponsors


def parse_bill_page(year, bill):
    # TODO: SHOULD CHANGE BASED ON BILL TYPE
    content = requests.get("http://le.utah.gov/~{}/bills/hbillint/{}.htm".format(year, bill)).content
    soup = BeautifulSoup(content, 'lxml')
    sponsors = get_sponsor(soup)
    changes = get_changes(soup)
    full_text = soup.body.text
    return sponsors, changes, full_text


def extract_year(filename):
    end = os.path.split(filename)[1]
    year = end[1:5]
    return year


def make_txt_of(content_dict, bill, year):
    file_name = '{bill}_{year}.txt'.format(bill=bill, year=year)
    f = open(os.path.join("bill_files", file_name), 'w')
    f.write('Sponsors: {sponsors}'.format(sponsors=content_dict['sponsors']))
    f.write('Modifications: {mods}'.format(mods=content_dict['mods']))
    f.write('Full text:\n')
    f.write(content_dict['full'])
    f.close()


def get_bill_names():
    files = glob.glob(os.path.join("voting", '*.csv'))
    bill_names = {}
    for file in files:
        df = pd.read_csv(file)
        year = extract_year(file)
        bill_names[year] = df.columns[2:]
    for year, bill_list in bill_names.items():
        for bill in bill_list:
            sponsors, changes, bill_text = parse_bill_page(year, bill)
            make_txt_of({'sponsors': sponsors, 'mods': changes, 'full': bill_text}, bill, year)



def go_through_bills():
    get_bill_names()


def main():
    # TODO: Look at bills
    get_bill_names()
    go_through_bills()


if __name__ == '__main__':
    main()