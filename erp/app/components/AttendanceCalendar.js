'use client';

import { useState, useEffect } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar, 
  Users, 
  CheckCircle, 
  XCircle, 
  Minus,
  Filter,
  Download,
  Search
} from 'lucide-react';

export default function AttendanceCalendar() {
  const [attendanceData, setAttendanceData] = useState([]);
  const [students, setStudents] = useState([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAttendanceData();
    fetchStudents();
  }, [currentDate]);

  const fetchAttendanceData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/data/attendance');
      const data = await response.json();
      if (data.success) {
        setAttendanceData(data.data);
      }
    } catch (error) {
      console.error('Error fetching attendance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async () => {
    try {
      const response = await fetch('/api/data/students');
      const data = await response.json();
      if (data.success) {
        setStudents(data.data);
      }
    } catch (error) {
      console.error('Error fetching students:', error);
    }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getAttendanceForDate = (date, studentRoll) => {
    if (!studentRoll) return null;
    
    const monthYear = date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    const attendanceRecord = attendanceData.find(record => 
      record.studentRoll === studentRoll && 
      record.month === monthYear
    );
    
    if (!attendanceRecord) return null;
    
    const dayAttendance = attendanceRecord.attendance.find(att => 
      new Date(att.date).toDateString() === date.toDateString()
    );
    
    return dayAttendance ? dayAttendance.status : null;
  };

  const getAttendanceColor = (status) => {
    switch (status) {
      case 'P':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'A':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'DNM':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-50 text-gray-500 border-gray-200';
    }
  };

  const getAttendanceIcon = (status) => {
    switch (status) {
      case 'P':
        return <CheckCircle className="w-3 h-3" />;
      case 'A':
        return <XCircle className="w-3 h-3" />;
      case 'DNM':
        return <Minus className="w-3 h-3" />;
      default:
        return null;
    }
  };

  const getAttendanceStats = (studentRoll) => {
    const monthYear = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    const attendanceRecord = attendanceData.find(record => 
      record.studentRoll === studentRoll && 
      record.month === monthYear
    );
    
    if (!attendanceRecord) {
      return { present: 0, absent: 0, total: 0, percentage: 0 };
    }
    
    return {
      present: attendanceRecord.presentDays,
      absent: attendanceRecord.absentDays,
      total: attendanceRecord.totalDays,
      percentage: attendanceRecord.attendancePercentage
    };
  };

  const filteredStudents = students.filter(student => 
    student.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.roll.toString().includes(searchTerm)
  );

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const navigateMonth = (direction) => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      newDate.setMonth(prev.getMonth() + direction);
      return newDate;
    });
  };

  const days = getDaysInMonth(currentDate);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border p-6 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-6 animate-pulse">
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex items-center space-x-4">
            <Calendar className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Attendance Calendar</h2>
              <p className="text-sm text-gray-500">Monthly attendance overview</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigateMonth(-1)}
                className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-lg font-medium text-gray-900 min-w-[140px] text-center">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </span>
              <button
                onClick={() => navigateMonth(1)}
                className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
            
            <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
            
            <button className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
              <Filter className="w-4 h-4" />
              <span>Bulk Mark</span>
            </button>
          </div>
        </div>
      </div>

      {/* Student Selection */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 mb-6">
          <div className="flex items-center space-x-4">
            <Users className="w-5 h-5 text-gray-500" />
            <h3 className="text-lg font-medium text-gray-900">Select Student</h3>
          </div>
          
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search students..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredStudents.map((student) => {
            const stats = getAttendanceStats(student.roll);
            return (
              <button
                key={student._id}
                onClick={() => setSelectedStudent(student)}
                className={`p-4 rounded-lg border text-left transition-colors ${
                  selectedStudent?._id === student._id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium text-gray-900">{student.fullName}</div>
                  <div className="text-sm text-gray-500">Roll: {student.roll}</div>
                </div>
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-1">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-green-600">{stats.present}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <XCircle className="w-4 h-4 text-red-500" />
                    <span className="text-red-600">{stats.absent}</span>
                  </div>
                  <div className="text-gray-600">
                    {stats.percentage.toFixed(1)}%
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Attendance Summary */}
      {selectedStudent && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Attendance Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-8 h-8 text-green-600" />
                <div>
                  <p className="text-sm font-medium text-green-800">Present Days</p>
                  <p className="text-2xl font-bold text-green-900">{getAttendanceStats(selectedStudent.roll).present}</p>
                </div>
              </div>
            </div>
            <div className="bg-red-50 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <XCircle className="w-8 h-8 text-red-600" />
                <div>
                  <p className="text-sm font-medium text-red-800">Absent Days</p>
                  <p className="text-2xl font-bold text-red-900">{getAttendanceStats(selectedStudent.roll).absent}</p>
                </div>
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <Calendar className="w-8 h-8 text-blue-600" />
                <div>
                  <p className="text-sm font-medium text-blue-800">Total Days</p>
                  <p className="text-2xl font-bold text-blue-900">{getAttendanceStats(selectedStudent.roll).total}</p>
                </div>
              </div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <Users className="w-8 h-8 text-purple-600" />
                <div>
                  <p className="text-sm font-medium text-purple-800">Percentage</p>
                  <p className="text-2xl font-bold text-purple-900">{getAttendanceStats(selectedStudent.roll).percentage.toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Calendar */}
      {selectedStudent && (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  {selectedStudent.fullName} - Roll {selectedStudent.roll}
                </h3>
                <p className="text-sm text-gray-500">
                  Attendance for {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
                </p>
              </div>
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-100 border border-green-200 rounded"></div>
                  <span className="text-gray-600">Present</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-100 border border-red-200 rounded"></div>
                  <span className="text-gray-600">Absent</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-gray-100 border border-gray-200 rounded"></div>
                  <span className="text-gray-600">Not Marked</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-7 gap-1 mb-4">
              {dayNames.map((day) => (
                <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
                  {day}
                </div>
              ))}
            </div>
            
            <div className="grid grid-cols-7 gap-1">
              {days.map((day, index) => {
                if (!day) {
                  return <div key={index} className="h-12"></div>;
                }
                
                const attendance = getAttendanceForDate(day, selectedStudent.roll);
                const isToday = day.toDateString() === new Date().toDateString();
                
                return (
                  <div
                    key={index}
                    className={`h-12 border rounded-lg flex items-center justify-center text-sm font-medium transition-colors ${
                      isToday 
                        ? 'ring-2 ring-blue-500' 
                        : attendance 
                          ? getAttendanceColor(attendance)
                          : 'bg-gray-50 text-gray-400 border-gray-200'
                    }`}
                  >
                    <div className="flex flex-col items-center">
                      <span className="text-xs">{day.getDate()}</span>
                      {attendance && getAttendanceIcon(attendance)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
