from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import time

base = "https://le.utah.gov/DynaBill/svotes.jsp?sessionid=2017GS&voteid="
end = "&house="

def get_next_page(vote_number, house):
	print('.', end='')
	url =  base + str(vote_number) + end + house
	response = requests.get(url)
	content = response.content
	page = BeautifulSoup(content, 'html.parser')
	contents = page.body.text
	content_size = len(contents)
	representatives = page.find_all('td')
	names = []
	print('!')
	for r in representatives:
		names.append(r.text)
	info = page.find_all('b')
	return names, info, content_size
	
def filter_bill_info(bill_info):
    bill_name = str()
    yeas = None
    nays = None
    absent = None
    for r in bill_info:
        names = r.text.split()
        if len(names) > 0:
            if 'HB' in names[0]:
                bill_name = names[0]
            elif 'HJR' in names[0]:
                bill_name = names[0]
            elif 'SB' in names[0]:
                bill_name = names[0]
            elif names[0] == 'Yeas':
                yeas = names[2]
            elif names[0] == 'Nays':
                nays = names[2]
            elif names[0] == 'Absent':
                absent = names[5]
    return bill_name, yeas, nays, absent

def get_vote_names(yeas, nays, absent, representatives):
	# TODO: finish this
	y_names = representatives[0:int(yeas)]
	n_names = representatives[int(yeas):int(nays)+int(yeas)]
	a_names = representatives[int(nays)+int(yeas):]
	#print('yeas: ', y_names, '\nnays:', n_names,'\nabsent: ', a_names)
	return y_names, n_names, a_names
	
def make_df(full_r_list, votes, house="house"):
	# TODO: goes through all of the things, then maps out the representatives
    df = pd.DataFrame({'Representatives': full_r_list})
    for bill in votes:
        vote_record = []
        for person in full_r_list:
            if person in bill['vote_yea']:
                vote_record.append(1)
            elif person in bill['vote_nay']:
                vote_record.append(0)
            elif person in bill['vote_absent']:
                vote_record.append(2)
            else:
                vote_record.append(-1)
        df[bill['bill']] = vote_record
    print(df.head(10))
    timestamp = time.strftime('%d')
    df.to_csv(os.path.join("data", house+timestamp+"_voting_records.csv"))

def end_condition(current_bill):
	if current_bill > 20:
		return True
	else:
		return False
	
def run_main():
	current_bill = 1
	last_page = False
	base = "https://le.utah.gov/DynaBill/svotes.jsp?sessionid=2017GS&voteid="
	end = "&house="
	votes = []
	full_r_list = []
	while not last_page:
		print('.', end='')
		representatives, info, content_size = get_next_page(current_bill, 'H')
		if len(full_r_list) == 0:
			full_r_list = representatives
		bill_name, yeas, nays, absent = filter_bill_info(info)
		if bill_name and yeas and nays:
			#print(current_bill, ': ', bill_name, ': \nYeas: ', yeas, '\nNays: ', nays, '\nAbsent: ', absent)
			v_yeas, v_nays, v_absents = get_vote_names(yeas, nays, absent, representatives)
			votes.append({'bill': bill_name, 'yeas': yeas, 'nays': nays, 'absent': absent, 'vote_yea': v_yeas,
						  'vote_nay': v_nays, 'vote_absent': v_absents})
		if content_size < 10: # or end_condition(current_bill)
			last_page = True
		else:
			current_bill += 1
	make_df(full_r_list, votes, 'congress')