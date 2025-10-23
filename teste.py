import time

import requests

host_dev = 'http://127.0.0.1:8000'
host_prod = 'http://151.243.218.157:8080'

queries = [
    122, 125, 129, 130, 131, 132, 133, 134, 135, 137, 139, 140, 141, 145, 147, 148, 149, 150, 154, 155, 157, 158, 159,
    160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 172, 173, 175, 176, 177, 178, 179, 180, 181, 209
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
    time.sleep(20)
