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
import {DetailedProcess} from "@/models/query";
import {ScrollText, Users, FileText, Paperclip} from "lucide-react";

interface ProcessCardProps {
  process: DetailedProcess;
}

export function ProcessCard({process}: ProcessCardProps) {
  const proc = process.process().process;
  const parties = process.process().case_parties;
  const movements = process.process().movements;
  const attachments = process.process().attachments || [];

  return (
    <Card className="w-full max-w-3xl border-gray-200 shadow-sm hover:shadow-md transition">
      <CardHeader className="border-b bg-gray-50/60">
        <CardTitle className="text-base sm:text-lg font-semibold text-gray-800">
          Processo <span className="text-primary">{process.formated_process_number()}</span>
        </CardTitle>
      </CardHeader>

      <CardContent className="text-sm text-gray-700 space-y-2 pt-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1">
          <p><strong>Tribunal:</strong> {process.tribunal()}</p>
          <p><strong>CPF:</strong> {process.activePartyAuthorCpf()}</p>
          <p><strong>Nome:</strong> {process.activePartyAuthorName()}</p>
          <p><strong>Assunto:</strong> {proc.subject || "-"}</p>
        </div>

        <Accordion type="single" collapsible className="w-full mt-4">
          {/* Detalhes */}
          <AccordionItem value="details">
            <AccordionTrigger className="text-gray-800 font-medium">
              <div className="flex items-center gap-2">
                <ScrollText className="h-4 w-4 text-primary" />
                Detalhes do processo
              </div>
            </AccordionTrigger>
            <AccordionContent className="space-y-1 mt-1 text-gray-600">
              <p><strong>Classe Judicial:</strong> {proc.judicial_class || "-"}</p>
              <p><strong>Entidade Julgadora:</strong> {proc.judge_entity || "-"}</p>
              <p><strong>Colégio Julgador:</strong> {proc.collegiate_judge_entity || "-"}</p>
              <p><strong>Data de Julgamento:</strong> {proc.accessment_date || "-"}</p>
              <p><strong>Juiz:</strong> {proc.judge || "-"}</p>
              <p><strong>Data de Distribuição:</strong> {proc.distribution_date || "-"}</p>
              <p><strong>Juridição:</strong> {proc.jurisdiction || "-"}</p>
              <p><strong>Processo Referenciado:</strong> {proc.referenced_process_number || "-"}</p>
            </AccordionContent>
          </AccordionItem>

          {/* Partes */}
          <AccordionItem value="parties">
            <AccordionTrigger className="text-gray-800 font-medium">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-primary" />
                Partes
              </div>
            </AccordionTrigger>
            <AccordionContent className="space-y-3 mt-1 text-gray-600">
              <div>
                <strong>Polo Ativo:</strong>
                <ul className="list-disc list-inside mt-1 space-y-1 max-h-[240px] overflow-y-auto pr-2">
                  {parties.active.length === 0 && (
                    <li className="text-gray-400 text-xs">Nenhum participante</li>
                  )}
                  {parties.active.map((p, i) => (
                    <li key={i}>
                      {p.name} {p.role ? `(${p.role})` : ""}
                      {p.documents.length > 0 && (
                        <ul className="ml-5 text-xs text-gray-500 list-disc list-inside">
                          {p.documents.map((d, j) => (
                            <li key={j}>{d.type.toUpperCase()}: {d.value}</li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <strong>Polo Passivo:</strong>
                <ul className="list-disc list-inside mt-1 space-y-1 max-h-[240px] overflow-y-auto pr-2">
                  {parties.passive.length === 0 && (
                    <li className="text-gray-400 text-xs">Nenhum participante</li>
                  )}
                  {parties.passive.map((p, i) => (
                    <li key={i}>
                      {p.name} {p.role ? `(${p.role})` : ""}
                      {p.documents.length > 0 && (
                        <ul className="ml-5 text-xs text-gray-500 list-disc list-inside">
                          {p.documents.map((d, j) => (
                            <li key={j}>{d.type.toUpperCase()}: {d.value}</li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Movimentações */}
          <AccordionItem value="movements">
            <AccordionTrigger className="text-gray-800 font-medium">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-primary" />
                Movimentações
              </div>
            </AccordionTrigger>
            <AccordionContent className="space-y-2 mt-1">
              {movements.length === 0 ? (
                <p className="text-gray-500 text-sm">Nenhuma movimentação registrada.</p>
              ) : (
                <div className="max-h-[300px] overflow-y-auto pr-2 divide-y divide-gray-200">
                  {movements.map((m, i) => (
                    <div key={i} className="py-2">
                      <p><strong>Data:</strong> {m.created_at}</p>
                      <p><strong>Descrição:</strong> {m.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </AccordionContent>
          </AccordionItem>

          {/* Anexos */}
          {/*<AccordionItem value="attachments">*/}
          {/*  <AccordionTrigger className="text-gray-800 font-medium">*/}
          {/*    <div className="flex items-center gap-2">*/}
          {/*      <Paperclip className="h-4 w-4 text-primary" />*/}
          {/*      Anexos*/}
          {/*    </div>*/}
          {/*  </AccordionTrigger>*/}
          {/*  <AccordionContent className="space-y-2 mt-1">*/}
          {/*    {attachments.length === 0 ? (*/}
          {/*      <p className="text-gray-500 text-sm">Nenhum anexo disponível.</p>*/}
          {/*    ) : (*/}
          {/*      <div className="max-h-[300px] overflow-y-auto pr-2 divide-y divide-gray-200">*/}
          {/*        {attachments.map((a, i) => (*/}
          {/*          <div key={i} className="py-2">*/}
          {/*            <p><strong>Descrição:</strong> {a.description}</p>*/}
          {/*            <p><strong>Data:</strong> {a.created_at || "-"}</p>*/}
          {/*            <p><strong>Arquivo:</strong> {a.file_md5 ? "Disponível" : "Indisponível"}</p>*/}
          {/*            <p><strong>Protocolo:</strong> {a.protocol_md5 || "-"}</p>*/}
          {/*          </div>*/}
          {/*        ))}*/}
          {/*      </div>*/}
          {/*    )}*/}
          {/*  </AccordionContent>*/}
          {/*</AccordionItem>*/}
        </Accordion>
      </CardContent>
    </Card>
  );
}
