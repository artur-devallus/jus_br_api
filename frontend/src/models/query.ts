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
  attachments?: Attachment[];
}

export interface DetailedProcess {
  process_number: string;
  raw_json: string;

  process(): ProcessJson;

  tribunal(): string;

  distributionDate(): string;

  activePartyAuthorCpf(): string;

  activePartyAuthorName(): string;

  activePartyLawyerCpf(): string;

  activePartyLawyerName(): string;

  passivePartyDefendantCpfOrCnpj(): string;

  firstMovement(): string;

  firstMovementAt(): string;

  passivePartyDefendantName(): string;

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

  distributionDate(): string {
    return this._parsed.process.distribution_date ? new Date(this._parsed.process.distribution_date).toLocaleString("pt-BR") : '-';
  }

  subject(): string {
    return this._parsed.process.subject;
  }

  findCpf(party: Party | null): DocumentParty | null {
    return (party?.documents || []).find(it => it.type === 'cpf') || null;
  }

  findCnpj(party: Party | null): DocumentParty | null {
    return (party?.documents || []).find(it => it.type === 'cnpj') || null;
  }

  passivePartyDefendant(): Party | null {
    return this._parsed.case_parties.passive[0] || null;
  }

  activePartyAuthor(): Party | null {
    return this._parsed.case_parties.active[0] || null;
  }

  activePartyLawyer(): Party | null {
    return this._parsed.case_parties.active[1] || null;
  }

  activePartyAuthorName(): string {
    return this.activePartyAuthor()?.name || '-';
  }

  activePartyAuthorCpf(): string {
    const doc = this.findCpf(this.activePartyAuthor());
    return doc ? doc.value : 'XXX.XXX.XXX-XX'
  }

  activePartyLawyerName(): string {
    return this.activePartyLawyer()?.name || '-';
  }

  activePartyLawyerCpf(): string {
    const doc = this.findCpf(this.activePartyLawyer());
    return doc ? doc.value : 'XXX.XXX.XXX-XX'
  }

  passivePartyDefendantCpfOrCnpj(): string {
    const cpf = this.findCpf(this.passivePartyDefendant());
    const cnpj = this.findCnpj(this.passivePartyDefendant());
    return cpf ? cpf.value : cnpj ? cnpj.value : 'XXX.XXX.XXX-XX';
  }

  firstMovement(): string {
    return this._parsed.movements && this._parsed.movements.length ? this._parsed.movements[this._parsed.movements.length - 1].description : '-';
  }

  firstMovementAt(): string {
    return this._parsed.movements && this._parsed.movements.length && this._parsed.movements[this._parsed.movements.length - 1].created_at ? new Date(this._parsed.movements[this._parsed.movements.length - 1].created_at).toLocaleString('pt-BR') : '-';
  }

  passivePartyDefendantName(): string {
    return this.passivePartyDefendant()?.name || '-';
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
  created_at: string;
  processes: DetailedProcess[];
}

export class QueryImpl implements Query {
  id: number;
  processes: DetailedProcess[];
  query_type: QueryType;
  query_value: string;
  created_at: string;
  result_process_count: number;
  status: QueryStatus;

  constructor(q: Query) {
    this.id = q.id;
    this.created_at = q.created_at;
    this.processes = q.processes.map(it => new DetailedProcessImpl(it));
    this.query_type = q.query_type;
    this.query_value = q.query_value;
    this.result_process_count = q.result_process_count;
    this.status = q.status;
  }
}