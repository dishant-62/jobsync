const mongoose = require('mongoose')

// ── Sub-schemas ───────────────────────────────────────────────────────────────

const contactSchema = new mongoose.Schema(
  {
    email: { type: String, default: '' },
    phone: { type: String, default: '' },
    location: { type: String, default: '' },
    linkedin: { type: String, default: '' },
    github: { type: String, default: '' },
    website: { type: String, default: '' },
  },
  { _id: false }
)

const educationSchema = new mongoose.Schema(
  {
    institution: { type: String, default: '' },
    degree: { type: String, default: '' },
    field: { type: String, default: '' },
    start_date: { type: String, default: '' },
    end_date: { type: String, default: '' },
    gpa: { type: String, default: '' },
    description: { type: String, default: '' },
  },
  { _id: false }
)

const experienceSchema = new mongoose.Schema(
  {
    company: { type: String, default: '' },
    title: { type: String, default: '' },
    location: { type: String, default: '' },
    start_date: { type: String, default: '' },
    end_date: { type: String, default: '' },
    is_current: { type: Boolean, default: false },
    bullets: { type: [String], default: [] },
  },
  { _id: false }
)

const projectSchema = new mongoose.Schema(
  {
    name: { type: String, default: '' },
    url: { type: String, default: '' },
    description: { type: String, default: '' },
    tech_stack: { type: [String], default: [] },
  },
  { _id: false }
)

const resumeContentSchema = new mongoose.Schema(
  {
    name: { type: String, default: '' },
    summary: { type: String, default: '' },
    contact: { type: contactSchema, default: () => ({}) },
    education: { type: [educationSchema], default: [] },
    experience: { type: [experienceSchema], default: [] },
    projects: { type: [projectSchema], default: [] },
    skills: { type: [String], default: [] },
  },
  { _id: false }
)

const suggestionSchema = new mongoose.Schema(
  {
    section: { type: String, required: true },
    type: { type: String, enum: ['urgent', 'critical', 'optional'], required: true },
    issue: { type: String, required: true },
    suggestion: { type: String, required: true },
    improved_text: { type: String, default: '' },
  },
  { _id: false }
)

// ── Main Resume schema ────────────────────────────────────────────────────────

const resumeSchema = new mongoose.Schema(
  {
    user_id: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true,
    },
    title: {
      type: String,
      required: true,
      trim: true,
    },
    target_job_title: {
      type: String,
      default: '',
      trim: true,
    },
    is_primary: {
      type: Boolean,
      default: false,
    },
    content: {
      type: resumeContentSchema,
      default: () => ({}),
    },
    score: {
      type: String,
      enum: ['A', 'B', 'C', 'D', 'F', null],
      default: null,
    },
    score_label: {
      type: String,
      default: null,
    },
    analysis_summary: {
      type: String,
      default: null,
    },
    suggestions: {
      type: [suggestionSchema],
      default: [],
    },
    analysis_status: {
      type: String,
      enum: ['pending', 'analyzing', 'complete', 'error'],
      default: 'pending',
    },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
  }
)

// Ensure only one primary per user
resumeSchema.index({ user_id: 1, is_primary: 1 })

module.exports = mongoose.model('Resume', resumeSchema)
