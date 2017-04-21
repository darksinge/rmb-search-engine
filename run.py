"""
Script to implement all of the code needed to maintain the data on the server, should run and update data regularly,
without overloading the legislation website.
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
    # things that must be done:
    # scrape votes (it's very quick, so it should be fine)
    vote_scraper.vote_scrape()
    # scrape bills
    async_bill_scrape.bill_scrape()
    offline_bill_scrape.get_files()
    # bill data analysis
    bill_data_analysis.start_analysis()
    # create sparse matrix
    create_sparse_matrix.make_pickle()
    # update the search server
    configs.searching.refresh_matrix()


def main():
    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)
    job = scheduler.add_job(scrape, 'interval', hours=24)
    scheduler.start()
    search_server.run_server()


if __name__ == '__main__':
    main()