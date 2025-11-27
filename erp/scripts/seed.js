import connectDB from '../lib/mongodb.js';
import Student from '../models/Student.js';
import Faculty from '../models/Faculty.js';
import Course from '../models/Course.js';
import Attendance from '../models/Attendance.js';
import LeaveRequest from '../models/LeaveRequest.js';
import Timetable from '../models/Timetable.js';

async function seedDatabase() {
  try {
    await connectDB();
    console.log('Connected to MongoDB');

    // Clear existing data
    await Student.deleteMany({});
    await Faculty.deleteMany({});
    await Course.deleteMany({});
    await Attendance.deleteMany({});
    await LeaveRequest.deleteMany({});
    await Timetable.deleteMany({});
    console.log('Cleared existing data');

    // Create Students
    const students = await Student.create([
      {
        roll: 1,
        fullName: "Aisha Khan",
        email: "aisha@college.edu",
        phone: "+91-9876543210"
      },
      {
        roll: 43,
        fullName: "Tanush",
        email: "tanush@college.edu",
        phone: "+91-240394798"
      },
      {
        roll: 15,
        fullName: "Priya Sharma",
        email: "priya@college.edu",
        phone: "+91-9876543211"
      },
      {
        roll: 28,
        fullName: "Rajesh Kumar",
        email: "rajesh@college.edu",
        phone: "+91-9876543212"
      }
    ]);
    console.log('Created students:', students.length);

    // Create Faculties
    const faculties = await Faculty.create([
      {
        employeeId: "FAC-01",
        fullName: "Dr.S.Vanaja",
        email: "s.vanaja@college.edu",
        designation: "Associate Professor",
        subjectsHandled: ["DL", "NOSQL", "SCM", "COU", "EAI"]
      },
      {
        employeeId: "FAC-02",
        fullName: "Dr.R.Kumar",
        email: "r.kumar@college.edu",
        designation: "Professor",
        subjectsHandled: ["AI", "ML", "DL", "NLP"]
      },
      {
        employeeId: "FAC-03",
        fullName: "Prof.S.Rajesh",
        email: "s.rajesh@college.edu",
        designation: "Assistant Professor",
        subjectsHandled: ["DBMS", "NOSQL", "SCM"]
      }
    ]);
    console.log('Created faculties:', faculties.length);

    // Create Courses
    const courses = await Course.create([
      {
        code: "191CAC701T",
        title: "Deep Learning (PE-III)",
        credits: 3,
        semester: 7,
        description: "Deep Learning concepts and applications",
        facultyInCharge: faculties[0]._id
      },
      {
        code: "191CAC702T",
        title: "NoSQL Databases",
        credits: 3,
        semester: 7,
        description: "NoSQL database systems and applications",
        facultyInCharge: faculties[0]._id
      },
      {
        code: "191CAC703T",
        title: "Supply Chain Management",
        credits: 3,
        semester: 7,
        description: "Supply chain optimization and management",
        facultyInCharge: faculties[2]._id
      },
      {
        code: "191CAC704T",
        title: "Computer Organization & Architecture",
        credits: 4,
        semester: 7,
        description: "Computer system organization and architecture",
        facultyInCharge: faculties[0]._id
      },
      {
        code: "191CAC705T",
        title: "Enterprise Application Integration",
        credits: 3,
        semester: 7,
        description: "EAI concepts and implementation",
        facultyInCharge: faculties[0]._id
      }
    ]);
    console.log('Created courses:', courses.length);

    // Create Attendance Records
    const attendanceRecords = [];
    const months = ['January', 'February', 'March', 'April', 'May', 'June'];
    const year = 2025;
    
    // Sample attendance pattern: P,A,P,P,P,A,P,P,P,A,P,A,P,P,P,A,P,P,P,A,A,P,A,P,P,P,A,P,P,P
    const attendancePattern = ['P','A','P','P','P','A','P','P','P','A','P','A','P','P','P','A','P','P','P','A','A','P','A','P','P','P','A','P','P','P'];
    
    for (const student of students) {
      for (let monthIndex = 0; monthIndex < months.length; monthIndex++) {
        const month = months[monthIndex];
        let attendanceData = [...attendancePattern];
        
        // June has DNM (Do Not Mark) for last 10 days
        if (month === 'June') {
          attendanceData = attendancePattern.slice(0, 20).concat(['DNM','DNM','DNM','DNM','DNM','DNM','DNM','DNM','DNM','DNM']);
        }
        
        // Create attendance records for each day
        const attendanceEntries = attendanceData.map((status, dayIndex) => ({
          date: new Date(year, monthIndex, dayIndex + 1),
          status: status
        }));
        
        // Calculate statistics
        const totalDays = attendanceEntries.length;
        const presentDays = attendanceEntries.filter(entry => entry.status === 'P').length;
        const absentDays = attendanceEntries.filter(entry => entry.status === 'A').length;
        const attendancePercentage = totalDays > 0 ? (presentDays / totalDays) * 100 : 0;
        
        const attendanceRecord = await Attendance.create({
          student: student._id,
          studentRoll: student.roll,
          month: `${month} ${year}`,
          year: year,
          attendance: attendanceEntries,
          totalDays: totalDays,
          presentDays: presentDays,
          absentDays: absentDays,
          attendancePercentage: Math.round(attendancePercentage * 100) / 100
        });
        
        attendanceRecords.push(attendanceRecord);
      }
    }
    console.log('Created attendance records:', attendanceRecords.length);

    // Create Leave Requests
    const leaveRequests = await LeaveRequest.create([
      {
        student: students[1]._id, // Tanush
        studentRoll: students[1].roll,
        startDate: new Date('2024-08-15'),
        endDate: new Date('2024-08-17'),
        reason: 'Medical - fever',
        totalDays: 3,
        status: 'pending'
      },
      {
        student: students[0]._id, // Aisha
        studentRoll: students[0].roll,
        startDate: new Date('2024-09-10'),
        endDate: new Date('2024-09-12'),
        reason: 'Family emergency',
        totalDays: 3,
        status: 'approved',
        handledBy: faculties[0]._id,
        handledAt: new Date('2024-09-09')
      },
      {
        student: students[2]._id, // Priya
        studentRoll: students[2].roll,
        startDate: new Date('2024-10-05'),
        endDate: new Date('2024-10-07'),
        reason: 'Personal work',
        totalDays: 3,
        status: 'pending'
      }
    ]);
    console.log('Created leave requests:', leaveRequests.length);

    // Create Timetable
    const timetable = await Timetable.create([
      {
        dayOfWeek: 'Monday',
        semester: 7,
        slots: [
          {
            period: 1,
            type: 'lecture',
            courseCode: 'DL',
            course: courses[0]._id,
            faculty: faculties[0]._id,
            room: 'A101'
          },
          {
            period: 2,
            type: 'lecture',
            courseCode: 'NOSQL',
            course: courses[1]._id,
            faculty: faculties[0]._id,
            room: 'A102'
          },
          {
            period: 3,
            type: 'break',
            courseCode: 'BREAK',
            room: 'Cafeteria'
          },
          {
            period: 4,
            type: 'lecture',
            courseCode: 'DL',
            course: courses[0]._id,
            faculty: faculties[0]._id,
            room: 'A101'
          },
          {
            period: 5,
            type: 'lecture',
            courseCode: 'SCM',
            course: courses[2]._id,
            faculty: faculties[2]._id,
            room: 'A103'
          },
          {
            period: 6,
            type: 'lecture',
            courseCode: 'SCM',
            course: courses[2]._id,
            faculty: faculties[2]._id,
            room: 'A103'
          },
          {
            period: 7,
            type: 'break',
            courseCode: 'LUNCH',
            room: 'Cafeteria'
          },
          {
            period: 8,
            type: 'lecture',
            courseCode: 'COU',
            course: courses[3]._id,
            faculty: faculties[0]._id,
            room: 'A104'
          },
          {
            period: 9,
            type: 'lecture',
            courseCode: 'COU',
            course: courses[3]._id,
            faculty: faculties[0]._id,
            room: 'A104'
          },
          {
            period: 10,
            type: 'lecture',
            courseCode: 'EAI',
            course: courses[4]._id,
            faculty: faculties[0]._id,
            room: 'A105'
          }
        ]
      }
    ]);
    console.log('Created timetable records:', timetable.length);

    console.log('Database seeded successfully!');
    console.log('Summary:');
    console.log(`- Students: ${students.length}`);
    console.log(`- Faculties: ${faculties.length}`);
    console.log(`- Courses: ${courses.length}`);
    console.log(`- Attendance Records: ${attendanceRecords.length}`);
    console.log(`- Leave Requests: ${leaveRequests.length}`);
    console.log(`- Timetable Records: ${timetable.length}`);

  } catch (error) {
    console.error('Error seeding database:', error);
  } finally {
    process.exit(0);
  }
}

seedDatabase();
