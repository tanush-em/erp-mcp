import mongoose from 'mongoose';

const leaveRequestSchema = new mongoose.Schema({
  student: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Student',
    required: true
  },
  studentRoll: {
    type: Number,
    required: true
  },
  startDate: {
    type: Date,
    required: true
  },
  endDate: {
    type: Date,
    required: true
  },
  reason: {
    type: String,
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'approved', 'rejected'],
    default: 'pending'
  },
  handledBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Faculty',
    default: null
  },
  handledAt: {
    type: Date,
    default: null
  },
  totalDays: {
    type: Number,
    required: true
  },
  comments: {
    type: String
  }
}, {
  timestamps: true
});

export default mongoose.models.LeaveRequest || mongoose.model('LeaveRequest', leaveRequestSchema);
