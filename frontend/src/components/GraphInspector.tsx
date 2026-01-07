import { CheckCircle, PlayCircle } from "lucide-react";
import React from "react";

interface Event {
  id: string;
  graph: "main_graph" | "sub_graph";
  type: "node" | "tool";
  name: string;
  status: "start" | "end";
  content: any;
  timestamp: number;
}

interface EventCardProps {
  event: Event;
}

const EventCard: React.FC<EventCardProps> = ({ event }) => {
  const isStart = event.status === "start";
  const isMainGraph = event.graph === "main_graph";

  return (
    <div
      className={`rounded-lg border-2 transition-all ${
        isMainGraph
          ? "border-blue-500 bg-blue-50"
          : "border-purple-500 bg-purple-50"
      }`}
    >
      <div className="p-4">
        <div className="mb-3 flex items-start justify-between">
          <div className="flex items-center gap-2">
            {isStart ? (
              <PlayCircle
                className={`h-5 w-5 ${isMainGraph ? "text-blue-600" : "text-purple-600"}`}
              />
            ) : (
              <CheckCircle
                className={`h-5 w-5 ${isMainGraph ? "text-blue-600" : "text-purple-600"}`}
              />
            )}
            <span
              className={`font-semibold ${isMainGraph ? "text-blue-900" : "text-purple-900"}`}
            >
              {event.name}
            </span>
          </div>
          <span
            className={`rounded-full px-2 py-1 text-xs font-medium ${
              event.type === "tool"
                ? "bg-orange-100 text-orange-700"
                : "bg-green-100 text-green-700"
            }`}
          >
            {event.type}
          </span>
        </div>

        <div className="mt-2">
          <div
            className={`mb-1 text-xs font-medium ${isMainGraph ? "text-blue-700" : "text-purple-700"}`}
          >
            Graph: {event.graph}
          </div>
          {event.content && Object.keys(event.content).length > 0 && (
            <div className="mt-2">
              <div className="mb-1 text-xs font-medium text-gray-700">
                Content:
              </div>
              <pre className="overflow-x-auto rounded border border-gray-200 bg-white p-2 text-xs">
                {JSON.stringify(event.content, null, 2)}
              </pre>
            </div>
          )}
        </div>

        <div className="mt-2 text-xs text-gray-500">
          {new Date(event.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export function GraphInspector({ events }: { events: any[] }) {
  return (
    <div className="flex h-full w-full flex-col gap-4 p-4">
      {events.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
    </div>
  );
}
