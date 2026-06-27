import React from "react";
import { BarChart3, FileText } from "lucide-react";

export default function Dashboard({ summary }) {
  return (
    <section className="dashboard">
      <div className="metric">
        <BarChart3 size={18} />
        <span>Total Queries</span>
        <b>{summary?.total_queries ?? 0}</b>
      </div>

      <div className="metric">
        <FileText size={18} />
        <span>Documents</span>
        <b>{summary?.total_documents ?? 0}</b>
      </div>

      <div className="metric">
        <span>Chunks</span>
        <b>{summary?.total_chunks ?? 0}</b>
      </div>

      <div className="metric">
        <span>No Answer</span>
        <b>{summary?.no_answer_count ?? 0}</b>
      </div>

      <div className="metric">
        <span>Avg Latency</span>
        <b>{summary?.average_latency_ms ?? 0} ms</b>
      </div>
    </section>
  );
}