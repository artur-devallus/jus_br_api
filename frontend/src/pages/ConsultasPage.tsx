import {useState} from "react";
import {useForm} from "react-hook-form";
import {z} from "zod";
import {zodResolver} from "@hookform/resolvers/zod";
import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Skeleton} from "@/components/ui/skeleton";
import {ProcessCard} from "@/components/process/process-card";
import {useCreateQuery, useQueryDetail} from "@/hooks/useQueries.ts";
import {DetailedProcess, Query} from "@/models/query.ts";
import {ErrorUtils} from "@/lib/errorUtils.ts";
import {cn} from "@/lib/utils.ts";
import {Loader2, Search} from "lucide-react";
import {formatCpfOrProcess} from "@/lib/format-utils.ts";

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
      onSuccess: (data) => {
        setQuery(data);
      },
      onError: (error) => {
        ErrorUtils.displayAxiosError(error);
      }
    });
  };

  return (
    <div className="flex flex-col items-center w-full h-full p-6">
      <div className="w-full max-w-xl text-center mb-8">
        <h1 className="text-3xl font-semibold mb-6">Consulta Processual</h1>

        <form onSubmit={form.handleSubmit(onSubmit)} className="relative">
          <Input
            {...form.register("term")}
            placeholder="CPF ou Número do processo"
            value={form.watch("term")}
            onChange={(e) => form.setValue("term", formatCpfOrProcess(e.target.value))}
            className={cn(
              "h-12 pl-5 pr-12 text-lg border border-gray-300 focus-visible:ring-0 focus:border-primary rounded-lg"
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

      {/* Área rolável apenas para resultados */}
      <div className="w-full max-w-2xl flex-1 overflow-y-auto space-y-4 pb-4">
        {(details?.processes || []).map((p: DetailedProcess) => (
          <ProcessCard key={p.process_number} process={p} />
        ))}

        {!details && !isStarting && (
          <div className="text-gray-500 mt-8 text-sm text-center">
            Digite um CPF ou número de processo para iniciar a consulta.
          </div>
        )}

        {(isStarting || isFetching) && !details && (
          <div className="flex flex-col gap-3 mt-6">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        )}

        {details?.status === "running" && (
          <div className="flex items-center justify-center gap-2 mt-4 text-sm text-gray-600">
            <Loader2 className="animate-spin h-4 w-4 text-primary" />
            <span>Consultando tribunais...</span>
          </div>
        )}
      </div>
    </div>
  );
}
