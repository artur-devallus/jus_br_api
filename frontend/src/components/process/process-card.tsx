import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import {DetailedProcess} from "@/models/query.ts";

interface ProcessCardProps {
  process: DetailedProcess;
}

export function ProcessCard({process}: ProcessCardProps) {
  const proc = process.process().process;
  const parties = process.process().case_parties;
  const movements = process.process().movements;
  const attachments = process.process().attachments;

  return (
    <Card className="w-full max-w-3xl">
      <CardHeader>
        <CardTitle>Processo {process.formated_process_number()}</CardTitle>
      </CardHeader>

      <CardContent className="text-sm text-gray-700 space-y-2">
        <p><strong>Tribunal:</strong> {process.tribunal()}</p>
        <p><strong>CPF:</strong> {process.cpf()}</p>
        <p><strong>Nome:</strong> {process.name()}</p>

        <Accordion type="single" collapsible className="w-full mt-4 overflow-y-auto">
          <AccordionItem value="details">
            <AccordionTrigger>Detalhes do processo</AccordionTrigger>
            <AccordionContent className="space-y-1">
              <p><strong>Classe Judicial:</strong> {proc.judicial_class}</p>
              <p><strong>Entidade Julgadora:</strong> {proc.judge_entity}</p>
              <p><strong>Processo Referenciado:</strong> {proc.referenced_process_number}</p>
              <p><strong>Assunto:</strong> {proc.subject}</p>
              <p><strong>Colégio Julgador:</strong> {proc.collegiate_judge_entity || '-'}</p>
              <p><strong>Data de Julgamento:</strong> {proc.accessment_date || '-'}</p>
              <p><strong>Juiz:</strong> {proc.judge || '-'}</p>
              <p><strong>Data de Distribuição:</strong> {proc.distribution_date || '-'}</p>
              <p><strong>Juridição:</strong> {proc.jurisdiction || '-'}</p>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="parties">
            <AccordionTrigger>Partes</AccordionTrigger>
            <AccordionContent className="space-y-3">
              <div>
                <strong>Polo Ativo:</strong>
                <div className="max-h-[300px] overflow-y-auto pr-2 space-y-2">
                  <ul className="list-disc list-inside">
                    {parties.active.map((p, i) => (
                      <li key={i}>
                        {p.name} {p.role ? `(${p.role})` : ""}
                        {p.documents.length > 0 && (
                          <ul className="ml-4 text-xs text-gray-600">
                            {p.documents.map((d, j) => (
                              <li key={j}>{d.type.toUpperCase()}: {d.value}</li>
                            ))}
                          </ul>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div>
                <strong>Polo Passivo:</strong>
                <div className="max-h-[300px] overflow-y-auto pr-2 space-y-2">
                  <ul className="list-disc list-inside">
                    {parties.passive.map((p, i) => (
                      <li key={i}>
                        {p.name} {p.role ? `(${p.role})` : ""}
                        {p.documents.length > 0 && (
                          <ul className="ml-4 text-xs text-gray-600">
                            {p.documents.map((d, j) => (
                              <li key={j}>{d.type.toUpperCase()}: {d.value}</li>
                            ))}
                          </ul>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="movements">
            <AccordionTrigger>Movimentações</AccordionTrigger>
            <AccordionContent>
              {movements.length === 0 ? (
                <p className="text-gray-500">Nenhuma movimentação registrada.</p>
              ) : (
                <div className="max-h-[300px] overflow-y-auto pr-2 space-y-2">
                  {movements.map((m, i) => (
                    <div
                      key={i}
                      className="border-b border-gray-200 pb-2 text-sm"
                    >
                      <p><strong>Data:</strong> {m.created_at}</p>
                      <p><strong>Descrição:</strong> {m.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="attachments">
            <AccordionTrigger>Anexos</AccordionTrigger>
            <AccordionContent className="space-y-2">
              {attachments.length === 0 ? (
                <p>Nenhum anexo disponível.</p>
              ) : (
                <div className="max-h-[300px] overflow-y-auto pr-2 space-y-2">
                  {attachments.map((a, i) => (
                    <div key={i} className="border-b pb-2">
                      <p><strong>Descrição:</strong> {a.description}</p>
                      <p><strong>Data:</strong> {a.created_at || '-'}</p>
                      <p><strong>Arquivo:</strong> {a.file_md5 ? "Disponível" : "Indisponível"}</p>
                      <p><strong>Protocolo:</strong> {a.protocol_md5 || '-'}</p>
                    </div>
                  ))}
                </div>
              )}
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  );
}
