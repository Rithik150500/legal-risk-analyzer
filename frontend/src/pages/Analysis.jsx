import React, { useState, useEffect } from 'react';
import {
  Play,
  RefreshCw,
  Trash2,
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  AlertTriangle,
  ChevronDown
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { analysisApi, documentsApi, createWebSocket } from '../api';

function Analysis() {
  const [sessions, setSessions] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  const [showNewAnalysis, setShowNewAnalysis] = useState(false);

  // New analysis form state
  const [analysisMessage, setAnalysisMessage] = useState(
    'Conduct a comprehensive legal risk analysis of all documents in the data room. Identify risks across all categories including contractual, compliance, IP, liability, financial, operational, and reputational risks. Generate a detailed report and interactive dashboard.'
  );
  const [approvalLevel, setApprovalLevel] = useState('moderate');
  const [selectedDocs, setSelectedDocs] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [sessionsRes, docsRes] = await Promise.all([
        analysisApi.list(),
        documentsApi.list()
      ]);
      setSessions(sessionsRes.data.sessions || []);
      setDocuments(docsRes.data.documents || []);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startAnalysis = async () => {
    if (!analysisMessage.trim()) {
      alert('Please enter an analysis request');
      return;
    }

    setStarting(true);
    try {
      const response = await analysisApi.start({
        message: analysisMessage,
        approval_level: approvalLevel,
        documents: selectedDocs.length > 0 ? selectedDocs : null
      });

      const sessionId = response.data.session_id;

      // Connect to WebSocket for updates
      const ws = createWebSocket(
        sessionId,
        (data) => {
          if (data.type === 'status_update') {
            setSessions(prev =>
              prev.map(s =>
                s.session_id === sessionId
                  ? { ...s, ...data }
                  : s
              )
            );
          }
        },
        (error) => console.error('WebSocket error:', error)
      );

      // Reload sessions to include the new one
      await loadData();
      setShowNewAnalysis(false);
      setSelectedSession(sessionId);
    } catch (error) {
      console.error('Failed to start analysis:', error);
      alert('Failed to start analysis: ' + (error.response?.data?.detail || error.message));
    } finally {
      setStarting(false);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!confirm('Delete this analysis session?')) return;

    try {
      await analysisApi.delete(sessionId);
      setSessions(sessions.filter(s => s.session_id !== sessionId));
      if (selectedSession === sessionId) {
        setSelectedSession(null);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      alert('Failed to delete session');
    }
  };

  const viewResults = async (sessionId) => {
    try {
      const response = await analysisApi.getResults(sessionId);
      setSelectedSession(sessionId);
      // Update session with results
      setSessions(prev =>
        prev.map(s =>
          s.session_id === sessionId
            ? { ...s, results: response.data.results }
            : s
        )
      );
    } catch (error) {
      console.error('Failed to load results:', error);
      alert('Failed to load results');
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const selectedSessionData = sessions.find(s => s.session_id === selectedSession);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analysis</h1>
          <p className="text-gray-600 mt-1">Start and monitor risk analysis sessions</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadData}
            className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button
            onClick={() => setShowNewAnalysis(!showNewAnalysis)}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            <Play className="w-4 h-4 mr-2" />
            New Analysis
          </button>
        </div>
      </div>

      {/* New Analysis Form */}
      {showNewAnalysis && (
        <div className="mb-8 bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Start New Analysis</h2>

          {/* Analysis Message */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Analysis Request
            </label>
            <textarea
              value={analysisMessage}
              onChange={(e) => setAnalysisMessage(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Describe what you want to analyze..."
            />
          </div>

          {/* Approval Level */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Approval Level (HITL)
            </label>
            <select
              value={approvalLevel}
              onChange={(e) => setApprovalLevel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="high">High - All operations require approval</option>
              <option value="moderate">Moderate - Planning and outputs only</option>
              <option value="minimal">Minimal - Final outputs only</option>
            </select>
          </div>

          {/* Document Selection */}
          {documents.length > 0 && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Documents to Analyze (leave empty for all)
              </label>
              <div className="max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-2">
                {documents.map((doc) => (
                  <label key={doc.doc_id} className="flex items-center p-2 hover:bg-gray-50 rounded">
                    <input
                      type="checkbox"
                      checked={selectedDocs.includes(doc.doc_id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedDocs([...selectedDocs, doc.doc_id]);
                        } else {
                          setSelectedDocs(selectedDocs.filter(id => id !== doc.doc_id));
                        }
                      }}
                      className="mr-3"
                    />
                    <span className="text-sm">{doc.filename || doc.doc_id}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Start Button */}
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setShowNewAnalysis(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={startAnalysis}
              disabled={starting || documents.length === 0}
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {starting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Start Analysis
                </>
              )}
            </button>
          </div>

          {documents.length === 0 && (
            <p className="mt-4 text-sm text-yellow-600">
              <AlertTriangle className="w-4 h-4 inline mr-1" />
              No documents available. Please upload and process documents first.
            </p>
          )}
        </div>
      )}

      {/* Sessions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Session List */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Analysis Sessions ({sessions.length})
            </h2>
          </div>

          {sessions.length > 0 ? (
            <div className="divide-y divide-gray-200 max-h-[500px] overflow-y-auto">
              {sessions.map((session) => (
                <div
                  key={session.session_id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer ${
                    selectedSession === session.session_id ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => setSelectedSession(session.session_id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 text-sm">
                        {session.session_id.substring(0, 12)}...
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(session.started_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <StatusBadge status={session.status} />
                      {session.status === 'completed' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            viewResults(session.session_id);
                          }}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                          title="View results"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteSession(session.session_id);
                        }}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Delete session"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Progress bar for running sessions */}
                  {session.status === 'running' && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-gray-600">{session.current_step}</span>
                        <span className="text-gray-500">{session.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${session.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No analysis sessions yet.</p>
              <p className="text-sm mt-1">Start a new analysis to begin.</p>
            </div>
          )}
        </div>

        {/* Session Details */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Session Details</h2>
          </div>

          {selectedSessionData ? (
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Session ID</label>
                  <div className="text-sm font-mono text-gray-900">
                    {selectedSessionData.session_id}
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-500">Status</label>
                  <div className="mt-1">
                    <StatusBadge status={selectedSessionData.status} />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-500">Started</label>
                  <div className="text-sm text-gray-900">
                    {new Date(selectedSessionData.started_at).toLocaleString()}
                  </div>
                </div>

                {selectedSessionData.completed_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Completed</label>
                    <div className="text-sm text-gray-900">
                      {new Date(selectedSessionData.completed_at).toLocaleString()}
                    </div>
                  </div>
                )}

                {selectedSessionData.error && (
                  <div className="p-3 bg-red-50 rounded-lg">
                    <label className="text-sm font-medium text-red-700">Error</label>
                    <div className="text-sm text-red-600 mt-1">
                      {selectedSessionData.error}
                    </div>
                  </div>
                )}

                {/* Results visualization */}
                {selectedSessionData.results && (
                  <div className="mt-6">
                    <label className="text-sm font-medium text-gray-500 block mb-4">
                      Risk Summary
                    </label>

                    <RiskSummaryChart data={selectedSessionData.results.risk_count} />

                    <div className="mt-4 space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">High Risks</span>
                        <span className="font-medium text-red-600">
                          {selectedSessionData.results.risk_count.high}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Medium Risks</span>
                        <span className="font-medium text-orange-600">
                          {selectedSessionData.results.risk_count.medium}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Low Risks</span>
                        <span className="font-medium text-green-600">
                          {selectedSessionData.results.risk_count.low}
                        </span>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="flex items-center gap-2">
                        {selectedSessionData.results.has_report && (
                          <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                            Report Generated
                          </span>
                        )}
                        {selectedSessionData.results.has_dashboard && (
                          <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                            Dashboard Ready
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              <Eye className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Select a session to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const config = {
    completed: { icon: CheckCircle, color: 'bg-green-100 text-green-800' },
    running: { icon: Loader2, color: 'bg-blue-100 text-blue-800', animate: true },
    failed: { icon: XCircle, color: 'bg-red-100 text-red-800' },
    initializing: { icon: Clock, color: 'bg-yellow-100 text-yellow-800' },
  };

  const { icon: Icon, color, animate } = config[status] || config.initializing;

  return (
    <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${color}`}>
      <Icon className={`w-3 h-3 mr-1 ${animate ? 'animate-spin' : ''}`} />
      {status}
    </span>
  );
}

function RiskSummaryChart({ data }) {
  const chartData = [
    { name: 'High', value: data.high, fill: '#DC2626' },
    { name: 'Medium', value: data.medium, fill: '#EA580C' },
    { name: 'Low', value: data.low, fill: '#16A34A' },
  ];

  const total = data.high + data.medium + data.low;

  if (total === 0) {
    return (
      <div className="text-center py-4 text-gray-500">
        No risks identified
      </div>
    );
  }

  return (
    <div className="h-40">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical">
          <XAxis type="number" hide />
          <YAxis type="category" dataKey="name" width={60} />
          <Tooltip />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default Analysis;
