const { body, param, validationResult } = require('express-validator')
const Resume = require('../models/Resume')
const { analyzeResume } = require('./aiController')

const MAX_RESUMES_PER_USER = 5

// ── Helpers ───────────────────────────────────────────────────────────────────

function validate(req, res) {
  const errors = validationResult(req)
  if (!errors.isEmpty()) {
    res.status(422).json({ errors: errors.array() })
    return false
  }
  return true
}

// ── List resumes for current user ─────────────────────────────────────────────

exports.list = async (req, res) => {
  try {
    const resumes = await Resume.find({ user_id: req.user._id })
      .select('-suggestions -content')
      .sort({ is_primary: -1, updated_at: -1 })
    res.json({ resumes, total: resumes.length, slots: MAX_RESUMES_PER_USER })
  } catch (err) {
    console.error('Resume list error:', err)
    res.status(500).json({ error: 'Failed to fetch resumes' })
  }
}

// ── Get single resume (full detail) ──────────────────────────────────────────

exports.getOne = async (req, res) => {
  try {
    const resume = await Resume.findOne({ _id: req.params.id, user_id: req.user._id })
    if (!resume) return res.status(404).json({ error: 'Resume not found' })
    res.json({ resume })
  } catch (err) {
    console.error('Resume getOne error:', err)
    res.status(500).json({ error: 'Failed to fetch resume' })
  }
}

// ── Create resume ─────────────────────────────────────────────────────────────

exports.createValidation = [
  body('title').trim().notEmpty().withMessage('Title is required'),
  body('target_job_title').optional().trim(),
  body('content').optional().isObject().withMessage('Content must be an object'),
]

exports.create = async (req, res) => {
  if (!validate(req, res)) return

  try {
    const count = await Resume.countDocuments({ user_id: req.user._id })
    if (count >= MAX_RESUMES_PER_USER) {
      return res.status(429).json({
        error: `You have reached the ${MAX_RESUMES_PER_USER}-resume limit. Delete one to add another.`,
      })
    }

    const { title, target_job_title, content } = req.body

    // First resume created → make it primary automatically
    const shouldBePrimary = count === 0

    const resume = await Resume.create({
      user_id: req.user._id,
      title,
      target_job_title: target_job_title || '',
      content: content || {},
      is_primary: shouldBePrimary,
    })

    res.status(201).json({ resume })
  } catch (err) {
    console.error('Resume create error:', err)
    res.status(500).json({ error: 'Failed to create resume' })
  }
}

// ── Update resume ─────────────────────────────────────────────────────────────

exports.updateValidation = [
  param('id').isMongoId().withMessage('Invalid resume ID'),
  body('title').optional().trim().notEmpty().withMessage('Title cannot be empty'),
  body('target_job_title').optional().trim(),
  body('content').optional().isObject().withMessage('Content must be an object'),
]

exports.update = async (req, res) => {
  if (!validate(req, res)) return

  try {
    const allowed = ['title', 'target_job_title', 'content']
    const updates = {}
    allowed.forEach((key) => {
      if (req.body[key] !== undefined) updates[key] = req.body[key]
    })

    const resume = await Resume.findOneAndUpdate(
      { _id: req.params.id, user_id: req.user._id },
      { $set: updates },
      { new: true }
    )
    if (!resume) return res.status(404).json({ error: 'Resume not found' })
    res.json({ resume })
  } catch (err) {
    console.error('Resume update error:', err)
    res.status(500).json({ error: 'Failed to update resume' })
  }
}

// ── Delete resume ─────────────────────────────────────────────────────────────

exports.remove = async (req, res) => {
  try {
    const resume = await Resume.findOneAndDelete({ _id: req.params.id, user_id: req.user._id })
    if (!resume) return res.status(404).json({ error: 'Resume not found' })

    // If deleted resume was primary, promote the newest remaining one
    if (resume.is_primary) {
      const next = await Resume.findOne({ user_id: req.user._id }).sort({ updated_at: -1 })
      if (next) await Resume.updateOne({ _id: next._id }, { $set: { is_primary: true } })
    }

    res.json({ message: 'Resume deleted' })
  } catch (err) {
    console.error('Resume delete error:', err)
    res.status(500).json({ error: 'Failed to delete resume' })
  }
}

// ── Set primary ───────────────────────────────────────────────────────────────

exports.setPrimary = async (req, res) => {
  try {
    const resume = await Resume.findOne({ _id: req.params.id, user_id: req.user._id })
    if (!resume) return res.status(404).json({ error: 'Resume not found' })

    // Clear existing primary then set the requested one
    await Resume.updateMany({ user_id: req.user._id }, { $set: { is_primary: false } })
    await Resume.updateOne({ _id: resume._id }, { $set: { is_primary: true } })

    res.json({ message: 'Primary resume updated' })
  } catch (err) {
    console.error('Resume setPrimary error:', err)
    res.status(500).json({ error: 'Failed to update primary resume' })
  }
}

// ── Trigger AI analysis ───────────────────────────────────────────────────────

exports.analyze = async (req, res) => {
  try {
    const resume = await Resume.findOne({ _id: req.params.id, user_id: req.user._id })
    if (!resume) return res.status(404).json({ error: 'Resume not found' })

    // Mark as analyzing immediately so client can show loading state
    await Resume.updateOne({ _id: resume._id }, { $set: { analysis_status: 'analyzing' } })

    const result = await analyzeResume(resume.content, resume.target_job_title)

    const updated = await Resume.findByIdAndUpdate(
      resume._id,
      {
        $set: {
          score: result.score,
          score_label: result.score_label,
          analysis_summary: result.summary,
          suggestions: result.suggestions,
          analysis_status: 'complete',
        },
      },
      { new: true }
    )

    res.json({ resume: updated })
  } catch (err) {
    console.error('Resume analyze error:', err)
    await Resume.updateOne({ _id: req.params.id }, { $set: { analysis_status: 'error' } }).catch(
      () => {}
    )
    res.status(500).json({ error: 'Analysis failed — please try again' })
  }
}
