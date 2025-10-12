import {useState} from "react";

interface Props {
  tribunal: string;
  process_number: string;
  name: string;
}

export default function TribunalCard({tribunal, process_number, name}: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white shadow rounded p-4 border hover:shadow-md transition">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="font-semibold">{tribunal.toUpperCase()}</h3>
          <p className="text-sm text-gray-600">{process_number}</p>
          <p className="text-gray-800">{name}</p>
        </div>
        <button
          onClick={() => setExpanded((v) => !v)}
          className="text-blue-600 font-medium hover:underline"
        >
          {expanded ? "Fechar" : "Detalhar"}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 text-sm text-gray-700 border-t pt-2">
          <p>Mais informações do processo...</p>
        </div>
      )}
    </div>
  );
}
