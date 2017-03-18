import glob, os

"""
Simple script to detect and remove files that have no information on them in this folder
"""
"""
files = glob.glob('*.txt')
for file in files:
    f = open(file, 'r')
    contents = f.read()
    should_delete = False
    if 'The resource you are looking for has been removed, had its name changed, or is temporarily unavailable.' in\
            contents:
        should_delete = True
    f.close()
    if should_delete:
        os.remove(file)

"""
