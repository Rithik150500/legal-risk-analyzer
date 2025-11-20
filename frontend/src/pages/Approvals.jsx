import React, { useState, useEffect } from 'react';
import {
  CheckCircle,
  XCircle,
  Edit3,
  RefreshCw,
  Clock,
  FileText,
  AlertTriangle,
  Eye,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { approvalsApi, statisticsApi } from '../api';

function Approvals() {
  const [approvals, setApprovals] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApproval, setSelectedApproval] = useState(null);
  const [showAuditLogs, setShowAuditLogs] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [approvalsRes, logsRes] = await Promise.all([
        approvalsApi.list(),
        statisticsApi.getAuditLogs()
      ]);
      setApprovals(approvalsRes.data.approvals || []);
      setAuditLogs(logsRes.data.logs || []);
    } catch (error) {
      console.error('Failed to load approvals:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewApprovalDetails = async (approvalId) => {
    try {
      const response = await approvalsApi.get(approvalId);
      setSelectedApproval(response.data);
    } catch (error) {
      console.error('Failed to load approval details:', error);
      alert('Failed to load approval details');
    }
  };

  const submitDecision = async (approvalId, decision, editedValue = null, reason = null) => {
    try {
      await approvalsApi.decide(approvalId, {
        session_id: selectedApproval?.session_id || '',
        approval_id: approvalId,
        decision,
        edited_value: editedValue,
        reason
      });

      // Refresh data
      await loadData();
      setSelectedApproval(null);
      alert(`Decision "${decision}" submitted successfully`);
    } catch (error) {
      console.error('Failed to submit decision:', error);
      alert('Failed to submit decision');
    }
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
          <h1 className="text-2xl font-bold text-gray-900">Approvals</h1>
          <p className="text-gray-600 mt-1">Human-in-the-Loop approval management</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowAuditLogs(!showAuditLogs)}
            className={`flex items-center px-4 py-2 text-sm font-medium rounded-lg ${
              showAuditLogs
                ? 'text-white bg-blue-600'
                : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
            }`}
          >
            <FileText className="w-4 h-4 mr-2" />
            Audit Logs
          </button>
          <button
            onClick={loadData}
            className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Pending Approvals */}
      {!showAuditLogs && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Approval List */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Pending Approvals ({approvals.length})
              </h2>
            </div>

            {approvals.length > 0 ? (
              <div className="divide-y divide-gray-200 max-h-[500px] overflow-y-auto">
                {approvals.map((approval) => (
                  <div
                    key={approval.approval_id}
                    className={`p-4 hover:bg-gray-50 cursor-pointer ${
                      selectedApproval?.approval_id === approval.approval_id ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => viewApprovalDetails(approval.approval_id)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-900">
                          {getActionLabel(approval.action_type)}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          Session: {approval.session_id.substring(0, 8)}...
                        </div>
                        <div className="text-xs text-gray-400">
                          {new Date(approval.created_at).toLocaleString()}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-yellow-500" />
                        <Eye className="w-4 h-4 text-gray-400" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500 opacity-50" />
                <p>No pending approvals</p>
                <p className="text-sm mt-1">All actions have been approved</p>
              </div>
            )}
          </div>

          {/* Approval Details */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Approval Details</h2>
            </div>

            {selectedApproval ? (
              <div className="p-6">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Action Type</label>
                    <div className="text-sm text-gray-900 font-medium">
                      {getActionLabel(selectedApproval.action_request?.tool_name)}
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">Session ID</label>
                    <div className="text-sm font-mono text-gray-900">
                      {selectedApproval.session_id}
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-500">Created</label>
                    <div className="text-sm text-gray-900">
                      {new Date(selectedApproval.created_at).toLocaleString()}
                    </div>
                  </div>

                  {/* Action Details */}
                  <div>
                    <label className="text-sm font-medium text-gray-500">Action Details</label>
                    <div className="mt-2 p-3 bg-gray-50 rounded-lg max-h-48 overflow-y-auto">
                      <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                        {JSON.stringify(selectedApproval.action_request, null, 2)}
                      </pre>
                    </div>
                  </div>

                  {/* Decision Buttons */}
                  <div className="pt-4 border-t border-gray-200">
                    <div className="flex gap-2">
                      <button
                        onClick={() => submitDecision(selectedApproval.approval_id, 'approve')}
                        className="flex-1 flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Approve
                      </button>
                      <button
                        onClick={() => submitDecision(selectedApproval.approval_id, 'reject')}
                        className="flex-1 flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Reject
                      </button>
                      <button
                        onClick={() => {
                          const reason = prompt('Enter edit reason:');
                          if (reason) {
                            submitDecision(selectedApproval.approval_id, 'edit', null, reason);
                          }
                        }}
                        className="flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                <Eye className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select an approval to view details</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Audit Logs */}
      {showAuditLogs && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Audit Logs ({auditLogs.length})
            </h2>
          </div>

          {auditLogs.length > 0 ? (
            <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
              {auditLogs.map((log, index) => (
                <AuditLogEntry key={index} log={log} />
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No audit logs yet</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function AuditLogEntry({ log }) {
  const [expanded, setExpanded] = useState(false);

  const decisionColors = {
    approve: 'text-green-600 bg-green-50',
    reject: 'text-red-600 bg-red-50',
    edit: 'text-blue-600 bg-blue-50',
  };

  return (
    <div className="p-4">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-4">
          <span className={`px-2 py-1 text-xs font-medium rounded ${decisionColors[log.decision] || 'bg-gray-100 text-gray-600'}`}>
            {log.decision}
          </span>
          <div>
            <div className="text-sm font-medium text-gray-900">
              {getActionLabel(log.action_type || log.tool_name)}
            </div>
            <div className="text-xs text-gray-500">
              by {log.reviewer} • {new Date(log.timestamp).toLocaleString()}
            </div>
          </div>
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </div>

      {expanded && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto">
            {JSON.stringify(log, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

function getActionLabel(actionType) {
  const labels = {
    write_todos: 'Create Analysis Plan',
    task: 'Delegate to Subagent',
    get_document: 'Access Document',
    get_document_pages: 'Access Document Pages',
    write_file: 'Create File',
    edit_file: 'Edit File',
  };
  return labels[actionType] || actionType || 'Unknown Action';
}

export default Approvals;
