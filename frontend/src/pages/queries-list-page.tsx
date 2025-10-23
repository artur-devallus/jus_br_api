import {useEffect, useState} from "react";
import {useQuery} from "@tanstack/react-query";
import {Card, CardHeader, CardTitle, CardContent} from "@/components/ui/card";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Checkbox} from "@/components/ui/checkbox";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import {Skeleton} from "@/components/ui/skeleton";
import {api} from "@/lib/axios";
import {formatCpfOrProcess, onlyDigits} from "@/lib/format-utils";
import {
  AlertCircle,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  Clock,
  Download,
  ExternalLink,
  Loader2,
} from "lucide-react";
import {Query, QueryImpl} from "@/models/query";
import {exportAllProcessesToExcel} from "@/lib/export-process-utils";

async function fetchQueries(params: {
  query_value?: string;
  result_process_count_ge?: number;
  tribunal?: string;
  page?: number;
  size?: number;
}): Promise<Query[]> {
  const digits = params.query_value ? onlyDigits(params.query_value) : null;
  if (digits && (digits.length === 11 || digits.length === 20)) {
    params.query_value = digits;
  } else {
    params.query_value = undefined;
  }
  const {data} = await api.get("/v1/queries", {params});
  return data;
}

export default function QueriesListPage() {
  const [queryValue, setQueryValue] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [withMovements, setWithMovements] = useState(false);
  const [tribunal, setTribunal] = useState("ALL");
  const [page, setPage] = useState(1);
  const [isExportingAll, setIsExportingAll] = useState(false);

  // debounce input
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(queryValue), 500);
    return () => clearTimeout(timer);
  }, [queryValue]);

  // reset page ao mudar filtros
  useEffect(() => {
    setPage(1);
  }, [withMovements, tribunal]);

  const {data, isFetching, isLoading} = useQuery({
    queryKey: ["queries", {queryValue: debouncedQuery, withMovements, tribunal, page}],
    queryFn: () =>
      fetchQueries({
        query_value: debouncedQuery || undefined,
        result_process_count_ge: withMovements ? 1 : undefined,
        tribunal: tribunal !== "ALL" ? tribunal : undefined,
        page,
        size: 10,
      }),
    placeholderData: (prev) => prev,
  });

  const detail = async (queryId: number) => {
    return await api.get(`/v1/queries/${queryId}/detailed`).then((res) => new QueryImpl(res.data));
  };

  async function exportAll() {
    try {
      setIsExportingAll(true);
      const {data: allQueries} = await api.get("/v1/queries", {
        params: {
          size: 1000,
          result_process_count_ge: 1,
          tribunal: tribunal !== "ALL" ? tribunal : undefined,
        },
      });
      const ids = allQueries.map((q: Query) => q.id);
      await exportAllProcessesToExcel(ids, detail);
    } finally {
      setIsExportingAll(false);
    }
  }

  async function exportOne(p: Query) {
    await exportAllProcessesToExcel([p.id], detail, `processo_${p.query_value}.xlsx`, "detailed");
  }

  const displayStatus = (r: Query) => {
    switch (r.status) {
      case "queued":
        return (
          <span className="flex items-center gap-1 text-blue-600 font-medium">
            <Clock size={14}/> Em fila
          </span>
        );
      case "running":
        return (
          <span className="flex items-center gap-1 text-amber-600 font-medium">
            <Loader2 size={14} className="animate-spin"/> Processando
          </span>
        );
      case "failed":
        return (
          <span className="flex items-center gap-1 text-red-600 font-medium">
            <AlertCircle size={14}/> Erro
          </span>
        );
      case "done":
        return (
          <span className="flex items-center gap-1 text-green-600 font-medium">
            <CheckCircle size={14}/> Concluído
          </span>
        );
      default:
        return "Não enviado";
    }
  };

  return (
    <Card className="max-w-5xl mx-auto mt-8">
      <CardHeader>
        <CardTitle>Histórico de Consultas</CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Filtros */}
        <div className="flex flex-col sm:flex-row sm:flex-wrap gap-3 items-stretch sm:items-center">
          <Input
            placeholder="CPF ou número do processo"
            value={queryValue}
            onChange={(e) => setQueryValue(formatCpfOrProcess(e.target.value))}
            className="w-full sm:w-64"
          />
          <div className="flex items-center space-x-2">
            <Checkbox
              checked={withMovements}
              onCheckedChange={(v) => setWithMovements(v === true)}
            />
            <span>Com movimentações</span>
          </div>

          <select
            value={tribunal}
            onChange={(e) => setTribunal(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary/40"
          >
            <option value="ALL">Todos</option>
            <option value="TRF1">TRF1</option>
            <option value="TRF2">TRF2</option>
            <option value="TRF3">TRF3</option>
            <option value="TRF4">TRF4</option>
            <option value="TRF5">TRF5</option>
            <option value="TRF6">TRF6</option>
          </select>

          <Button
            variant="outline"
            onClick={exportAll}
            disabled={isExportingAll}
            className="w-full sm:w-auto flex items-center justify-center gap-2"
          >
            {isExportingAll && <Loader2 size={16} className="animate-spin"/>}
            {isExportingAll ? "Exportando..." : "Exportar tudo"}
          </Button>
        </div>

        {/* Loading inicial */}
        {(isLoading || (isFetching && !data)) && (
          <div className="flex flex-col gap-2 mt-4">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-10 w-full"/>
            ))}
          </div>
        )}

        {/* Tabela */}
        {data && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>CPF/Processo</TableHead>
                <TableHead>Quantidade de processos</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Criado em</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((q) => (
                <TableRow key={q.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {isFetching && <Loader2 size={14} className="animate-spin text-gray-400"/>}
                      {formatCpfOrProcess(q.query_value)}
                    </div>
                  </TableCell>
                  <TableCell>{q.result_process_count}</TableCell>
                  <TableCell>{displayStatus(q)}</TableCell>
                  <TableCell>{new Date(q.created_at).toLocaleString("pt-BR")}</TableCell>
                  <TableCell className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => window.open(`/app?query_value=${q.query_value}`, "_blank")}
                    >
                      <ExternalLink className="h-4 w-4"/>
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => exportOne(q)}>
                      <Download className="h-4 w-4"/>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {/* Paginação */}
        {data && (
          <div className="flex justify-end items-center gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 1 || isFetching}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft size={18}/>
            </Button>
            <span>Página {page}</span>
            <Button
              variant="outline"
              size="sm"
              disabled={isFetching || data.length < 10}
              onClick={() => setPage((p) => p + 1)}
            >
              <ChevronRight size={18}/>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
