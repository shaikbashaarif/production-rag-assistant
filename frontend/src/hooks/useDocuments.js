import { useState } from "react";

import {
  uploadMultipleDocuments,
  listDocuments,
  deleteDocument,
  getEvaluationSummary,
} from "../lib/api";

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [summary, setSummary] = useState(null);
  const [status, setStatus] = useState("");

  async function refreshDocuments() {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    }
  }

  async function refreshSummary() {
    try {
      const data = await getEvaluationSummary();
      setSummary(data);
    } catch (err) {
      console.error(err);
    }
  }

  async function upload(files, setLoading) {
    if (!files.length) return;

    setLoading(true);
    setStatus("Uploading and indexing documents...");

    try {
      const results = await uploadMultipleDocuments(files);

      const totalChunks = results.reduce(
        (sum, item) => sum + item.chunks_added,
        0
      );

      setStatus(
        `${results.length} document(s) indexed successfully. Total chunks: ${totalChunks}`
      );

      await refreshDocuments();
      await refreshSummary();
    } catch (err) {
      setStatus(`Upload failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function remove(documentId) {
    if (!confirm("Delete this document?")) return;

    try {
      await deleteDocument(documentId);

      await refreshDocuments();
      await refreshSummary();

      setStatus("Document deleted successfully.");
    } catch (err) {
      setStatus(`Delete failed: ${err.message}`);
    }
  }

  return {
    documents,
    summary,
    status,
    setStatus,

    refreshDocuments,
    refreshSummary,

    upload,
    remove,
  };
}