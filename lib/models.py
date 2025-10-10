import dataclasses
import datetime
from typing import List, Literal


@dataclasses.dataclass(frozen=True)
class SimpleProcessData:
    process_class: str | None = dataclasses.field()
    process_class_abv: str | None = dataclasses.field()
    process_number: str = dataclasses.field()
    subject: str = dataclasses.field()
    plaintiff: str = dataclasses.field()
    defendant: str = dataclasses.field()
    status: str | None = dataclasses.field()
    last_update: datetime.datetime | None = dataclasses.field()


@dataclasses.dataclass(frozen=True)
class ProcessData:
    process_number: str = dataclasses.field()
    distribution_date: datetime.date = dataclasses.field()
    jurisdiction: str = dataclasses.field()
    judicial_class: str = dataclasses.field()
    judge_entity: str = dataclasses.field()
    collegiate_judge_entity: str = dataclasses.field()
    referenced_process_number: str = dataclasses.field()
    subject: str = dataclasses.field()


@dataclasses.dataclass(frozen=True)
class DocumentParty:
    type: Literal['cpf'] | Literal['oab'] | Literal['cnpj'] = dataclasses.field()
    value: str = dataclasses.field()

    @staticmethod
    def of_cpf(cpf):
        return DocumentParty(type='cpf', value=str(cpf))

    @staticmethod
    def of_cnpj(cnpj):
        return DocumentParty(type='cnpj', value=str(cnpj))

    @staticmethod
    def of_oab(oab):
        return DocumentParty(type='oab', value=str(oab))


@dataclasses.dataclass(frozen=True)
class Party:
    name: str = dataclasses.field()
    role: str = dataclasses.field()
    documents: List[DocumentParty] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class CaseParty:
    active: List[Party] = dataclasses.field(default_factory=list)
    passive: List[Party] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class Movement:
    created_at: datetime.datetime = dataclasses.field()
    description: str = dataclasses.field()
    document_ref: str | None = dataclasses.field(default=None)
    document_date: datetime.datetime | None = dataclasses.field(default=None)


@dataclasses.dataclass(frozen=True)
class Attachment:
    created_at: datetime.datetime = dataclasses.field()
    description: str = dataclasses.field()
    file_b64: str | None = dataclasses.field()
    protocol_b64: str | None = dataclasses.field()


@dataclasses.dataclass(frozen=True)
class DetailedProcessData:
    process: ProcessData = dataclasses.field()
    case_parties: CaseParty = dataclasses.field()
    movements: List[Movement] = dataclasses.field(default_factory=list)
    attachments: List[Attachment] = dataclasses.field(default_factory=list)
