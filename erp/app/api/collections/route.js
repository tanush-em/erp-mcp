import connectDB from '@/lib/mongodb';

// Define the collections we want to show with their metadata
const COLLECTIONS = [
  {
    name: 'students',
    displayName: 'Students',
    description: 'Student information and details',
    icon: 'users'
  },
  {
    name: 'faculties',
    displayName: 'Faculties',
    description: 'Faculty and teacher information',
    icon: 'users'
  },
  {
    name: 'courses',
    displayName: 'Courses',
    description: 'Course catalog and information',
    icon: 'book'
  },
  {
    name: 'attendances',
    displayName: 'Attendance',
    description: 'Student attendance records',
    icon: 'calendar'
  },
  {
    name: 'leaverequests',
    displayName: 'Leave Requests',
    description: 'Student leave applications',
    icon: 'calendar'
  },
  {
    name: 'timetables',
    displayName: 'Timetable',
    description: 'Class schedules and timetables',
    icon: 'clock'
  }
];

export async function GET() {
  try {
    await connectDB();
    
    return Response.json({ 
      success: true, 
      collections: COLLECTIONS
    });
  } catch (error) {
    console.error('Error fetching collections:', error);
    return Response.json({ 
      success: false, 
      error: error.message 
    }, { status: 500 });
  }
}
