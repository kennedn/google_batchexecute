# Initial page load

Several 'sources' within the HTML body must be scraped to collect required parameters for a call to batchexecute:

- WIZ_global_data
- AF_initDataCallback
- AF_dataServiceRequests

## URL parameters

|param|source|value / param name|description|
|------|-----|-----|-------|
|rpcids|`hardcoded`|HoAMBc|Function call name|
|bih|`hardcoded`|1080| Browser window height (effects grid_state)|
|biw|`hardcoded`|1920| Browser window width (effects grid_state)|
|source-path| `hardcoded` | %2fsearch| Request subdirectory
|f.sid |`WIZ_global_data`|FdrFJe|Signed 64 bit int, possible XSRF deterrent|
|bl|`WIZ_global_data`|cfb2h|endpoint version / server instance name?
|hl|`hardcoded`|en|Region code
|authuser|`hardcoded`|0|Based on logged in user, no value set when not logged in
|_reqid|`calculated`|181562| 1 + seconds since midnight + (100000 * page number)
|rt|`hardcoded`|c| c = normal response, b = protobuf, omit for json


## Data parameters

### f_req

```
[[["HoAMBc","[null,null,{grid_state},null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,{search_query},null,null,null,null,null,null,null,null,{nonce},null,false]",null,"generic"]]]
```

|name|index|source|value_index|description|
|-|-----|------|-----------|-----------|
|N/A|[0][0][0]|`hardcoded`|HoAMBc|Function call name|
|grid_state|[0][0][1][2]|`AF_initDataCallback`|[31][0][12][11]|Grid state, references one or more image results, result dimensions and screen dimensions, this seems to be used to calculate the offset of returned results|
|search_query|[0][0][1][29]|`AF_dataServiceRequests`|['ds:1']['request'][28]|Search query and region code|
|nonce|[0][0][1][38]|`AF_initDataCallback`|[31][0][12][16][3:]|Nonce values, base64 encoded, inc/decrements each call, [31][0][12][16][3] = 0x0802 + call count, [31][0][12][16][4] = 0x18d0012000 - (0x17ff0000 * call count) |

### at
|param|source|value / param name|description|
|------|-----|-----|-------|
|at|`WIZ_global_data`|SNlM0e|XSRF deterrent? Doesn't seem to be required|

# Subsequent requests

Additional requests require that `grid_state` and `nonce` values are updated. Values can be extracted from response data which echos data found in `AF_initDataCallback`, dig down to [0][2]. Indexes referenced in f_req section can then be used to get new `grid_state` and `nonce`.