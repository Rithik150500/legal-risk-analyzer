import React, { useState, useEffect, useRef } from 'react';
import {
  Upload,
  FileText,
  Trash2,
  RefreshCw,
  File,
  CheckCircle,
  XCircle,
  Loader2,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { documentsApi } from '../api';

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedDoc, setExpandedDoc] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await documentsApi.list();
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    uploadFiles(files);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files);
      uploadFiles(files);
    }
  };

  const uploadFiles = async (files) => {
    setUploading(true);
    try {
      const response = await documentsApi.upload(files);
      setUploadedFiles(response.data.files || []);
      alert(`Uploaded ${files.length} file(s). Click "Process Documents" to index them.`);
    } catch (error) {
      console.error('Failed to upload files:', error);
      alert('Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  const processDocuments = async () => {
    setProcessing(true);
    try {
      await documentsApi.process();
      alert('Document processing started. This may take a few minutes.');
      // Reload documents after a delay
      setTimeout(loadDocuments, 5000);
    } catch (error) {
      console.error('Failed to process documents:', error);
      alert('Failed to start document processing');
    } finally {
      setProcessing(false);
    }
  };

  const deleteDocument = async (docId) => {
    if (!confirm(`Delete document ${docId}?`)) return;

    try {
      await documentsApi.delete(docId);
      setDocuments(documents.filter(d => d.doc_id !== docId));
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('Failed to delete document');
    }
  };

  const toggleExpand = (docId) => {
    setExpandedDoc(expandedDoc === docId ? null : docId);
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-1">Upload and manage documents for analysis</p>
        </div>
        <button
          onClick={loadDocuments}
          className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Upload Area */}
      <div
        className={`mb-8 p-8 border-2 border-dashed rounded-lg text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept=".pdf,.docx,.doc,.xlsx,.xls,.pptx,.ppt,.txt,.rtf,.odt"
        />

        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-lg font-medium text-gray-700 mb-2">
          {dragActive ? 'Drop files here' : 'Drag and drop files here'}
        </p>
        <p className="text-sm text-gray-500 mb-4">
          or click to browse
        </p>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {uploading ? (
            <>
              <Loader2 className="w-4 h-4 inline mr-2 animate-spin" />
              Uploading...
            </>
          ) : (
            'Select Files'
          )}
        </button>
        <p className="text-xs text-gray-400 mt-4">
          Supported: PDF, DOCX, DOC, XLSX, XLS, PPTX, PPT, TXT, RTF, ODT
        </p>
      </div>

      {/* Uploaded Files (Pending Processing) */}
      {uploadedFiles.length > 0 && (
        <div className="mb-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-yellow-800">
              {uploadedFiles.length} file(s) uploaded - Ready for processing
            </h3>
            <button
              onClick={processDocuments}
              disabled={processing}
              className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
            >
              {processing ? (
                <>
                  <Loader2 className="w-4 h-4 inline mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                'Process Documents'
              )}
            </button>
          </div>
          <ul className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <li key={index} className="flex items-center text-sm text-yellow-700">
                <File className="w-4 h-4 mr-2" />
                {file.filename}
                <span className="ml-2 text-yellow-500">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Document List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Data Room Documents ({documents.length})
          </h2>
        </div>

        {documents.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <div key={doc.doc_id} className="p-4">
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => toggleExpand(doc.doc_id)}
                >
                  <div className="flex items-center">
                    <FileText className="w-10 h-10 text-blue-500 mr-4" />
                    <div>
                      <div className="font-medium text-gray-900">
                        {doc.filename || doc.doc_id}
                      </div>
                      <div className="text-sm text-gray-500">
                        {doc.page_count} pages
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteDocument(doc.doc_id);
                      }}
                      className="p-2 text-red-600 hover:bg-red-50 rounded"
                      title="Delete document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    {expandedDoc === doc.doc_id ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedDoc === doc.doc_id && (
                  <div className="mt-4 pl-14">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-700 mb-2">Summary</h4>
                      <p className="text-sm text-gray-600">{doc.summary}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No documents in the data room yet.</p>
            <p className="text-sm mt-1">Upload and process documents to get started.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Documents;
