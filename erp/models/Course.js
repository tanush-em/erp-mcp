import mongoose from 'mongoose';

const courseSchema = new mongoose.Schema({
  code: {
    type: String,
    required: true,
    unique: true
  },
  title: {
    type: String,
    required: true
  },
  credits: {
    type: Number,
    required: true
  },
  semester: {
    type: Number,
    required: true
  },
  description: {
    type: String
  },
  facultyInCharge: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Faculty'
  },
  isActive: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true
});

export default mongoose.models.Course || mongoose.model('Course', courseSchema);
