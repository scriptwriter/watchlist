import json
import requests
import sys

from flask import Flask, request, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)


configs = [
          'consumer_durables.json',
          'fmcg.json',
          'auto_4w.json',
          'auto_2w.json',
          'niche.json'
          ]
data = []
SALES_NUMBERS_POS = (14,17,20,23)
PROFIT_NUMBERS_POS = (122,125,128,131)

def extract_label_val(label):
    if label=='lblDivYeild':
        try:
            return soup.find("span", {"id":label}).contents[0]
        except:
            return '-'
    else:
        try:
            return round(float(soup.find("span", {"id":label}).contents[0].strip().replace(',', '')))
        except:
            return '-'


def find_drop(current_price, year_high, year_low):
    from_year_high = from_year_low = 0

    diff_from_year_high = year_high - current_price
    diff_from_year_low = current_price - year_low
    from_year_high = round(diff_from_year_high * 100 / year_high)
    from_year_low = round(diff_from_year_low * 100 / year_low)

    from_year_high = '52w HIGH' if from_year_high <= 2 else '-'+str(from_year_high)+'%'
    from_year_low = '52w LOW' if from_year_low <= 2 else '+'+str(from_year_low)+'%'

    return from_year_high, from_year_low


def load_url_mappings(filename):
    return json.loads(open(filename).read())


def extract_qtr_numbers(soup):
    qtr_sales_growth = []
    qtr_profit_growth = []
    for i in SALES_NUMBERS_POS:
        qtr_sales_growth.append(soup.find("table", {"id": "tblQtyCons"}).find_all("div",{"class":"float-lt in-tab-col2-2"})[i].contents[0].strip())
    for j in PROFIT_NUMBERS_POS:
        qtr_profit_growth.append(soup.find("table", {"id": "tblQtyCons"}).find_all("div",{"class":"float-lt in-tab-col2-2"})[j].contents[0].strip())
    return tuple(qtr_sales_growth), tuple(qtr_profit_growth)

#*************************  MAIN  ************************  #

for config in configs:
    url_mappings = json.loads(open('conf/' + config).read())

    industry = []
    for scrip, url in url_mappings.items():
        #print(scrip)
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')

        scrip=scrip
        market_cap=extract_label_val('lblMCap')
        current_price=extract_label_val('lblLTP') 
        year_high=extract_label_val('lblwHigh')
        year_low=extract_label_val('lblwLow')
        from_year_high, from_year_low=find_drop(current_price, year_high, year_low)
        price_to_earnings=extract_label_val('lblStockPE') 
        price_to_earnings_8=extract_label_val('lblPEAvg8')
        price_to_earnings_5=extract_label_val('lblPEAvg5')
        price_to_earnings_3=extract_label_val('lblPEAvg3')
        dividend=extract_label_val('lblDivYeild')
        qtr_sales_growth, qtr_profit_growth = extract_qtr_numbers(soup)

        an_item = dict(scrip=scrip,
                       market_cap=market_cap,
                       current_price=current_price,
                       from_year_high=from_year_high,
                       from_year_low=from_year_low,
                       price_to_earnings=price_to_earnings,
                       price_to_earnings_8=price_to_earnings_8,
                       price_to_earnings_5=price_to_earnings_5,
                       price_to_earnings_3=price_to_earnings_3,
                       dividend=dividend,
                       qtr_sales_growth=qtr_sales_growth,
                       qtr_profit_growth=qtr_profit_growth
                       )
        industry.append(an_item)
    data.append(industry)


@app.route('/')
def hello():
    #return render_template('index.html', fmcg=fmcg)
    return render_template('index.html', data=data)
