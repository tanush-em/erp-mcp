'use client';

import { useState, useEffect } from 'react';
import { 
  Users, 
  Calendar, 
  BookOpen, 
  Clock, 
  TrendingUp, 
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    students: 0,
    faculty: 0,
    courses: 0,
    attendance: 0,
    pendingLeaves: 0,
    totalLeaves: 0
  });
  const [loading, setLoading] = useState(true);
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch all collections data
      const [studentsRes, facultyRes, coursesRes, attendanceRes, leavesRes] = await Promise.all([
        fetch('/api/data/students'),
        fetch('/api/data/faculty'),
        fetch('/api/data/courses'),
        fetch('/api/data/attendance'),
        fetch('/api/data/leaverequests')
      ]);

      const [studentsData, facultyData, coursesData, attendanceData, leavesData] = await Promise.all([
        studentsRes.json(),
        facultyRes.json(),
        coursesRes.json(),
        attendanceRes.json(),
        leavesRes.json()
      ]);

      const pendingLeaves = leavesData.success ? 
        leavesData.data.filter(leave => leave.status === 'pending').length : 0;

      setStats({
        students: studentsData.success ? studentsData.data.length : 0,
        faculty: facultyData.success ? facultyData.data.length : 0,
        courses: coursesData.success ? coursesData.data.length : 0,
        attendance: attendanceData.success ? attendanceData.data.length : 0,
        pendingLeaves,
        totalLeaves: leavesData.success ? leavesData.data.length : 0
      });

      // Generate recent activity
      const activities = [];
      if (leavesData.success) {
        leavesData.data.slice(0, 5).forEach(leave => {
          activities.push({
            type: 'leave',
            message: `Leave request from Student ${leave.studentRoll}`,
            status: leave.status,
            date: new Date(leave.createdAt).toLocaleDateString()
          });
        });
      }
      setRecentActivity(activities);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Students',
      value: stats.students,
      icon: Users,
      color: 'blue',
      change: '+12%'
    },
    {
      title: 'Faculty Members',
      value: stats.faculty,
      icon: BookOpen,
      color: 'green',
      change: '+5%'
    },
    {
      title: 'Active Courses',
      value: stats.courses,
      icon: Clock,
      color: 'purple',
      change: '+8%'
    },
    {
      title: 'Attendance Records',
      value: stats.attendance,
      icon: Calendar,
      color: 'orange',
      change: '+15%'
    },
    {
      title: 'Pending Leaves',
      value: stats.pendingLeaves,
      icon: AlertCircle,
      color: 'red',
      change: `${stats.pendingLeaves > 0 ? '+' : ''}${stats.pendingLeaves}`
    },
    {
      title: 'Total Leave Requests',
      value: stats.totalLeaves,
      icon: TrendingUp,
      color: 'indigo',
      change: '+3%'
    }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'pending':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'text-green-600 bg-green-50';
      case 'rejected':
        return 'text-red-600 bg-red-50';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-sm border p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                  <p className={`text-sm mt-1 ${
                    stat.color === 'red' ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {stat.change} from last month
                  </p>
                </div>
                <div className={`p-3 rounded-lg bg-${stat.color}-50`}>
                  <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Attendance Overview */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-900">Attendance Overview</h3>
            <p className="text-sm text-gray-500">Monthly attendance trends</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-600">Overall Attendance</span>
                <span className="text-2xl font-bold text-green-600">85.2%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{width: '85.2%'}}></div>
              </div>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-green-600">92%</div>
                  <div className="text-xs text-gray-500">Present</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-red-600">6%</div>
                  <div className="text-xs text-gray-500">Absent</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-600">2%</div>
                  <div className="text-xs text-gray-500">Not Marked</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Course Distribution */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-900">Course Distribution</h3>
            <p className="text-sm text-gray-500">Courses by semester</p>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {[1, 2, 3, 4, 5, 6, 7, 8].map(semester => (
                <div key={semester} className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Semester {semester}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full" 
                        style={{width: `${Math.random() * 100}%`}}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-8">{Math.floor(Math.random() * 10) + 1}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
            <p className="text-sm text-gray-500">Latest system activities</p>
          </div>
          <div className="p-6">
            {recentActivity.length === 0 ? (
              <div className="text-center py-8">
                <AlertCircle className="w-8 h-8 mx-auto text-gray-400" />
                <p className="text-sm text-gray-500 mt-2">No recent activity</p>
              </div>
            ) : (
              <div className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    {getStatusIcon(activity.status)}
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                      <p className="text-xs text-gray-500">{activity.date}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(activity.status)}`}>
                      {activity.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
            <p className="text-sm text-gray-500">Common tasks and shortcuts</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 gap-4">
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
                <Calendar className="w-6 h-6 text-blue-600 mb-2" />
                <div className="text-sm font-medium text-gray-900">Mark Attendance</div>
                <div className="text-xs text-gray-500">Record daily attendance</div>
              </button>
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
                <BookOpen className="w-6 h-6 text-green-600 mb-2" />
                <div className="text-sm font-medium text-gray-900">Add Student</div>
                <div className="text-xs text-gray-500">Register new student</div>
              </button>
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
                <Clock className="w-6 h-6 text-purple-600 mb-2" />
                <div className="text-sm font-medium text-gray-900">View Timetable</div>
                <div className="text-xs text-gray-500">Check schedule</div>
              </button>
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
                <AlertCircle className="w-6 h-6 text-orange-600 mb-2" />
                <div className="text-sm font-medium text-gray-900">Process Leaves</div>
                <div className="text-xs text-gray-500">Review requests</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
