import dataclasses
import datetime
import json


def default_json_encoder(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    raise TypeError("Type %s not serializable" % type(o))


def json_dump(arr, indent=2):
    for o in arr:
        print(json.dumps(
            dataclasses.asdict(o) if dataclasses.asdict(o) else o,
            default=default_json_encoder,
            indent=indent
        ))
