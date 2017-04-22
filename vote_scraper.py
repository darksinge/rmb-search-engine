"""
Scrapes each bill vote for every year in the Utah House of Representatives and the Utah Senate and collects information about each
bill.
The information is then saved in a csv for easy access in the future.
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import time


def get_reps(unfiltered_reps):
    names = []
    for r in unfiltered_reps:
        names.append(r.text)
    return names


def is_bill(item):
    possible_names = ['HB', 'HJR', 'SB']
    for p in possible_names:
        if p in item[0]:
            return True
    return False


def determine_bill_feature(item):
    name = None
    possible_features = {None: None, 'Yeas': 2, 'Nays': 2, 'Absent': 5}
    for p, i in possible_features.items():
        if item[0] == p:
            name = p
    if name is not None:
        return name, item[possible_features[name]]
    return name, None


def get_bill_info(soup):
    unfiltered_info = soup.find_all('b')
    info = {}
    for r in unfiltered_info:
        items = r.text.split()
        if len(items) > 0:
            name, features = determine_bill_feature(items)
            if name is not None:
                info[name] = features
            elif is_bill(items):
                info['bill_name'] = items[0]
    return info


def get_vote_names(info, representatives):
    """

    :param info:
    :param representatives:
    :return:
    """
    yeas = info['Yeas']
    nays = info['Nays']
    y_names = representatives[0:int(yeas)]
    n_names = representatives[int(yeas):int(nays)+int(yeas)]
    a_names = representatives[int(nays)+int(yeas):]
    return {'yeas': y_names, 'nays': n_names, 'absent': a_names}


def get_page_contents(response):
    """

    :param response:
    :return:
    """
    soup = BeautifulSoup(response.content, 'lxml')
    # Used to determine whether the page gives us something interesting
    content_len = len(soup.body.text)
    # TODO: This var is out of place
    unfiltered_reps = soup.find_all('td')
    filtered_reps = get_reps(unfiltered_reps)
    bill_info = get_bill_info(soup)
    if 'Yeas' in bill_info:
        vote_names = get_vote_names(bill_info, filtered_reps)
    else:
        vote_names = {}
    return filtered_reps, content_len, bill_info, vote_names


def get_next_page(base_url, end_url, vote_number):
    """

    :param base_url:
    :param end_url:
    :param vote_number:
    :return:
    """
    full_url = base_url + str(vote_number) + end_url
    # print(full_url)
    response = requests.get(full_url)
    reps, content_len, bill_info, vote_names = get_page_contents(response)
    # TODO:
    return reps, content_len, bill_info, vote_names


def get_members(base_url, end_url):
    """
    Used to get just the representatives for the current session info was being collected. Called once per session,

    Parameters:
        base_url: string
        end_url: string

    Returns:
        list: strings of representative names
    """
    reps, content_len, bill_info, votes = get_next_page(base_url, end_url, 1)
    return reps


def save_csv_data(representatives, votes, house, session):
    """
    Creates a DataFrame of data using the information extracted and creates a csv file for future use.

    Parameters:
        representatives: a list of strings with the names of all the representatives
        votes: a list of votes of the individual
        house: string: house the information pertains to
        session: string/int, representing the year (and session, if it is not a general session)

    Returns:
        None
    """
    df = pd.DataFrame({'Representatives': representatives})
    for bill in votes:
        vote_record = []
        for person in representatives:
            if person in bill['vote_yea']:
                vote_record.append(1)
            elif person in bill['vote_nay']:
                vote_record.append(0)
            else:
                vote_record.append(2)
        df[bill['bill']] = vote_record
    df.to_csv(os.path.join("voting", house+str(session)+'_voting.csv'))


def get_session_voting(year, house):
    """
    Goes through the session for the year and house and extracts information about each vote made during that session,
    then sends that data to be saved as a csv.

    Parameters:
        year: int, a four digit number for the year that will be checked. Note that this will only work for the years
        following 2010
        house: character: 'H' or 'S', representing house or senate (respectively)

    Returns:
        None
    """
    current_vote = 2
    base_url = "https://le.utah.gov/DynaBill/svotes.jsp?sessionid={}GS&voteid=".format(year)
    end_url = "&house={}".format(house)
    cont_reading = True
    members = get_members(base_url, end_url)
    votes = []
    while cont_reading:
        reps, content_len, bill_info, vote_names = get_next_page(base_url, end_url, current_vote)
        if 'bill_name' in bill_info and 'yeas' in vote_names:
            votes.append({'bill': bill_info['bill_name'], 'yeas': bill_info['Yeas'], 'nays': bill_info['Nays'],
                          'absent': bill_info['Absent'], 'vote_yea': vote_names['yeas'], 'vote_nay': vote_names['nays'],
                          'vote_absent': vote_names['absent']})
        if content_len < 10:
            cont_reading = False
        current_vote += 1
    save_csv_data(members, votes, house, year)


def vote_scrape():
    # TODO: Only check votes from the current year
    for year in range(2016, 2017):
        get_session_voting(year, 'H')
        get_session_voting(year, 'S')


if __name__ == '__main__':
    vote_scrape()