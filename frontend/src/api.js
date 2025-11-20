import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Documents API
export const documentsApi = {
  list: () => api.get('/documents'),
  get: (docId) => api.get(`/documents/${docId}`),
  upload: (files) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  process: () => api.post('/documents/process'),
  delete: (docId) => api.delete(`/documents/${docId}`),
};

// Analysis API
export const analysisApi = {
  start: (request) => api.post('/analysis/start', request),
  getStatus: (sessionId) => api.get(`/analysis/${sessionId}`),
  getResults: (sessionId) => api.get(`/analysis/${sessionId}/results`),
  list: () => api.get('/analysis'),
  delete: (sessionId) => api.delete(`/analysis/${sessionId}`),
};

// Approvals API
export const approvalsApi = {
  list: () => api.get('/approvals'),
  get: (approvalId) => api.get(`/approvals/${approvalId}`),
  decide: (approvalId, decision) => api.post(`/approvals/${approvalId}/decide`, decision),
};

// Outputs API
export const outputsApi = {
  list: () => api.get('/outputs'),
  download: (filename) => api.get(`/outputs/${filename}`, { responseType: 'blob' }),
  getLatestReport: () => api.get('/outputs/report/latest', { responseType: 'blob' }),
  getLatestDashboard: () => api.get('/outputs/dashboard/latest', { responseType: 'blob' }),
};

// Statistics API
export const statisticsApi = {
  get: () => api.get('/statistics'),
  getAuditLogs: () => api.get('/audit/logs'),
};

// Health check
export const healthApi = {
  check: () => api.get('/health'),
};

// WebSocket connection helper
export const createWebSocket = (sessionId, onMessage, onError) => {
  const wsUrl = `ws://${window.location.host}/ws/${sessionId}`;
  const ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  ws.onerror = (error) => {
    if (onError) onError(error);
  };

  // Keepalive ping
  const pingInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }));
    }
  }, 30000);

  ws.onclose = () => {
    clearInterval(pingInterval);
  };

  return ws;
};

export default api;
