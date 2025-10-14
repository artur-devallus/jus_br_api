import {useState} from "react";
import {useQuery} from "@tanstack/react-query";
import {Card, CardHeader, CardTitle, CardContent} from "@/components/ui/card";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Checkbox} from "@/components/ui/checkbox";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import {api} from "@/lib/axios.ts";
import {formatCpfOrProcess, onlyDigits} from "@/lib/format-utils.ts";
import {AlertCircle, CheckCircle, ChevronLeft, ChevronRight, Clock, Loader2} from "lucide-react";
import {Query, QueryImpl} from "@/models/query.ts";
import {exportAllProcessesToExcel} from "@/lib/export-process-utils.ts";


async function fetchQueries(params: {
  query_value?: string;
  result_process_count_ge?: number;
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
  const [withMovements, setWithMovements] = useState(false);
  const [page, setPage] = useState(1);

  const {data, isFetching} = useQuery({
    queryKey: ["queries", {
      queryValue: queryValue ? (onlyDigits(queryValue).length === 11 || onlyDigits(queryValue).length == 20) ? queryValue : undefined : undefined,
      withMovements,
      page
    }],
    queryFn: () =>
      fetchQueries({
        query_value: queryValue || undefined,
        result_process_count_ge: withMovements ? 1 : undefined,
        page,
        size: 10,
      }),
    placeholderData: (prev) => prev,
  });

  async function exportAll() {
    const {data: allQueries} = await api.get("/v1/queries", {
      params: {size: 1000, result_process_count_ge: 1},
    });
    const ids = allQueries.map((q: Query) => q.id);

    await exportAllProcessesToExcel(ids, async (queryId: number) => {
      return await api.get(`/v1/queries/${queryId}/detailed`).then((res) => new QueryImpl(res.data).processes);
    });
  }

  const displayStatus = (r: Query) => {
    switch (r.status) {
      case "queued":
        return (
          <span className="flex items-center gap-1 text-blue-600 font-medium">
            <Clock size={14}/> Enfileirado
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
          <div className="flex gap-2 w-full sm:w-auto">
            <Button onClick={() => setPage(1)} disabled={isFetching} className="flex-1 sm:flex-none">
              Filtrar
            </Button>
            <Button variant="outline" onClick={exportAll} className="flex-1 sm:flex-none">
              Exportar tudo
            </Button>
          </div>
        </div>

        {/* Tabela */}
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>CPF/Processo</TableHead>
              <TableHead>Quantidade de processos</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.map((q) => (
              <TableRow key={q.id}>
                <TableCell>{formatCpfOrProcess(q.query_value)}</TableCell>
                <TableCell>{q.result_process_count}</TableCell>
                <TableCell>{displayStatus(q)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {/* Paginação */}
        <div className="flex justify-end items-center gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            <ChevronLeft size={18}/>
          </Button>
          <span>Página {page}</span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={(data || [])?.length < 10}
          >
            <ChevronRight size={18}/>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
