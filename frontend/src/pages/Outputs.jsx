import React, { useState, useEffect } from 'react';
import {
  Download,
  FileText,
  BarChart2,
  RefreshCw,
  ExternalLink,
  File,
  Clock,
  Eye
} from 'lucide-react';
import { outputsApi } from '../api';
import { format } from 'date-fns';

function Outputs() {
  const [outputs, setOutputs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(null);

  useEffect(() => {
    loadOutputs();
  }, []);

  const loadOutputs = async () => {
    try {
      const response = await outputsApi.list();
      setOutputs(response.data.outputs || []);
    } catch (error) {
      console.error('Failed to load outputs:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (filename) => {
    setDownloading(filename);
    try {
      const response = await outputsApi.download(filename);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download file:', error);
      alert('Failed to download file');
    } finally {
      setDownloading(null);
    }
  };

  const downloadLatestReport = async () => {
    setDownloading('report');
    try {
      const response = await outputsApi.getLatestReport();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'legal_risk_analysis_report.docx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download report:', error);
      alert('No report available. Run an analysis first.');
    } finally {
      setDownloading(null);
    }
  };

  const viewDashboard = async () => {
    try {
      const response = await outputsApi.getLatestDashboard();
      const blob = new Blob([response.data], { type: 'text/html' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      alert('No dashboard available. Run an analysis first.');
    }
  };

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    switch (ext) {
      case 'docx':
      case 'doc':
        return <FileText className="w-6 h-6 text-blue-500" />;
      case 'html':
        return <BarChart2 className="w-6 h-6 text-purple-500" />;
      case 'json':
        return <File className="w-6 h-6 text-green-500" />;
      default:
        return <File className="w-6 h-6 text-gray-500" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Categorize outputs
  const reports = outputs.filter(o => o.filename.endsWith('.docx') || o.filename.endsWith('.doc'));
  const dashboards = outputs.filter(o => o.filename.endsWith('.html'));
  const otherFiles = outputs.filter(o =>
    !o.filename.endsWith('.docx') &&
    !o.filename.endsWith('.doc') &&
    !o.filename.endsWith('.html')
  );

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Outputs</h1>
          <p className="text-gray-600 mt-1">Download generated reports and dashboards</p>
        </div>
        <button
          onClick={loadOutputs}
          className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <FileText className="w-8 h-8 text-blue-600 mr-3" />
            <div>
              <h3 className="font-semibold text-gray-900">Analysis Report</h3>
              <p className="text-sm text-gray-500">Professional Word document</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Comprehensive legal risk analysis report with executive summary,
            detailed findings, and recommendations.
          </p>
          <button
            onClick={downloadLatestReport}
            disabled={downloading === 'report'}
            className="w-full flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {downloading === 'report' ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Downloading...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Download Report
              </>
            )}
          </button>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <BarChart2 className="w-8 h-8 text-purple-600 mr-3" />
            <div>
              <h3 className="font-semibold text-gray-900">Interactive Dashboard</h3>
              <p className="text-sm text-gray-500">React-based visualization</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Interactive dashboard with risk heat maps, filtering capabilities,
            and detailed risk exploration.
          </p>
          <button
            onClick={viewDashboard}
            className="w-full flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700"
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            Open Dashboard
          </button>
        </div>
      </div>

      {/* File List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            All Output Files ({outputs.length})
          </h2>
        </div>

        {outputs.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {/* Reports Section */}
            {reports.length > 0 && (
              <div>
                <div className="px-6 py-3 bg-gray-50">
                  <h3 className="text-sm font-medium text-gray-700">Reports</h3>
                </div>
                {reports.map((file) => (
                  <FileRow
                    key={file.filename}
                    file={file}
                    icon={getFileIcon(file.filename)}
                    onDownload={downloadFile}
                    downloading={downloading}
                    formatSize={formatFileSize}
                  />
                ))}
              </div>
            )}

            {/* Dashboards Section */}
            {dashboards.length > 0 && (
              <div>
                <div className="px-6 py-3 bg-gray-50">
                  <h3 className="text-sm font-medium text-gray-700">Dashboards</h3>
                </div>
                {dashboards.map((file) => (
                  <FileRow
                    key={file.filename}
                    file={file}
                    icon={getFileIcon(file.filename)}
                    onDownload={downloadFile}
                    downloading={downloading}
                    formatSize={formatFileSize}
                    onView={() => {
                      outputsApi.download(file.filename).then(response => {
                        const blob = new Blob([response.data], { type: 'text/html' });
                        const url = window.URL.createObjectURL(blob);
                        window.open(url, '_blank');
                      });
                    }}
                  />
                ))}
              </div>
            )}

            {/* Other Files Section */}
            {otherFiles.length > 0 && (
              <div>
                <div className="px-6 py-3 bg-gray-50">
                  <h3 className="text-sm font-medium text-gray-700">Other Files</h3>
                </div>
                {otherFiles.map((file) => (
                  <FileRow
                    key={file.filename}
                    file={file}
                    icon={getFileIcon(file.filename)}
                    onDownload={downloadFile}
                    downloading={downloading}
                    formatSize={formatFileSize}
                  />
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">
            <Download className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No output files yet</p>
            <p className="text-sm mt-1">Run an analysis to generate reports and dashboards</p>
          </div>
        )}
      </div>
    </div>
  );
}

function FileRow({ file, icon, onDownload, downloading, formatSize, onView }) {
  return (
    <div className="px-6 py-4 flex items-center justify-between hover:bg-gray-50">
      <div className="flex items-center">
        {icon}
        <div className="ml-4">
          <div className="font-medium text-gray-900">{file.filename}</div>
          <div className="text-sm text-gray-500">
            {formatSize(file.size)} • Modified {format(new Date(file.modified), 'PPp')}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {onView && (
          <button
            onClick={onView}
            className="p-2 text-purple-600 hover:bg-purple-50 rounded"
            title="View in browser"
          >
            <Eye className="w-4 h-4" />
          </button>
        )}
        <button
          onClick={() => onDownload(file.filename)}
          disabled={downloading === file.filename}
          className="p-2 text-blue-600 hover:bg-blue-50 rounded disabled:opacity-50"
          title="Download"
        >
          {downloading === file.filename ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Download className="w-4 h-4" />
          )}
        </button>
      </div>
    </div>
  );
}

export default Outputs;
