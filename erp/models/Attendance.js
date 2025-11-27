import mongoose from 'mongoose';

const attendanceSchema = new mongoose.Schema({
  student: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Student',
    required: true
  },
  studentRoll: {
    type: Number,
    required: true
  },
  month: {
    type: String,
    required: true // Format: "January 2025"
  },
  year: {
    type: Number,
    required: true
  },
  attendance: [{
    date: {
      type: Date,
      required: true
    },
    status: {
      type: String,
      enum: ['P', 'A', 'DNM'], // Present, Absent, Do Not Mark
      required: true
    }
  }],
  totalDays: {
    type: Number,
    default: 0
  },
  presentDays: {
    type: Number,
    default: 0
  },
  absentDays: {
    type: Number,
    default: 0
  },
  attendancePercentage: {
    type: Number,
    default: 0
  }
}, {
  timestamps: true
});

// Compound index for efficient queries
attendanceSchema.index({ studentRoll: 1, month: 1, year: 1 }, { unique: true });

export default mongoose.models.Attendance || mongoose.model('Attendance', attendanceSchema);
