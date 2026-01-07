import { Button } from "@/components/ui/button";
import { ButtonGroup } from "@/components/ui/button-group";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
  InputGroupText,
} from "@/components/ui/input-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import Editor from "@monaco-editor/react";
import { useEffect, useState } from "react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GraphInspector } from "./components/GraphInspector";
import { useRunEvents } from "./hooks/useRunEvents";

function JsonCodeInput({ value, onChange }) {
  const [error, setError] = useState<string | null>(null);

  const handleChange = (v: string | undefined) => {
    if (!v) return;
    onChange(v);
    try {
      JSON.parse(v);
      setError(null);
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div className="space-y-2">
      <Editor
        height="100px"
        defaultLanguage="json"
        value={value}
        onChange={handleChange}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          scrollBeyondLastLine: false,
          // automaticLayout: true,
        }}
      />
    </div>
  );
}

function Authorization({ value, onChange }) {
  return (
    <div className="flex">
      <Label className="w-[30%] justify-center" htmlFor="token">
        Bearer Token
      </Label>
      <Input
        className="w-[50%]"
        placeholder="Token"
        id="token"
        type="password"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

function BodyInput({ values, onChange }) {
  return (
    <Tabs defaultValue="body" className="h-40 w-full">
      <TabsList>
        <TabsTrigger value="authorization">Authorization</TabsTrigger>
        <TabsTrigger value="body">Body</TabsTrigger>
      </TabsList>
      <TabsContent className="h-full" value="authorization">
        <Authorization
          value={values.headers}
          onChange={(v) => onChange("headers", v)}
        />
      </TabsContent>
      <TabsContent className="h-full" value="body">
        <JsonCodeInput
          value={values.body}
          onChange={(v) => onChange("body", v)}
        />
      </TabsContent>
    </Tabs>
  );
}

function ApiQueryInput({ values, onChange }) {
  return (
    <ButtonGroup className="flex w-full">
      <ButtonGroup className="flex-1">
        <Select
          value={values.method}
          onValueChange={(v) => onChange("method", v)}
        >
          <SelectTrigger className="w-35">
            <SelectValue>{values.method}</SelectValue>
          </SelectTrigger>
          <SelectContent className="min-w-24">
            <SelectItem key="get" value="GET">
              GET
            </SelectItem>
            <SelectItem key="post" value="POST">
              POST
            </SelectItem>
            <SelectItem key="put" value="PUT">
              PUT
            </SelectItem>
            <SelectItem key="delete" value="DELETE">
              DELETE
            </SelectItem>
          </SelectContent>
        </Select>
        <InputGroup>
          <InputGroupInput
            placeholder="Enter API path"
            className="pl-1!"
            value={values.path}
            onChange={(e) => onChange("path", e.target.value)}
          />
          <InputGroupAddon>
            <InputGroupText className="text-neutral-400">
              http://localhost:8000/api/agent/
            </InputGroupText>
          </InputGroupAddon>
        </InputGroup>
      </ButtonGroup>
      <ButtonGroup>
        <Button type="submit">Send</Button>
      </ButtonGroup>
    </ButtonGroup>
  );
}

// export default function App() {
//   const [nodes, setNodes] = useState([
//     { name: "node_1", status: "pending" },
//     { name: "node_2", status: "pending" },
//   ]);
//
//   const invokeGraph = async () => {
//     const res = await fetch("http://localhost:8000/invoke", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({}),
//     });
//
//     const { run_id } = await res.json();
//
//     const es = new EventSource(`http://localhost:8000/events/${run_id}`);
//
//     es.onmessage = (e) => {
//       const data = JSON.parse(e.data);
//
//       if (data.node === "node_1") {
//         setNodes((prev) => [
//           { ...prev[0], status: "done" },
//           { ...prev[1], status: "running" },
//         ]);
//       }
//       if (data.node === "node_2") {
//         setNodes((prev) => [
//           { ...prev[0], status: "done" },
//           { ...prev[1], status: "done" },
//         ]);
//         es.close();
//       }
//     };
//   };
//
//   return (
//     <>
//       <GraphView nodes={nodes} />
//       <button onClick={invokeGraph}>Invoke Graph</button>
//     </>
//   );
// }

type FormValues = {
  method: string;
  path: string;
  query_params: string;
  body: string;
  headers: string;
};

async function createRun(state) {
  const options: RequestInit = {
    method: state.method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${state.token}`,
    },
  };

  if (state.method === "POST") {
    options.body = JSON.stringify(state.body);
  }

  const res = await fetch(
    `http://localhost:8000/api/agent/${state.path}`,
    options,
  );

  return res.json() as Promise<{ run_id: string }>;
}

function ApiForm({ onRunStart }: { onRunStart: (id: string) => void }) {
  const [state, setState] = useState<FormValues>({
    method: "GET",
    path: "",
    query_params: "",
    body: "",
    headers: "",
  });

  const setField = <K extends keyof FormValues>(
    key: K,
    value: FormValues[K],
  ) => {
    setState((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("submitted:", state);
    const { run_id } = await createRun(state);
    console.log("run_id:", run_id);
    onRunStart(run_id);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full flex-col gap-2 rounded-lg bg-white p-4 shadow-xl"
    >
      <ApiQueryInput values={state} onChange={setField} />
      <BodyInput values={state} onChange={setField} />
    </form>
  );
}

// DB Canvas

function useDbTables() {
  const [tables, setTables] = useState<string[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/db/tables")
      .then((res) => res.json())
      .then((data) => setTables(data.tables));
  }, []);

  return tables;
}

function useTableSnapshot(table: string) {
  const [snapshot, setSnapshot] = useState<TableSnapshot | null>(null);

  useEffect(() => {
    const fetchData = () => {
      fetch(`http://localhost:8000/api/db/table/${table}`)
        .then((res) => res.json())
        .then(setSnapshot);
    };

    fetchData();
    const id = setInterval(fetchData, 1500);
    return () => clearInterval(id);
  }, [table]);

  return snapshot;
}

interface Props {
  table: string;
}

function TableNode({ table }: Props) {
  const snapshot = useTableSnapshot(table);

  if (!snapshot) return null;

  return (
    <div className="w-full rounded-2xl border bg-white p-4 shadow-lg">
      <div className="mb-2 flex justify-between text-lg font-bold">
        <span>{snapshot.table}</span>
        <span className="text-muted-foreground text-xs">live</span>
      </div>

      <div className="overflow-x-auto">
        <Table className="table-fixed">
          <TableHeader>
            <TableRow>
              {snapshot.columns.map((col) => (
                <TableHead key={col} className="w-25 max-w-25 truncate">
                  {col}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>

          <TableBody>
            {snapshot.rows.map((row, i) => (
              <TableRow key={i}>
                {snapshot.columns.map((col) => (
                  <TableCell key={col} className="w-25 max-w-25 truncate">
                    {String(row[col])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

interface TableSnapshot {
  table: string;
  columns: string[];
  rows: Record<string, any>[];
  updated_at: string;
}

function DbCanvas() {
  const tables = useDbTables();

  return (
    <div className="h-full w-full overflow-auto p-6">
      <div className="flex flex-col gap-6">
        {tables.map((t) => (
          <TableNode key={t} table={t} />
        ))}
      </div>
    </div>
  );
}

// Main

export default function App() {
  const [runId, setRunId] = useState<string | null>(null);
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const es = new EventSource(`http://localhost:8000/runs/events`);

    es.onopen = () => {
      console.log("EventSource connected");
    };

    es.onmessage = (e) => {
      setEvents((prev) => [...prev, JSON.parse(e.data)]);
    };

    es.onerror = (error) => {
      console.error("EventSource failed:", error);
    };

    return () => es.close();
  }, []);

  const onRunStart = (id: string) => {
    setRunId(id);
    setEvents([]);
  };

  return (
    <div className="grid h-screen grid-cols-2 gap-4 p-4">
      <div className="flex h-full flex-col gap-4 overflow-y-auto">
        <ApiForm onRunStart={onRunStart} />
        <div className="min-h-0 flex-1 overflow-y-scroll rounded-lg bg-purple-500 shadow-xl">
          <GraphInspector events={events} />
        </div>
      </div>
      <div className="h-full rounded-lg bg-teal-500 shadow-xl">
        <DbCanvas />
      </div>
    </div>
  );
}
