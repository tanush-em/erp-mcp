'use client';

import { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Users, 
  Clock
} from 'lucide-react';

export default function TimetableGrid() {
  const [timetables, setTimetables] = useState([]);
  const [courses, setCourses] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTimetableData();
    fetchCourses();
    fetchFaculty();
  }, []);

  const fetchTimetableData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/data/timetables');
      const data = await response.json();
      if (data.success) {
        setTimetables(data.data.filter(t => t.isActive));
      }
    } catch (error) {
      console.error('Error fetching timetable data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCourses = async () => {
    try {
      const response = await fetch('/api/data/courses');
      const data = await response.json();
      if (data.success) {
        setCourses(data.data);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
    }
  };

  const fetchFaculty = async () => {
    try {
      const response = await fetch('/api/data/faculty');
      const data = await response.json();
      if (data.success) {
        setFaculty(data.data);
      }
    } catch (error) {
      console.error('Error fetching faculty:', error);
    }
  };

  const getCourseInfo = (courseCode) => {
    return courses.find(course => course.code === courseCode);
  };

  const getFacultyInfo = (facultyId) => {
    return faculty.find(f => f._id === facultyId);
  };

  const getSlotColor = (type) => {
    switch (type) {
      case 'lecture':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'lab':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'tutorial':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'break':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSlotIcon = (type) => {
    switch (type) {
      case 'lecture':
        return <BookOpen className="w-4 h-4" />;
      case 'lab':
        return <Clock className="w-4 h-4" />;
      case 'tutorial':
        return <Users className="w-4 h-4" />;
      case 'break':
        return <Clock className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const periods = Array.from({ length: 10 }, (_, i) => i + 1);

  const getTimetableForDay = (day) => {
    return timetables.find(t => t.dayOfWeek === day);
  };

  const getSlotForPeriod = (dayTimetable, periodNumber) => {
    if (!dayTimetable) return null;
    return dayTimetable.slots.find(slot => slot.period === periodNumber);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border p-6 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-6 animate-pulse">
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center space-x-4">
          <Clock className="w-6 h-6 text-blue-600" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Timetable Grid</h2>
            <p className="text-sm text-gray-500">Weekly schedule overview</p>
          </div>
        </div>
      </div>

      {/* Timetable Grid */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                  Period
                </th>
                {days.map((day) => (
                  <th key={day} className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                    {day}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {periods.map((period) => (
                <tr key={period} className="hover:bg-gray-50">
                  <td className="px-4 py-4 text-sm font-medium text-gray-900">
                    <div className="text-center">
                      <div className="font-semibold">Period {period}</div>
                    </div>
                  </td>
                  {days.map((day) => {
                    const dayTimetable = getTimetableForDay(day);
                    const slot = getSlotForPeriod(dayTimetable, period);
                    
                    return (
                      <td key={day} className="px-2 py-2">
                        {slot ? (
                          <div className={`p-3 rounded-lg border text-center ${getSlotColor(slot.type)}`}>
                            <div className="flex items-center justify-center mb-1">
                              {getSlotIcon(slot.type)}
                            </div>
                            <div className="text-xs font-medium mb-1">{slot.courseCode}</div>
                            {slot.type !== 'break' && (
                              <>
                                <div className="text-xs opacity-75 mb-1">
                                  {getCourseInfo(slot.courseCode)?.title || 'Course'}
                                </div>
                                {slot.faculty && (
                                  <div className="text-xs opacity-75 mb-1">
                                    {getFacultyInfo(slot.faculty)?.fullName || 'Faculty'}
                                  </div>
                                )}
                              </>
                            )}
                          </div>
                        ) : (
                          <div className="p-3 rounded-lg border border-dashed border-gray-200 text-center">
                            <div className="text-xs text-gray-400">Free</div>
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
