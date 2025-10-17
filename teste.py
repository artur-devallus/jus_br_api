import time

import requests

host_dev = 'http://127.0.0.1:8000'
host_prod = 'http://151.243.218.157:8080'

queries = [
    234, 228, 227, 226, 225, 224, 223, 222, 220, 217, 216, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204,
    203, 202, 200, 199, 198, 195, 194, 193, 192, 191, 190, 188, 184, 182, 181, 180, 179, 178, 177, 176, 175, 173, 172,
    169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159, 158, 157, 155, 154, 150, 149, 148, 147, 145, 141, 140, 139,
    137, 135, 134, 133, 132, 131, 130, 129, 128, 127, 125, 124, 123, 122, 121
]
last = host_dev
for query_id in queries:
    res = requests.post(
        f'{last}/v1/queries/{query_id}/enqueue',
        json=dict(
            force=False
        ),
        headers=dict(
            Authorization='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzYwNzQ1NjAwfQ.GFnPhERpWUVM700y2hD1Z3kjtBZSgrgiYmEoMkQCtnk'
        )
    )
    print(res.url)
    if last == host_dev:
        last = host_prod
    else:
        last = host_dev
    time.sleep(10)
