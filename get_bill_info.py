"""
@author: Bradley Robinson

Contains code to get information about the bills for the search engine
"""
import pickle
import os


class BillInfo(object):
    def __init__(self):
        self.bill_dict = pickle.load(open(os.path.join("analysis", "bill_information.pickle"), 'rb'))

    def get_all_info_(self, year, bill):
        try:
            current_bill = self.bill_dict[(str(year), bill)]
            return current_bill
        except KeyError:
            return "Unable to find bill"

    def get_detailed_info(self, year, bill):
        return self.get_all_info_(year, bill)

    def get_summary(self, year, bill):
        current_bill = self.get_all_info_(year, bill)
        if type(current_bill) is dict:
            #del current_bill['description']
            pass
        return current_bill

    def get_all_bills(self, year):
        all_bills = []
        for key, info in self.bill_dict.items():
            all_bills.append(info)
        return all_bills


def test():
    bill = BillInfo()
    print(bill.get_all_bills('2017'))

if __name__ == '__main__':
    test()