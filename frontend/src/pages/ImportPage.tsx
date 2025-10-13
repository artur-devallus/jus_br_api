import {useCallback, useEffect, useState} from "react";
import {useDropzone} from "react-dropzone";
import * as XLSX from "xlsx";
import {Button} from "@/components/ui/button";
import {useCreateQuery} from "@/hooks/useQueries";
import {Query, QueryImpl} from "@/models/query";
import {Loader2, UploadCloud} from "lucide-react";
import {formatCpfOrProcess, onlyDigits} from "@/lib/format-utils";
import {api} from "@/lib/axios.ts";

interface Row {
  id: number;
  value: string;
  type: "cpf" | "process";
  query?: Query;
  status: 'sending' | 'queued' | "running" | "done" | "error";
}

export function ImportPage() {
  const [rows, setRows] = useState<Row[]>([]);
  const {mutateAsync: startQuery} = useCreateQuery();
  
  // Dropzone
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      const data = new Uint8Array(e.target?.result as ArrayBuffer);
      const workbook = XLSX.read(data, {type: "array"});
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const json: Row[] = XLSX.utils.sheet_to_json(sheet, {header: 1});
      const values = json.flat().filter((v) => !!v);
      
      const newRows: Row[] = values.map((val: Row, i: number) => {
        const digits = onlyDigits(String(val)).padStart(11, '0');
        const type = digits.length === 11 ? "cpf" : "process";
        return {id: i, value: digits, type, status: "queued"};
      });
      
      setRows(newRows);
    };
    reader.readAsArrayBuffer(file);
  }, []);
  
  const {getRootProps, getInputProps, isDragActive} = useDropzone({
    onDrop,
    accept: {"text/csv": [], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": []},
  });
  
  // Envio linha a linha
  const handleSend = async () => {
    for (const row of rows) {
      setRows((prev) => prev.map((r) => (r.id === row.id ? {...r, status: "sending"} : r)));
      try {
        const query = await startQuery({term: row.value});
        setRows((prev) => prev.map((r) => (r.id === row.id ? {...r, status: query.status, query} : r)));
      } catch {
        setRows((prev) => prev.map((r) => (r.id === row.id ? {...r, status: "error"} : r)));
      }
    }
  };
  
  // Atualização periódica
  useEffect(() => {
    const interval = setInterval(async () => {
      const running = rows.filter((r) => r.query && (r.status === "running" || r.status === 'queued'));
      if (running.length === 0) return;
      
      for (const row of running) {
        try {
          const q = await api.get(`/v1/queries/${row?.query?.id}/detailed`).then((res) => new QueryImpl(res.data));
          if (!q) continue;
          setRows((prev) =>
            prev.map((r) =>
              r.id === row.id ? {...r, query: q, status: q.status} : r
            )
          );
        } catch {
          // ignora falhas de rede momentâneas
        }
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [rows]);
  
  // Download CSV consolidado
  const handleDownload = () => {
    const header = ["CPF", "Tribunal", "Número do Processo", "Assunto"];
    const csv = [
      header,
      ...rows.flatMap((r) =>
        r.query?.processes.map((p) => [
          p.cpf(),
          p.tribunal(),
          p.formated_process_number(),
          p.subject().replace(/[\n\r]/g, " "),
        ]) || []
      ),
    ]
      .map((row) => row.join(","))
      .join("\n");
    
    const blob = new Blob([csv], {type: "text/csv"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "resultados.csv";
    a.click();
    URL.revokeObjectURL(url);
  };
  
  const displayStatus = (r: Row) => {
    switch (r.status) {
      case "sending":
        return 'Enviando';
      case "queued":
        return 'Enfileirado'
      case "running":
        return 'Processando';
      case "error":
        return 'Erro';
      case "done":
        return 'Concluído'
    }
  }
  
  return (
    <div className="p-6 w-full h-full flex flex-col items-center">
      <h1 className="text-2xl font-semibold mb-6">Importar Consultas</h1>
      
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg w-full max-w-2xl h-40 flex flex-col items-center justify-center cursor-pointer transition
          ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-400"}`}
      >
        <input {...getInputProps()} />
        <UploadCloud className="w-10 h-10 text-gray-500 mb-2"/>
        {isDragActive ? (
          <p className="text-gray-700">Solte o arquivo aqui...</p>
        ) : (
          <p className="text-gray-700">Arraste um arquivo CSV/XLSX ou clique para selecionar</p>
        )}
      </div>
      
      <div className="flex items-center gap-3 mt-6 mb-6">
        <Button onClick={handleSend} disabled={!rows.length}>Enviar</Button>
        <Button variant="outline" onClick={handleDownload} disabled={!rows.some(r => r.query?.processes?.length)}>Baixar
          Resultados</Button>
      </div>
      
      {/* Tabela */}
      <div className="w-full max-w-5xl overflow-x-auto border rounded">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 text-left w-[180px]">CPF</th>
            <th className="px-4 py-2 text-left w-[180px]">Quantidade</th>
            <th className="px-4 py-2 text-left w-[100px]">Status</th>
          </tr>
          </thead>
          <tbody>
          {rows.flatMap((r) =>
            r.query !== undefined ? (
              <tr key={`${r.id}-${r.query.id}`} className="border-t">
                <td className="px-4 py-2">{r.value.length === 11 ? `CPF: ${formatCpfOrProcess(r.value)}` : `Processo: ${formatCpfOrProcess(r.value)}`}</td>
                <td className="px-4 py-2">
                  {r.query.result_process_count > 0 ? `${r.query.result_process_count} processos encontrados` : 'Nenhum processo encontrado'}
                </td>
                <td className="px-4 py-2">{displayStatus(r)}</td>
              </tr>
            ) : (
              <tr key={r.id} className="border-t">
                <td colSpan={3} className="px-4 py-2 text-gray-500 italic">
                  {r.status === "sending" ? (
                    <span className="flex items-center gap-1"><Loader2
                      className="h-3 w-3 animate-spin"/> Enviando...</span>
                  ) : r.status === "error" ? "Erro ao enviar" : "Sem resultados"}
                </td>
              </tr>
            )
          )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
