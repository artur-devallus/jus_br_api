// src/lib/importUtils.ts
import Papa from "papaparse";
import * as XLSX from "xlsx";

export type RawRow = { raw: string; line: number };

export function isCPF(digits: string) {
  return /^\d{11}$/.test(digits);
}

export function isProcessNumber(digits: string) {
  return /^\d{20}$/.test(digits);
}

export async function parseFile(file: File): Promise<RawRow[]> {
  const name = file.name.toLowerCase();
  if (name.endsWith(".csv")) {
    return parseCSV(file);
  }
  if (name.endsWith(".xls") || name.endsWith(".xlsx")) {
    return parseXlsx(file);
  }
  throw new Error("Unsupported file type");
}

function parseCSV(file: File): Promise<RawRow[]> {
  return new Promise((resolve, reject) => {
    const rows: RawRow[] = [];
    let line = 0;
    Papa.parse(file, {
      skipEmptyLines: true,
      step: (result) => {
        line++;
        const value = Array.isArray(result.data) ? result.data.join(" ") : String(result.data);
        rows.push({ raw: String(value).trim(), line });
      },
      complete: () => resolve(rows),
      error: (err) => reject(err),
    });
  });
}

function parseXlsx(file: File): Promise<RawRow[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const data = ev.target?.result;
        const workbook = XLSX.read(data, { type: "array" });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const json = XLSX.utils.sheet_to_json<string[]>(sheet, { header: 1, raw: false });
        const rows: RawRow[] = [];
        for (let i = 0; i < json.length; i++) {
          const row = json[i] as never[];
          const value = (row || []).join(" ").trim();
          rows.push({ raw: String(value).trim(), line: i + 1 });
        }
        resolve(rows);
      } catch (e) {
        reject(e);
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}
