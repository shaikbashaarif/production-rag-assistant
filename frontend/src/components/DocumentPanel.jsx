import React from "react";
import { Trash2 } from "lucide-react";

export default function DocumentPanel({
  documents,
  handleDeleteDocument,
}) {
  return (
    <section className="card documents-card">
      <h2>Documents</h2>

      {documents.length === 0 && (
        <p>No documents uploaded yet.</p>
      )}

      {documents.map((doc) => (
        <div
          key={doc.document_id}
          className="document-row"
        >
          <div>
            <b>{doc.filename}</b>

            <p>
              Chunks: {doc.chunks_added} | ID:{" "}
              {doc.document_id.slice(0, 8)}
            </p>
          </div>

          <button
            className="delete"
            type="button"
            onClick={() =>
              handleDeleteDocument(doc.document_id)
            }
          >
            <Trash2 size={16} />
            Delete
          </button>
        </div>
      ))}
    </section>
  );
}