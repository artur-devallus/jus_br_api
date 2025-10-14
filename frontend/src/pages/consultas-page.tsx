import {useState} from "react";
import {useForm} from "react-hook-form";
import {z} from "zod";
import {zodResolver} from "@hookform/resolvers/zod";
import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Skeleton} from "@/components/ui/skeleton";
import {ProcessCard} from "@/components/process/process-card";
import {useCreateQuery, useQueryDetail} from "@/hooks/useQueries";
import {DetailedProcess, Query} from "@/models/query";
import {ErrorUtils} from "@/lib/errorUtils";
import {cn} from "@/lib/utils";
import {Loader2, Search, AlertCircle, CheckCircle2, Clock} from "lucide-react";
import {formatCpfOrProcess} from "@/lib/format-utils";

const schema = z.object({
  term: z.string().min(11, "Digite um CPF ou número de processo válido"),
});

type FormValues = z.infer<typeof schema>;

export default function ConsultasPage() {
  const [query, setQuery] = useState<Query | null>(null);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {term: ""},
  });

  const {mutate: startQuery, isPending: isStarting} = useCreateQuery();
  const {data: details, isFetching} = useQueryDetail(query);

  const onSubmit = (data: FormValues) => {
    startQuery(data, {
      onSuccess: (res) => setQuery(res),
      onError: (err) => ErrorUtils.displayAxiosError(err),
    });
  };

  const getStatusDisplay = (status?: string) => {
    switch (status) {
      case "queued":
        return (
          <div className="flex items-center gap-2 text-amber-500">
            <Clock className="h-4 w-4" />
            <span className="text-sm font-medium">Na fila</span>
          </div>
        );
      case "running":
        return (
          <div className="flex items-center gap-2 text-blue-500 animate-pulse">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm font-medium">Consultando tribunais...</span>
          </div>
        );
      case "failed":
        return (
          <div className="flex items-center gap-2 text-red-500">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm font-medium">Erro na consulta</span>
          </div>
        );
      case "done":
        return (
          <div className="flex items-center gap-2 text-emerald-600">
            <CheckCircle2 className="h-4 w-4" />
            <span className="text-sm font-medium">Consulta concluída</span>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col items-center w-full h-full p-6">
      <div className="w-full max-w-xl text-center mb-8">
        <h1 className="text-3xl font-semibold mb-4">Consulta Processual</h1>
        <p className="text-gray-500 text-sm mb-6">
          Consulte processos por CPF ou número completo do processo.
        </p>

        <form onSubmit={form.handleSubmit(onSubmit)} className="relative">
          <Input
            {...form.register("term")}
            placeholder="CPF ou Número do processo"
            value={form.watch("term")}
            onChange={(e) => form.setValue("term", formatCpfOrProcess(e.target.value))}
            className={cn(
              "h-12 pl-5 pr-12 text-lg border border-gray-300 focus-visible:ring-2 focus-visible:ring-primary/40 rounded-lg transition"
            )}
          />
          <Button
            type="submit"
            size="icon"
            disabled={isStarting}
            className="absolute right-1.5 top-1.5 h-9 w-9"
            variant="ghost"
          >
            {isStarting ? (
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
            ) : (
              <Search className="h-5 w-5 text-gray-500" />
            )}
          </Button>
        </form>
      </div>

      <div className="w-full max-w-2xl flex-1 overflow-y-auto space-y-4 pb-8">
        {/* Estado inicial */}
        {!details && !isStarting && (
          <div className="text-gray-500 text-sm text-center mt-8">
            Digite um CPF ou número de processo para iniciar a consulta.
          </div>
        )}

        {/* Carregando */}
        {(isStarting || (isFetching && !details)) && (
          <div className="flex flex-col gap-3 mt-6 animate-pulse">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        )}

        {/* Status geral */}
        {details?.status && (
          <div className="flex justify-center mt-4">{getStatusDisplay(details.status)}</div>
        )}

        {/* Resultados */}
        {(details?.processes || []).map((p: DetailedProcess) => (
          <ProcessCard key={p.process_number} process={p} />
        ))}

        {/* Nenhum processo encontrado */}
        {details && details.processes?.length === 0 && (
          <div className="text-gray-500 text-sm text-center mt-6">
            Nenhum processo encontrado para o termo informado.
          </div>
        )}
      </div>
    </div>
  );
}
