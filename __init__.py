import json
import requests
import sys

from flask import Flask, request, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

#configs = ['fastfood.json']
configs = [
          'consumer_durables.json',
          'fmcg.json',
          'fastfood.json',
          'electronics.json',
          'auto_4w.json',
          'auto_2w.json',
          'auto_ancilary.json',
          'tyres.json',
          'building_materials.json',
          'roofing.json',
          'utilities.json',
          'chemicals.json',
          'midcaps.json',
          'niche.json'
          ]
data = []
SALES_NUMBERS_POS = (14,17,20,23)
PROFIT_NUMBERS_POS = (122,125,128,131)
count=0

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


def extract_qtr_numbers(soup, result_type='tblQtyCons'):
    qtr_sales_growth = []
    qtr_profit_growth = []
    for i in SALES_NUMBERS_POS:
        qtr_sales_growth.append(soup.find("table", {"id": result_type}).find_all("div",{"class":"float-lt in-tab-col2-2"})[i].contents[0].strip())
    for j in PROFIT_NUMBERS_POS:
        qtr_profit_growth.append(soup.find("table", {"id": result_type}).find_all("div",{"class":"float-lt in-tab-col2-2"})[j].contents[0].strip())

    if len(set(qtr_sales_growth)) == 1:
        # return is used to break out of the recursion.
        # else the main function returns twice - onec from inside and then outside
        return extract_qtr_numbers(soup, 'tblQtyStd')

    return tuple(qtr_sales_growth), tuple(qtr_profit_growth)

#*************************  MAIN  ************************  #

for config in configs:
    url_mappings = json.loads(open('conf/' + config).read())

    industry = []
    for scrip, url in url_mappings.items():
        count+=1
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
        promoter=soup.findAll("div", {"class": "float-lt com-mid-share-tab2"})[0].contents[1].contents[1].get_text().strip()
        debt=soup.findAll("div", {"class": "in-tab-col bg-white"})[-1].contents[3].contents[1].contents[0].strip()

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
                       qtr_profit_growth=qtr_profit_growth,
                       promoter=promoter,
                       debt=debt
                       )
        industry.append(an_item)
    data.append(industry)


@app.route('/')
def hello():
    #return render_template('index.html', fmcg=fmcg)
    return render_template('index.html', data=data, count=count)
