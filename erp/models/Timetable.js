import mongoose from 'mongoose';

const timeSlotSchema = new mongoose.Schema({
  period: {
    type: Number,
    required: true
  },
  type: {
    type: String,
    enum: ['lecture', 'break', 'lab', 'tutorial'],
    required: true
  },
  courseCode: {
    type: String,
    required: true
  },
  course: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Course'
  },
  faculty: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Faculty'
  },
  room: {
    type: String
  }
});

const timetableSchema = new mongoose.Schema({
  dayOfWeek: {
    type: String,
    enum: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    required: true
  },
  slots: [timeSlotSchema],
  semester: {
    type: Number,
    required: true
  },
  isActive: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true
});

export default mongoose.models.Timetable || mongoose.model('Timetable', timetableSchema);
