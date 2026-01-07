import { useEffect, useState } from "react";

export function useRunEvents(setEvents: any) {
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

    es.addEventListener("end", (event) => {
      console.log("Stream ended");
      es.close(); // Close the connection when done
    });

    return () => es.close();
  }, []);
}
