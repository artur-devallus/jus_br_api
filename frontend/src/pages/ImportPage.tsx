import {useCallback, useEffect, useState} from "react";
import {useDropzone} from "react-dropzone";
import * as XLSX from "xlsx";
import {Button} from "@/components/ui/button";
import {useCreateQuery} from "@/hooks/useQueries";
import {Query, QueryImpl, QueryStatus} from "@/models/query";
import {UploadCloud} from "lucide-react";
import {formatCpfOrProcess, onlyDigits} from "@/lib/format-utils";
import {api} from "@/lib/axios.ts";

interface Row {
  id: number;
  value: string;
  type: "cpf" | "process";
  query?: Query;
  status: QueryStatus;
}

export function ImportPage() {
  const [rows, setRows] = useState<Row[]>([]);
  const {mutateAsync: startQuery} = useCreateQuery();

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
        const type = digits.length === 11 ? 'cpf' : 'process';
        return {id: i, value: digits, type, status: 'queued'};
      });

      setRows(newRows);
    };
    reader.readAsArrayBuffer(file);
  }, []);

  const {getRootProps, getInputProps, isDragActive} = useDropzone({
    onDrop,
    accept: {
      "text/csv": [],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": []
    },
  });

  const handleSend = async () => {
    for (const row of rows) {
      setRows((prev) => prev.map((r) => (r.id === row.id ? {...r, status: "queued"} : r)));
      try {
        const query = await startQuery({term: row.value, enqueue: true});
        setRows((prev) => prev.map((r) => (r.id === row.id ? {...r, status: query.status, query} : r)));
      } catch {
        setRows((prev) => prev.map((r) => (r.id === row.id ? {...r, status: "failed"} : r)));
      }
    }
  };

  useEffect(() => {
    const interval = setInterval(async () => {
      const running = rows.filter((r) => r.query && (r.status === "running" || r.status === "queued"));
      if (running.length === 0) return;

      for (const row of running) {
        try {
          const q = await api
            .get(`/v1/queries/${row?.query?.id}/detailed`)
            .then((res) => new QueryImpl(res.data));
          if (!q) continue;
          setRows((prev) =>
            prev.map((r) =>
              r.id === row.id ? {...r, query: q, status: q.status} : r
            )
          );
        } catch {
          // ignora falhas
        }
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [rows]);

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
      case "queued": return "Enfileirado";
      case "running": return "Processando";
      case "failed": return "Erro";
      case "done": return "Concluído";
    }
  };

  const displayProcessCount = (count: number) =>
    count === 0
      ? "Nenhum processo encontrado"
      : count === 1
        ? "1 processo encontrado"
        : `${count} processos encontrados`;

  return (
    <div className="p-4 sm:p-6 w-full min-h-screen flex flex-col items-center">
      <h1 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 text-center">Importar Consultas</h1>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg w-full max-w-2xl min-h-[160px] sm:h-40 flex flex-col items-center justify-center cursor-pointer px-4 text-center transition
          ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-400"}`}
      >
        <input {...getInputProps()} />
        <UploadCloud className="w-8 h-8 sm:w-10 sm:h-10 text-gray-500 mb-2"/>
        <p className="text-gray-700 text-sm sm:text-base">
          {isDragActive ? "Solte o arquivo aqui..." : "Arraste um arquivo CSV/XLSX ou clique para selecionar"}
        </p>
      </div>

      {/* Botões */}
      <div className="flex flex-col sm:flex-row items-center gap-3 mt-6 mb-6 w-full max-w-2xl justify-center">
        <Button onClick={handleSend} disabled={!rows.length} className="w-full sm:w-auto">
          Enviar
        </Button>
        <Button
          variant="outline"
          onClick={handleDownload}
          disabled={!rows.some(r => r.query?.processes?.length)}
          className="w-full sm:w-auto"
        >
          Baixar Resultados
        </Button>
      </div>

      {/* Tabela */}
      <div className="w-full max-w-5xl overflow-x-auto border rounded shadow-sm">
        <table className="min-w-full text-xs sm:text-sm">
          <thead className="bg-gray-100">
          <tr>
            <th className="px-3 sm:px-4 py-2 text-left w-[180px]">CPF/Processo</th>
            <th className="px-3 sm:px-4 py-2 text-left w-[180px]">Quantidade</th>
            <th className="px-3 sm:px-4 py-2 text-left w-[100px]">Status</th>
          </tr>
          </thead>
          <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-t hover:bg-gray-50">
              <td className="px-3 sm:px-4 py-2 truncate max-w-[200px]">
                {r.value.length === 11
                  ? `CPF: ${formatCpfOrProcess(r.value)}`
                  : `Processo: ${formatCpfOrProcess(r.value)}`}
              </td>
              <td className="px-3 sm:px-4 py-2">
                {r.query ? displayProcessCount(r.query.result_process_count) : ""}
              </td>
              <td className="px-3 sm:px-4 py-2 text-gray-700">
                {r.query ? displayStatus(r) : "Não enviado"}
              </td>
            </tr>
          ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
