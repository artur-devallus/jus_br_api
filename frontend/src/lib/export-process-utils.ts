import * as XLSX from "xlsx";
import {DetailedProcess} from "@/models/query.ts";


const asDetailed = async (
  wb: XLSX.WorkBook,
  allQueries: number[],
  fetchDetailed: (id: number) => Promise<DetailedProcess[]>,
) => {
  for (const q of allQueries) {
    const processes = await fetchDetailed(q);
    
    for (const proc of processes) {
      const wsData: (string | null)[][] = [];
      
      const p = proc.process().process;
      const parties = proc.process().case_parties;
      const movements = proc.process().movements;
      const attachments = proc.process().attachments;
      
      // Cabeçalho principal
      wsData.push([""]);
      wsData.push(["📄 DADOS DO PROCESSO"]);
      wsData.push(["────────────────────────────"]);
      wsData.push(["Número do Processo", p.process_number]);
      wsData.push(["Classe Judicial", p.judicial_class]);
      wsData.push(["Entidade Julgadora", p.judge_entity]);
      wsData.push(["Processo Referenciado", p.referenced_process_number]);
      wsData.push(["Assunto", p.subject]);
      wsData.push(["Colégio Julgador", p.collegiate_judge_entity || "-"]);
      wsData.push(["Data de Julgamento", formatDate(p.accessment_date)]);
      wsData.push(["Juiz", p.judge || "-"]);
      wsData.push(["Data de Distribuição", formatDate(p.distribution_date)]);
      wsData.push(["Juridição", p.jurisdiction || "-"]);
      wsData.push([]);
      
      // Partes ativas
      wsData.push(["⚖️ PARTES ATIVAS"]);
      wsData.push(["────────────────────────────"]);
      if (!parties.active.length) wsData.push(["Nenhuma parte ativa."]);
      parties.active.forEach((a) => {
        wsData.push([a.name, a.role || "-"]);
        a.documents.forEach((d) =>
          wsData.push([`• ${d.type === 'unknown' ? '-' : d.type.toUpperCase()}`, d.value])
        );
        wsData.push([]);
      });
      
      // Partes passivas
      wsData.push(["⚖️ PARTES PASSIVAS"]);
      wsData.push(["────────────────────────────"]);
      if (!parties.passive.length) wsData.push(["Nenhuma parte passiva."]);
      parties.passive.forEach((p) => {
        wsData.push([p.name, p.role || "-"]);
        p.documents.forEach((d) =>
          wsData.push([`• ${d.type === 'unknown' ? '-' : d.type.toUpperCase()}`, d.value])
        );
        wsData.push([]);
      });
      
      // Movimentações
      wsData.push(["📜 MOVIMENTAÇÕES"]);
      wsData.push(["────────────────────────────"]);
      if (!movements.length) wsData.push(["Nenhuma movimentação registrada."]);
      movements.forEach((m, i) => {
        wsData.push([`Movimentação ${i + 1}`]);
        wsData.push(["Data", formatDateTime(m.created_at)]);
        wsData.push(["Descrição", m.description]);
        if (m.attachments?.length) {
          m.attachments.forEach((a) =>
            wsData.push([
              `Anexo: ${a.document_ref || "-"}`,
              `Data: ${formatDate(a.document_date)}`,
            ])
          );
        }
        wsData.push([]);
      });
      
      // Anexos gerais
      wsData.push(["📎 ANEXOS GERAIS"]);
      wsData.push(["────────────────────────────"]);
      if (!attachments.length) wsData.push(["Nenhum anexo disponível."]);
      attachments.forEach((a) => {
        wsData.push([
          a.description,
          formatDateTime(a.created_at),
          a.file_md5 ? "Arquivo disponível" : "Sem arquivo",
          a.protocol_md5 || "-",
        ]);
      });
      
      // Definição da planilha
      const ws = XLSX.utils.aoa_to_sheet(wsData);
      ws["!cols"] = [{wch: 45}, {wch: 55}, {wch: 25}, {wch: 25}];
      
      const sheetName = sanitizeSheetName(`${proc.activePartyAuthorCpf()} - ${p.process_number}`);
      XLSX.utils.book_append_sheet(wb, ws, sheetName);
    }
  }
}
const asSimple = async (
  wb: XLSX.WorkBook,
  allQueries: number[],
  fetchDetailed: (id: number) => Promise<DetailedProcess[]>
) => {
  const wsData: (string | null)[][] = [];
  
  wsData.push([
    "Número do Processo",
    "Tribunal",
    "Autor",
    "Advogado",
    "Defensor",
    "Assunto",
  ]);
  
  for (const q of allQueries) {
    const processes = await fetchDetailed(q);
    
    for (const proc of processes) {
      const p = proc.process().process;
      
      wsData.push([
        p.process_number,
        proc.tribunal() || "-",
        `${proc.activePartyAuthorName()} - ${proc.activePartyAuthorCpf()}`,
        `${proc.activePartyLawyerName()} - ${proc.activePartyLawyerCpf()}`,
        `${proc.passivePartyDefendantName()} - ${proc.passivePartyDefendantCpfOrCnpj()}`,
        proc.subject() || "-",
      ]);
    }
  }
  
  const ws = XLSX.utils.aoa_to_sheet(wsData);
  ws["!cols"] = [
    {wch: 40},
    {wch: 25},
    {wch: 50},
    {wch: 50},
    {wch: 50},
    {wch: 65},
  ];
  
  XLSX.utils.book_append_sheet(wb, ws, "Processos");
};

/**
 * Exporta todos os processos detalhados (de todas as queries) para um único Excel.
 * Cada aba é um processo identificado por: {CPF} - {Número do processo}.
 */
export async function exportAllProcessesToExcel(
  allQueries: number[],
  fetchDetailed: (id: number) => Promise<DetailedProcess[]>,
  fileName?: string,
  mode: 'single' | 'detailed' = 'single'
) {
  const wb = XLSX.utils.book_new();
  if (mode === 'detailed') {
    await asDetailed(wb, allQueries, fetchDetailed);
  } else {
    await asSimple(wb, allQueries, fetchDetailed);
  }
  
  const wbout = XLSX.write(wb, {bookType: "xlsx", type: "array"});
  const blob = new Blob([wbout], {type: "application/octet-stream"});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = fileName || 'processos.xlsx';
  link.click();
}

function sanitizeSheetName(name: string): string {
  return name.replace(/[/\\?*[\]:]/g, "").substring(0, 31) || "Processo";
}

function formatDate(date?: string | null): string {
  if (!date) return "-";
  return new Date(date).toLocaleDateString("pt-BR");
}

function formatDateTime(date?: string | null): string {
  if (!date) return "-";
  return new Date(date).toLocaleString("pt-BR");
}
