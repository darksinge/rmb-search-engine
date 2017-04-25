"""
Script to implement all of the code needed to maintain the data on the server, should run and update data regularly,
without overloading the legislation website.

Not ready to be implemented yet
"""
import async_bill_scrape
import bill_data_analysis
import offline_bill_scrape
import create_sparse_matrix
import search_server
import vote_scraper
import configs
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc


def scrape():
    # TODO: Finish respective functions before fully implementing
    # vote_scraper.vote_scrape()
    # async_bill_scrape.bill_scrape()
    # offline_bill_scrape.get_files()
    #offline_bill_scrape.extract_files()
    # bill_data_analysis.start_analysis()
    create_sparse_matrix.make_pickle()
    # configs.searching.refresh_matrix()


def main():
    """
    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)
    scheduler.add_job(scrape, 'interval', hours=24)
    scheduler.start()
    search_server.run_server()
    """
    scrape()


if __name__ == '__main__':
    main()