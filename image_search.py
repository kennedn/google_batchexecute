#!/usr/bin/env python3
from bs4 import BeautifulSoup
import json
import argparse
from urllib.parse import urlencode, quote, unquote
import requests
from datetime import datetime
import re
import pdb

params = None

def debug(*args, **kwargs):
  if params.debug:
    print(*args, **kwargs)

def log(*args, **kwargs):
  if not params.debug:
    print(*args, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape urls from google images')
    parser.add_argument('-s', '--search', type=str, metavar='term', nargs='?', const=False, default='monkey',
                        help='Image search term(s)')
    parser.add_argument('-p', '--page_num', type=int, default=1, help='Iterations of batch execute')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug logging instead of usual')
    params = parser.parse_args()

    query_args = urlencode(
      {
        'q': params.search,
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
    for i in range(params.page_num):
      grid_state = af_initdatacallback[31][0][12][11]
      search_query = af_dataservicerequests[28]
      nonce1 = af_initdatacallback[31][0][12][16][3]
      nonce2 = af_initdatacallback[31][0][12][16][4]
      debug(json.dumps({
          "grid_state": f"{grid_state}",
          "nonce1": f"{nonce1}",
          "nonce2": f"{nonce2}" 
        }
      ))

      f_req = f"""[[["HoAMBc","[null,null,{grid_state},null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,{search_query},null,null,null,null,null,null,null,null,[null,\\"{nonce1}\\",\\"{nonce2}\\"],null,false]",null,"generic"]]]"""
      f_req = f_req.replace('None', 'null').replace(' ', '').replace("\'", '\\"')

      query_args = {
          'rpcids': 'HoAMBc',
          'source-path': '/search',
          'f.sid': wiz_global_data['FdrFJe'],
          'bl': wiz_global_data['cfb2h'],
          'hl': 'en-US',
          '_reqid': 1 + (3600 * now.hour + 60 * now.minute + now.second) + (100000 * i),
          'f.req': f_req
      }
      debug(json.dumps(query_args, indent=2))
      query_args = urlencode(query_args)
      headers = {
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Origin': 'https://www.google.com',
        'Referer': 'https://www.google.com/',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0'
      }
      query_url = f"https://www.google.com/_/VisualFrontendUi/data/batchexecute?{query_args}"
      resp = requests.post(query_url, headers=headers)
      resp = json.loads(re.search('.*(\[\["wrb.fr".*$)', resp.text).group(1))
      af_initdatacallback = json.loads(resp[0][2])
    
    image_results = af_initdatacallback[31][0][12][2]
    for i, image in enumerate(image_results):
        try:
          log(json.dumps({
              'title': image[1][9]['2003'][3],
              'url': image[1][3][0],
              'href': image[1][9]['2003'][2]
            }, indent=2
          ))
        except:
          pass
