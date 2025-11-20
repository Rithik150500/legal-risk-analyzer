import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  Clock,
  Activity,
  ArrowRight
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { statisticsApi, analysisApi } from '../api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, sessionsRes] = await Promise.all([
        statisticsApi.get(),
        analysisApi.list()
      ]);
      setStats(statsRes.data);
      setSessions(sessionsRes.data.sessions.slice(0, 5));
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const sessionStatusData = stats ? [
    { name: 'Completed', value: stats.sessions.completed, color: '#16A34A' },
    { name: 'Running', value: stats.sessions.running, color: '#2563EB' },
    { name: 'Failed', value: stats.sessions.failed, color: '#DC2626' }
  ].filter(d => d.value > 0) : [];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your legal risk analysis system</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={FileText}
          label="Documents"
          value={stats?.documents.total || 0}
          subtext={`${stats?.documents.pages || 0} pages total`}
          color="blue"
        />
        <StatCard
          icon={BarChart3}
          label="Analysis Sessions"
          value={stats?.sessions.total || 0}
          subtext={`${stats?.sessions.completed || 0} completed`}
          color="green"
        />
        <StatCard
          icon={CheckCircle}
          label="Pending Approvals"
          value={stats?.approvals.pending || 0}
          subtext="Awaiting review"
          color="orange"
        />
        <StatCard
          icon={Activity}
          label="Running"
          value={stats?.sessions.running || 0}
          subtext="Active analyses"
          color="purple"
        />
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Session Status Chart */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Session Status</h2>
          {sessionStatusData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sessionStatusData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sessionStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-4">
                {sessionStatusData.map((item, index) => (
                  <div key={index} className="flex items-center">
                    <div
                      className="w-3 h-3 rounded-full mr-2"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-sm text-gray-600">
                      {item.name} ({item.value})
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No analysis sessions yet
            </div>
          )}
        </div>

        {/* Recent Sessions */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Sessions</h2>
            <Link
              to="/analysis"
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
            >
              View all
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>
          {sessions.length > 0 ? (
            <div className="space-y-3">
              {sessions.map((session) => (
                <div
                  key={session.session_id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {session.session_id.substring(0, 8)}...
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(session.started_at).toLocaleString()}
                    </div>
                  </div>
                  <StatusBadge status={session.status} />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              No analysis sessions yet.
              <br />
              <Link to="/analysis" className="text-blue-600 hover:underline">
                Start your first analysis
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/documents"
            className="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <FileText className="w-6 h-6 text-blue-600 mr-3" />
            <div>
              <div className="font-medium text-gray-900">Upload Documents</div>
              <div className="text-sm text-gray-600">Add new documents to analyze</div>
            </div>
          </Link>
          <Link
            to="/analysis"
            className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <BarChart3 className="w-6 h-6 text-green-600 mr-3" />
            <div>
              <div className="font-medium text-gray-900">Start Analysis</div>
              <div className="text-sm text-gray-600">Begin risk assessment</div>
            </div>
          </Link>
          <Link
            to="/outputs"
            className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <Download className="w-6 h-6 text-purple-600 mr-3" />
            <div>
              <div className="font-medium text-gray-900">Download Reports</div>
              <div className="text-sm text-gray-600">Get generated reports</div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, subtext, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600',
    purple: 'bg-purple-50 text-purple-600',
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="ml-4">
          <div className="text-sm font-medium text-gray-600">{label}</div>
          <div className="text-2xl font-bold text-gray-900">{value}</div>
          <div className="text-xs text-gray-500">{subtext}</div>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const styles = {
    completed: 'bg-green-100 text-green-800',
    running: 'bg-blue-100 text-blue-800',
    failed: 'bg-red-100 text-red-800',
    initializing: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  );
}

export default Dashboard;
