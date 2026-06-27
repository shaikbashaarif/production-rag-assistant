import React from "react";
import { Upload } from "lucide-react";

export default function UploadPanel({
  files,
  setFiles,
  handleUpload,
  loading,
  status,
}) {
  return (
    <section className="card upload-card">
      <h2>Upload Documents</h2>

      <input
        type="file"
        accept=".pdf,.txt"
        multiple
        onChange={(e) =>
          setFiles(Array.from(e.target.files || []))
        }
      />

      <button
        onClick={handleUpload}
        disabled={!files.length || loading}
      >
        <Upload size={16} />
        Upload & Index
      </button>

      {files.length > 0 && (
        <p className="status">
          Selected: {files.map((f) => f.name).join(", ")}
        </p>
      )}

      {status && <p className="status">{status}</p>}
    </section>
  );
}