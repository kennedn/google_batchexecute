# Installing reference script

```
python3 -m pip install -r requirements.txt
python3 image_search.py
```

## Usage

```
Scrape urls from google images, with working pagination

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Display request debug information instead of results
  -s [term], --search [term]
                        Image search term(s)
  -p PAGE_NUM, --page_num PAGE_NUM
                        Page number to request
```

# Batchexecute documentation

## Initial image search

### URL
`https://google.com/search`

### Headers

|Header|Value|Reason|
|------|-----|------|
|Content-Type|application/x-www-form-urlencoded;charset=UTF-8|Request payload is a 'JSON-like' string and must be sent as a urlencoded parameter|
|User-Agent|Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0| Google determines whether to enable javascript based on this header, Javascript must be enabled to scrape the required parameters from the HTML body. Any modern user-agent string should work

### Params

|Param|Example Value|Description|
|-----|-------------|-----------|
|q    |monkey       |search query|
|tbm  |isch         |search function, `isch` = image search|

### Notes

Screen width can be set with the param `biw`. This will eventually end up as a parameter for batchexecute calls but does not seem to affect returned results.

## Calling batchexecute

Several 'sources' within the HTML body of the initial image search must be scraped to collect required parameters for a call to batchexecute:

- WIZ_global_data
- AF_initDataCallback
- AF_dataServiceRequests

Refer to the reference script (image_search.py) for details on how to scrape the listed information sources into useable python objects

### URL
`https://www.google.com/_/VisualFrontendUi/data/batchexecute`

### Headers

|Header|Value|Reason|
|------|-----|------|
|Content-Type|application/x-www-form-urlencoded;charset=UTF-8|Request payload is a 'JSON-like' string and must be sent as a urlencoded parameter|
|User-Agent|Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0| Google determines whether to enable javascript based on this header, Javascript must be enabled to scrape the required parameters from the HTML body. Any modern user-agent string should work
## Parameters

|Param|Source|Example value/index|description|
|------|-----|-----|-------|
|rpcids|hardcoded|HoAMBc|Function call name `HoAMBc` = image search|
|source-path| hardcoded | /search| Request subdirectory
|f.sid |`WIZ_global_data`|`FdrFJe`|Signed 64 bit int, possible XSRF deterrent|
|bl|`WIZ_global_data`|`cfb2h`|endpoint version / server instance name?
|hl|`WIZ_global_data`|`GWsdKe`|Region code
|authuser|`hardcoded`|`Unset`|Based on logged in user, no value set when not logged in
|_reqid|`calculated`|181562| 1 + seconds since midnight + (100000 * page number)
|rt|`hardcoded`|`Unset`| c = normal response, b = protobuf, omit for easier to parse json response
|f.req|`calculated`| See [f.req](#f.req) section|batchexecute function parameters


### f.req

The f.req parameter contains the data required for the batchexecute endpoint to return a set of image results. It is purposfully obfuscated to make its construction unclear, despite looking like a JSON object it is in fact a string and must be  treated as such. The following template shows a paramaterised version of the data: 

> ```[[["HoAMBc","[null,null,{grid_state},null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,{search_query},null,null,null,null,null,null,null,null,[null,\\"{page_number_nonce}\\",\\"{countdown_nonce}\\"],null,false]",null,"generic"]]]```

|Param|Source|Index|Description|
|-----|------|-----|-----------|
|grid_state|`AF_initDataCallback`|`[31][0][12][11]`|references zero or more image results, result dimensions and screen dimensions, does not seem to directly affect returned results|
|search_query|`AF_dataServiceRequests`|`[28]`|search query
|page_number_nonce|`AF_initDataCallback`|`[31][0][12][16][3]`|Obfuscated page number, a base64 encoded integer that determines which page number to return results for, incremented on each subsequent call to batchexecute
|countdown_nonce|`AF_initDataCallback`|`[31][0][12][16][4]`|Unknown obfuscated number, decrements on each subsequent call to batchexecute. Does not appear to affect returned results and can be left at initial value

## Subsequent requests

The intended use of the batchexecute function call is to incrementally make subsequent calls to batchexecute as the user scrolls down the page so that new images can be loaded in dynamically on the infinite scroll. This can be imitated by taking the following steps:

- Perform the call outlined in [Calling batchexecute](#Calling-batchexecute)
- Convert the returned data into a python object (refer to image_search.py) and infer a new AF_initDataCallback object from `returned_data[0][2]`
- Extract new variables `grid_state`, `page_number_nonce` and `countdown_nonce` from the object, and build a new `f.req` parameter
- Repeat the call with the newly constructed `f.req` parameter in [Calling batchexecute](#Calling-batchexecute)

However, the only variables that change between calls are `page_number_nonce` and `countdown_nonce` and luckily for us the offset values for these can be calculated! This means that we can skip making subsequent calls and skip right to the page number we want. Refer to `image_search.py` on how to convert these values to integers and back.

### Offset formulas

### page_number_nonce

> ```page_number_nonce_offset = b64encode((int.from_bytes(b64decode(page_number_nonce), "big") + page_number).to_bytes(2, "big")).decode('utf-8')```

> #### Description : Base64 decode the nonce and then cast to an integer. Increment value by the desired page number. Cast back to bytes and re-encode to base64

### Countdown_nonce

> ```countdown_nonce_offset = af_initdatacallback[31][0][12][16][4] if page_number ==  0 else b64encode(max(0,(106568949760 - (page_number * 402587648))).to_bytes(5, "big")).decode('utf-8')```

> #### Description : If this is the first page number, just infer the nonce from AF_InitDataCallback, else take the first nonce returned from batchexecute (always 'GNABIAA=' which converts to 106568949760`) and decrement by the page_number * 402587648 (this seems to be a constant decrement value for subsequent calls)

#### Note:
`countdown_nonce` is not required for the call to succeed and return desired image results, it can actually be left at its initial value (`af_initdatacallback[31][0][12][16][4]`). `page_number_nonce` however is required.

## Acknowledgments 

Deciphering this endpoint would not have been possible without the work of some other noteworthy people:

[Ryan Kovatch](https://kovatch.medium.com/deciphering-google-batchexecute-74991e4e446c) - For deciphering a lot of common parameters in the batchexecute endpoint and documenting their use

[FOAF-lambda](https://blog.csdn.net/lwdfzr/article/details/124805045) - For creating a reference script that gave me a solid start in deciphering the HoAMBc varient of  the batchexecute endpoint