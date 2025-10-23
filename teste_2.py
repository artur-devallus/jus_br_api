import dataclasses
import json
import os

from lib.exceptions import LibJusBrException
from lib.json_utils import default_json_encoder
from lib.pje.service import get_trf3_service
from lib.webdriver.driver import new_driver

data = [
    {
        "id": 122,
        "query_value": "03446903852"
    },
    {
        "id": 125,
        "query_value": "83364358834"
    },
    {
        "id": 129,
        "query_value": "13700504888"
    },
    {
        "id": 130,
        "query_value": "13093945801"
    },
    {
        "id": 131,
        "query_value": "06759335872"
    },
    {
        "id": 132,
        "query_value": "15960851857"
    },
    {
        "id": 133,
        "query_value": "15155321867"
    },
    {
        "id": 134,
        "query_value": "26060804837"
    },
    {
        "id": 135,
        "query_value": "29220312840"
    },
    {
        "id": 137,
        "query_value": "15519043817"
    },
    {
        "id": 139,
        "query_value": "20733780806"
    },
    {
        "id": 140,
        "query_value": "05204453849"
    },
    {
        "id": 141,
        "query_value": "31699528896"
    },
    {
        "id": 145,
        "query_value": "79681441834"
    },
    {
        "id": 147,
        "query_value": "11734689862"
    },
    {
        "id": 148,
        "query_value": "31913927857"
    },
    {
        "id": 149,
        "query_value": "22719942847"
    },
    {
        "id": 150,
        "query_value": "15842951800"
    },
    {
        "id": 154,
        "query_value": "29156185855"
    },
    {
        "id": 155,
        "query_value": "01924751852"
    },
    {
        "id": 157,
        "query_value": "10930702859"
    },
    {
        "id": 159,
        "query_value": "09840326813"
    },
    {
        "id": 160,
        "query_value": "13692389833"
    },
    {
        "id": 161,
        "query_value": "03851636813"
    },
    {
        "id": 162,
        "query_value": "04247502875"
    },
    {
        "id": 163,
        "query_value": "02598470702"
    },
    {
        "id": 165,
        "query_value": "08899262802"
    },
    {
        "id": 166,
        "query_value": "06654613805"
    },
    {
        "id": 167,
        "query_value": "01782715860"
    },
    {
        "id": 168,
        "query_value": "88761118834"
    },
    {
        "id": 169,
        "query_value": "25309566856"
    },
    {
        "id": 172,
        "query_value": "16240454800"
    },
    {
        "id": 173,
        "query_value": "37617298803"
    },
    {
        "id": 175,
        "query_value": "23431196861"
    },
    {
        "id": 176,
        "query_value": "04583755864"
    },
    {
        "id": 177,
        "query_value": "01176905899"
    },
    {
        "id": 178,
        "query_value": "11736190890"
    },
    {
        "id": 179,
        "query_value": "26515292813"
    },
    {
        "id": 180,
        "query_value": "09775759854"
    },
    {
        "id": 181,
        "query_value": "03897121832"
    },
    {
        "id": 209,
        "query_value": "00432674837"
    }
]
jsons = [x for x in os.listdir() if x.endswith('.json')]
with new_driver() as driver:
    service = get_trf3_service(
        driver
    )

    for o in data:
        query_id, query_value = o.values()
        if any([x.split('_')[0] == str(query_id) for x in jsons]):
            print(
                f'already finished for query_id={query_id} query_value={query_value}'
            )
            continue
        try:
            processes = service.get_detailed_processes(query_value)
        except LibJusBrException as ex:
            print(f'error on query_id={query_id} query_value={query_value}: {ex.message}')
            continue

        for p in processes:
            with open(f'{query_id}_{query_value}_{p.process.process_number}.json', 'w') as f:
                json.dump(dataclasses.asdict(p), f, default=default_json_encoder, indent=2)

            print(
                f'finished for query_id={query_id} query_value={query_value} process_number={p.process.process_number}'
            )
