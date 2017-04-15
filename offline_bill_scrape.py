"""
Takes already saved html files, scrapes them, removes extra characters, and places them in the proper folder.
"""

import glob
import os
from async_bill_scrape import get_clean_contents, make_txt_of


def get_info(filename):
    just_file = os.path.split(filename)[-1]
    year = just_file[0:4]
    end_name = just_file.split('hbillint')[1]
    bill = end_name.split('.')[0]
    return year, bill


def make_txt(year, bill, contents):
    make_txt_of({}, bill, year, contents)


def get_files():
    raw_folders = glob.glob(os.path.join("bill_files", "raw", "*/"))
    # TODO: Do this all asynchronously, so it doesn't take forever.
    for folder in raw_folders:
        files = glob.glob(os.path.join(folder, "*.html"))
        for f in files:
            year, bill = get_info(f)
            file_contents = open(f)
            file_cleaned = get_clean_contents(file_contents.read())
            make_txt(year, bill, file_cleaned)
            file_contents.close()


def main():
    get_files()


if __name__ == '__main__':
    main()