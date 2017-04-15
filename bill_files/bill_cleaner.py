"""
A script that will go through and clean up all of the bill files of extra information such as numbers and non-letter
characters. Currently, without filtering the documents the results are abysmal for k-means analysis
"""

import glob
import os
import string

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


def remove_extra_files(clean_sweep=False):
    """
    Goes through and finds any files without useful information and deletes them.

    Parameters:
        clean_sweep: bool that says whether to remove all txt files from the main folders. Be wise about calling this
        function!

    Returns:
        None
    """
    if clean_sweep:
        txt_files = glob.glob("filtered/*.txt")
        for f in txt_files:
            os.remove(f)
    for folder in glob.glob("raw/*/"):
        html_files = glob.glob("{}*.html".format(folder))
        for html in html_files:
            file = open(html, 'r')
            content = file.read()
            if not check_bill(content):
                print(html, " was deleted")
                file.close()
                os.remove(html)
            else:
                file.close()


def get_clean_char(c):
    """
    Checks the character to see if it is a letter, returns that letter or a replacement space character.

    Parameters:
        c: A single character

    Returns:
         char: A letter or a replacement space character.

    """
    ascii_code = ord(c)
    if 65 <= ascii_code <= 90:
        return c
    elif 97 <= ascii_code <= 122:
        return c
    elif ascii_code == 46 or ascii_code == 44:
        return c
    else:
        return ' '

def clean_text(doc):
    doc_char_list = [get_clean_char(c) for c in doc]
    return ''.join(doc_char_list)


def main():
    """
    files = glob.glob('*.txt')
    sample_file = open(os.path.join('sample', 'sample.txt'))
    sample_contents = sample_file.read()
    for f in files:
        current = open(f, 'r')
        doc = current.read()
        current.close()
        clean_doc = doc.replace(sample_contents, '')
        clean_doc = clean_text(clean_doc)
        current = open(os.path.join('filtered',f), 'w')
        current.write(clean_doc)
        current.close()
    sample_file.close()
    """
    remove_extra_files()


if __name__ == '__main__':
    main()