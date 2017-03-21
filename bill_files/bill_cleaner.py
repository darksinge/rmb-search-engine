# A script that will go through and clean up all of the bill files of extra information such as numbers and non-letter
# characters. Currently, without filtering the documents the results are abysmal for k-means analysis
import glob
import os
import string

def get_clean_char(c):
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