const router = require('express').Router()
const passport = require('passport')
const rateLimit = require('express-rate-limit')
const controller = require('../controllers/authController')
const requireAuth = require('../middleware/requireAuth')

// ── Rate limiters ─────────────────────────────────────────────────────────
// Limit login / register to 10 attempts per 15 minutes per IP
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: { error: 'Too many requests — please try again in 15 minutes' },
  standardHeaders: true,
  legacyHeaders: false,
})

// ── Google OAuth ──────────────────────────────────────────────────────────
router.get(
  '/google',
  passport.authenticate('google', { scope: ['profile', 'email'], session: false })
)

router.get(
  '/google/callback',
  passport.authenticate('google', { session: false, failureRedirect: '/auth/failure' }),
  controller.oauthSuccess
)

// ── LinkedIn OAuth ────────────────────────────────────────────────────────
router.get(
  '/linkedin',
  passport.authenticate('linkedin', { session: false })
)

router.get(
  '/linkedin/callback',
  passport.authenticate('linkedin', { session: false, failureRedirect: '/auth/failure' }),
  controller.oauthSuccess
)

// ── OAuth failure fallback ────────────────────────────────────────────────
router.get('/failure', controller.oauthFailure)

// ── Local auth ────────────────────────────────────────────────────────────
router.post('/register', authLimiter, controller.registerValidation, controller.register)
router.post('/login',    authLimiter, controller.loginValidation,    controller.login)
router.post('/logout',   controller.logout)

// ── Session ───────────────────────────────────────────────────────────────
router.get('/me', requireAuth, controller.me)

module.exports = router
