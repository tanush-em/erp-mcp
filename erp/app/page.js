'use client';

import { useState, useEffect } from 'react';
import { 
  Users, 
  Calendar, 
  BookOpen, 
  Clock, 
  UserCheck, 
  GraduationCap,
  Menu,
  X,
  Home as HomeIcon,
  BarChart3,
  Settings
} from 'lucide-react';

// Import specialized components
import AttendanceCalendar from './components/AttendanceCalendar';
import TimetableGrid from './components/TimetableGrid';
import StudentManagement from './components/StudentManagement';
import FacultyManagement from './components/FacultyManagement';
import LeaveRequests from './components/LeaveRequests';
import CourseManagement from './components/CourseManagement';
import Dashboard from './components/Dashboard';

export default function ERPPortal() {
  const [activeFeature, setActiveFeature] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const features = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: HomeIcon,
      description: 'Overview and Analytics'
    },
    {
      id: 'attendance',
      name: 'Attendance',
      icon: Calendar,
      description: 'Monthly Calendar View'
    },
    {
      id: 'timetable',
      name: 'Timetable',
      icon: Clock,
      description: 'Weekly Timetable and Schedule'
    },
    {
      id: 'students',
      name: 'Students',
      icon: GraduationCap,
      description: 'Student Database'
    },
    {
      id: 'faculty',
      name: 'Faculty',
      icon: UserCheck,
      description: 'Faculty Database '
    },
    {
      id: 'leaves',
      name: 'Leave Requests',
      icon: BookOpen,
      description: 'Leave Applications and Approvals'
    },
    {
      id: 'courses',
      name: 'Courses',
      icon: BookOpen,
      description: 'Course Management & Subject Handling'
    }
  ];

  const renderActiveComponent = () => {
    switch (activeFeature) {
      case 'dashboard':
        return <Dashboard />;
      case 'attendance':
        return <AttendanceCalendar />;
      case 'timetable':
        return <TimetableGrid />;
      case 'students':
        return <StudentManagement />;
      case 'faculty':
        return <FacultyManagement />;
      case 'leaves':
        return <LeaveRequests />;
      case 'courses':
        return <CourseManagement />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 lg:flex">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:flex-shrink-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">ERP Portal</h1>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-md hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="p-4 space-y-2">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <button
                key={feature.id}
                onClick={() => {
                  setActiveFeature(feature.id);
                  setSidebarOpen(false);
                }}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeFeature === feature.id
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50 text-gray-700'
                }`}
              >
                <Icon className="w-5 h-5" />
                <div className="flex-1">
                  <div className="font-medium">{feature.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{feature.description}</div>
                </div>
              </button>
            );
          })}
        </nav>

        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <Settings className="w-5 h-5 text-gray-500" />
              <div>
                <div className="text-sm font-medium text-gray-900">Settings</div>
                <div className="text-xs text-gray-500">System configuration</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:flex-1 min-h-screen">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="lg:hidden p-2 rounded-md hover:bg-gray-100"
                >
                  <Menu className="w-5 h-5" />
                </button>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {features.find(f => f.id === activeFeature)?.name || 'Dashboard'}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {features.find(f => f.id === activeFeature)?.description || 'Overview and analytics'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="p-4 sm:p-6 lg:p-8">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <div className="mt-2 text-sm text-red-700">{error}</div>
                </div>
              </div>
            </div>
          )}

          {renderActiveComponent()}
        </main>
      </div>
    </div>
  );
}
