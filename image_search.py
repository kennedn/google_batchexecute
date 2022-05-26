#!/usr/bin/env python3
from bs4 import BeautifulSoup
import json
import argparse
import requests
from urllib.parse import urlencode, quote, unquote
from datetime import datetime
import re

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape urls from google images')
    parser.add_argument('-s', '--search', type=str, metavar='term', nargs='?', const=False, default='monkey',
                        help='Image search term(s)')
    args = parser.parse_args()

    query_args = urlencode(
      {
        'q': args.search,
        'tbm': 'isch',
        'bih': 1080,
        'biw': 1920  
      }
    )
    query_url = f"https://google.com/search?{query_args}"
    headers = {
      'Accept-Language': 'en-GB,en;q=0.5',
      'Accept': '*/*',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
      'Origin': 'https://www.google.co.uk',
      'Referer': 'https://www.google.co.uk/',
      'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0'
    }
    resp = requests.get(query_url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    scripts = soup.find_all('script')
    wiz_global_data = next(s for s in scripts if re.match('window.WIZ_global_data\s*=', s.get_text()))
    wiz_global_data = json.loads(re.search('window.WIZ_global_data\s*=\s*(\{.*?\});', wiz_global_data.get_text()).group(1))
    af_initdatacallback = next(s for s in scripts if re.match("AF_initDataCallback\({key: 'ds:1', hash: '2',", s.get_text()))
    af_initdatacallback = json.loads(re.search("AF_initDataCallback\({key: 'ds:1', hash: '2', data:(\[.*\]),.*?;$", af_initdatacallback.get_text()).group(1))
    af_dataservicerequests = next(s for s in scripts if re.match(".*AF_dataServiceRequests = {'ds:0'.*?'ds:1'", s.get_text()))
    af_dataservicerequests = json.loads(re.search(".*AF_dataServiceRequests = {'ds:0'.*?'ds:1'\s*:\s*\{.*,request:(\[.*\])}", af_dataservicerequests.get_text()).group(1))

    now = datetime.now()
    query_args = urlencode(
        {
          'rpcids': 'HoAMBc',
          'source-path': '/search',
          'f.sid': wiz_global_data['FdrFJe'],
          'bl': wiz_global_data['cfb2h'],
          'hl': 'en',
          'authuser': '',
          '_reqid': 1 + (3600 * now.hour + 60 * now.minute + now.second) + (100000 * 1),
        }
      )
    grid_state = af_initdatacallback[31][0][12][11]
    search_query = af_dataservicerequests[28]
    nonce = af_initdatacallback[31][0][12][16][3:]
    f_req = f"""[[["HoAMBc","[null,null,{grid_state},null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,{search_query},null,null,null,null,null,null,null,null,{nonce},null,false]",null,"generic"]]]"""
    f_req = f_req.replace('None', 'null').replace(' ', '').replace("\'", '\\"').replace('\n', '')
    f_req = quote(f_req)

    data = f'f.req={f_req}'
    headers = {
      # 'Accept-Language': 'en-GB,en;q=0.5',
      # 'Accept': '*/*',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
      # 'Origin': 'https://www.google.co.uk',
      # 'Referer': 'https://www.google.co.uk/',
      'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0'
    }

    query_url = f"https://www.google.co.uk/_/VisualFrontendUi/data/batchexecute?{query_args}"
    resp = requests.post(query_url, headers=headers, data=data)
    resp = json.loads(re.search('.*(\[\["wrb.fr".*$)', resp.text).group(1))
    af_initdatacallback = json.loads(resp[0][2])
    


    

