import {onlyDigits} from "@/lib/format-utils.ts";

export type QueryStatus = 'queued' | 'running' | 'done' | 'failed';
export type QueryType = 'cpf' | 'process';
export type LiteralDocumentType = 'cpf' | 'oab' | 'cnpj' | 'unknown';

export interface ProcessData {
  process_number: string;
  judicial_class: string;
  judge_entity: string;
  referenced_process_number: string;
  subject: string;
  collegiate_judge_entity?: string | null;
  accessment_date?: string | null; // ISO datetime
  judge?: string | null;
  distribution_date?: string | null; // ISO date
  jurisdiction?: string | null;
}

export interface DocumentParty {
  type: LiteralDocumentType;
  value: string;
}

export interface Party {
  name: string;
  role: string | null;
  documents: DocumentParty[];
}

export interface CaseParty {
  active: Party[];
  passive: Party[];
}

export interface MovementAttachment {
  document_ref?: string | null;
  document_date?: string | null;
}

export interface Movement {
  created_at: string;
  description: string;
  attachments: MovementAttachment[];
}

export interface Attachment {
  created_at?: string | null; // ISO datetime
  description: string;
  file_b64?: string | null;
  file_md5?: string | null;
  protocol_b64?: string | null;
  protocol_md5?: string | null;
}

export interface ProcessJson {
  process: ProcessData;
  case_parties: CaseParty;
  movements: Movement[];
  attachments: Attachment[];
}

export interface DetailedProcess {
  process_number: string;
  raw_json: string;

  process(): ProcessJson;

  tribunal(): string;

  cpf(): string;

  name(): string;

  subject(): string;

  formated_process_number(): string;

}

export class DetailedProcessImpl implements DetailedProcess {
  process_number: string;
  raw_json: string;
  _parsed: ProcessJson;

  constructor(d: DetailedProcess) {
    this.process_number = d.process_number;
    this.raw_json = d.raw_json;
    this._parsed = JSON.parse(d.raw_json);
  }

  process(): ProcessJson {
    return this._parsed;
  }

  tribunal(): string {
    return `TRF${parseInt(onlyDigits(this.process_number).substring(14, 16))}`;
  }

  cpf(): string {
    return this._parsed.case_parties.active[0].documents[0].value;
  }

  subject(): string {
    return this._parsed.process.subject;
  }

  name(): string {
    return this._parsed.case_parties.active[0].name;
  }

  formated_process_number(): string {
    return this._parsed.process.process_number;
  }

}

export interface Query {
  id: number;
  query_type: QueryType;
  query_value: string;
  status: QueryStatus;
  result_process_count: number;
  processes: DetailedProcess[];
}

export class QueryImpl implements Query {
  id: number;
  processes: DetailedProcess[];
  query_type: QueryType;
  query_value: string;
  result_process_count: number;
  status: QueryStatus;

  constructor(q: Query) {
    this.id = q.id;
    this.processes = q.processes.map(it => new DetailedProcessImpl(it));
    this.query_type = q.query_type;
    this.query_value = q.query_value;
    this.result_process_count = q.result_process_count;
    this.status = q.status;
  }
}