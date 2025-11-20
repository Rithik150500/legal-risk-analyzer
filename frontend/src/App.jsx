import React from 'react';
import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import {
  FileText,
  BarChart3,
  Shield,
  CheckCircle,
  Download,
  Home,
  Settings,
  Scale
} from 'lucide-react';

// Pages
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Analysis from './pages/Analysis';
import Approvals from './pages/Approvals';
import Outputs from './pages/Outputs';

function App() {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/documents', icon: FileText, label: 'Documents' },
    { path: '/analysis', icon: BarChart3, label: 'Analysis' },
    { path: '/approvals', icon: CheckCircle, label: 'Approvals' },
    { path: '/outputs', icon: Download, label: 'Outputs' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <Scale className="h-8 w-8 text-blue-600" />
          <span className="ml-3 text-lg font-semibold text-gray-900">
            Legal Risk Analyzer
          </span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4">
          {navItems.map(({ path, icon: Icon, label }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `flex items-center px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'text-blue-600 bg-blue-50 border-r-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`
              }
            >
              <Icon className="h-5 w-5 mr-3" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            Legal Risk Analysis System
            <br />
            v1.0.0
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/approvals" element={<Approvals />} />
          <Route path="/outputs" element={<Outputs />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
