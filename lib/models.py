import dataclasses
import datetime


@dataclasses.dataclass(frozen=True)
class SimpleProcessData:
    process_class: str = dataclasses.field()
    process_class_abv: str = dataclasses.field()
    process_number: str = dataclasses.field()
    subject: str = dataclasses.field()
    plaintiff: str = dataclasses.field()
    defendant: str = dataclasses.field()
    status: str = dataclasses.field()
    last_update: datetime.datetime = dataclasses.field()
