const jwt = require('jsonwebtoken')
const passport = require('passport')
const { body, validationResult } = require('express-validator')
const User = require('../models/User')

// ── Cookie options ─────────────────────────────────────────────────────────
const COOKIE_OPTIONS = {
  httpOnly: true,                                            // never readable by JS
  secure: process.env.NODE_ENV === 'production',            // HTTPS only in prod
  sameSite: process.env.NODE_ENV === 'production' ? 'none' : 'lax',
  maxAge: 7 * 24 * 60 * 60 * 1000,                        // 7 days in ms
  path: '/',
}

// ── JWT signing ────────────────────────────────────────────────────────────
function signToken(user) {
  return jwt.sign(
    { sub: user._id.toString(), email: user.email },
    process.env.JWT_SECRET,
    { expiresIn: '7d' }
  )
}

// ── Issue token, set cookie, redirect to frontend ─────────────────────────
function issueTokenRedirect(res, user) {
  const token = signToken(user)
  res.cookie('token', token, COOKIE_OPTIONS)
  const origin = process.env.FRONTEND_URL || 'http://localhost:5173'
  res.redirect(`${origin}/auth/callback?success=true`)
}

// ─────────────────────────────────────────────────────────────────────────────
// OAuth success  (Google / LinkedIn)
// ─────────────────────────────────────────────────────────────────────────────
exports.oauthSuccess = (req, res) => {
  issueTokenRedirect(res, req.user)
}

// ─────────────────────────────────────────────────────────────────────────────
// OAuth failure
// ─────────────────────────────────────────────────────────────────────────────
exports.oauthFailure = (_req, res) => {
  const origin = process.env.FRONTEND_URL || 'http://localhost:5173'
  res.redirect(`${origin}/auth/callback?error=oauth_failed`)
}

// ─────────────────────────────────────────────────────────────────────────────
// Register  (email / password)
// ─────────────────────────────────────────────────────────────────────────────
exports.registerValidation = [
  body('name').trim().notEmpty().withMessage('Name is required'),
  body('email').isEmail().normalizeEmail().withMessage('A valid email is required'),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters'),
]

exports.register = async (req, res) => {
  const errors = validationResult(req)
  if (!errors.isEmpty()) {
    return res.status(422).json({ errors: errors.array() })
  }

  const { name, email, password } = req.body

  try {
    const existing = await User.findOne({ email: email.toLowerCase() })
    if (existing) {
      return res.status(409).json({ error: 'An account with this email already exists' })
    }

    // Password is hashed inside the pre-save hook on User
    const user = await User.create({ name, email, provider: 'local', password })
    const token = signToken(user)
    res.cookie('token', token, COOKIE_OPTIONS)
    res.status(201).json({ user })
  } catch (err) {
    console.error('Register error:', err)
    res.status(500).json({ error: 'Registration failed — please try again' })
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Login  (email / password)
// ─────────────────────────────────────────────────────────────────────────────
exports.loginValidation = [
  body('email').isEmail().normalizeEmail().withMessage('A valid email is required'),
  body('password').notEmpty().withMessage('Password is required'),
]

exports.login = (req, res, next) => {
  const errors = validationResult(req)
  if (!errors.isEmpty()) {
    return res.status(422).json({ errors: errors.array() })
  }

  passport.authenticate('local', { session: false }, (err, user, info) => {
    if (err) return next(err)
    if (!user) {
      return res.status(401).json({ error: info?.message || 'Invalid credentials' })
    }

    const token = signToken(user)
    res.cookie('token', token, COOKIE_OPTIONS)
    res.json({ user })
  })(req, res, next)
}

// ─────────────────────────────────────────────────────────────────────────────
// Logout
// ─────────────────────────────────────────────────────────────────────────────
exports.logout = (_req, res) => {
  res.clearCookie('token', { path: '/' })
  res.json({ message: 'Signed out successfully' })
}

// ─────────────────────────────────────────────────────────────────────────────
// Current user  (requires requireAuth middleware)
// ─────────────────────────────────────────────────────────────────────────────
exports.me = (req, res) => {
  res.json({ user: req.user })
}
