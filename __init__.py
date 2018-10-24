import requests

from flask import Flask, request, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

resp = requests.get('http://www.ratestar.in/company/asianpaint/500820/Asian-Paints-Ltd-100820')
soup = BeautifulSoup(resp.text, 'lxml')

#soup.find("span", {"id":"lblMCap"})
#soup.find("span", {"id":"lblStockPE"})

fmcg = []
an_item = dict(scrip="Asian Paints", 
               market_cap=soup.find("span", {"id":"lblMCap"}).contents[0], 
               price_to_earnings=soup.find("span", {"id":"lblStockPE"}).contents[0], 
               price_to_sales=0, 
               peg=0)
fmcg.append(an_item)


@app.route('/')
def hello():
    return render_template('index.html', fmcg=fmcg)
