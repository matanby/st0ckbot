import sys
from collections import namedtuple

import requests
from bs4 import BeautifulSoup
from errbot import BotPlugin, botcmd

import config


class St0ckBot(BotPlugin):
    FundStatus = namedtuple('FundStatus', 'name change_day change_month change_year')

    BASE_URL = 'http://www.funder.co.il/fund.aspx?id='

    @botcmd(template='fund_status')
    def fetch(self, msg, args):
        try:
            fund_id = int(str(msg).split()[-1])
            fund_ids = [fund_id]
        except:
            fund_ids = config.DEFAULT_FUND_IDS

        return {'items': self.fetch_funds_changes(fund_ids)}

    @staticmethod
    def fetch_funds_changes(fund_ids):
        from multiprocessing.pool import ThreadPool
        pool = ThreadPool(processes=10)
        async_results = [pool.apply_async(St0ckBot.fetch_fund_changes, (fund_id,)) for fund_id in fund_ids]
        results = [res.get() for res in async_results]

        return results

    @staticmethod
    def fetch_fund_changes(fund_id):
        url = St0ckBot.BASE_URL + str(fund_id)

        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')

        name = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_fundName'}).text.strip()
        change_day = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_day1'}).text.strip()
        change_month = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_monthB'}).text.strip()
        change_year = soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_yearB'}).text.strip()

        norm = lambda x: x[1:] + '-' if x.startswith('-') else x + '+'
        change_day = norm(change_day)
        change_month = norm(change_month)
        change_year = norm(change_year)

        return St0ckBot.FundStatus(
            name=name,
            change_day=change_day,
            change_month=change_month,
            change_year=change_year
        )


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s FUND_ID' % sys.argv[0])
        exit(1)

    fund_id = sys.argv[1]
    print(St0ckBot.fetch_fund_changes(fund_id))
