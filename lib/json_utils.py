import datetime


def default_json_encoder(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    raise TypeError("Type %s not serializable" % type(o))
