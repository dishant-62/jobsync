require('dotenv').config()
const express = require('express')
const helmet = require('helmet')
const cors = require('cors')
const cookieParser = require('cookie-parser')
const passport = require('./config/passport')
const connectDB = require('./config/db')
const authRoutes = require('./routes/auth')
const resumeRoutes = require('./routes/resume')

const app = express()

// ── Security headers ──────────────────────────────────────────────────────
app.use(helmet())

// ── CORS — allow the frontend origin with credentials ─────────────────────
const allowedOrigins = (process.env.FRONTEND_URL || 'http://localhost:5173').split(',')
app.use(
  cors({
    origin: (origin, cb) => {
      // Allow requests with no origin (e.g. curl, Postman) in development
      if (!origin || allowedOrigins.includes(origin)) return cb(null, true)
      cb(new Error(`CORS: origin '${origin}' is not allowed`))
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  })
)

// ── Body & cookie parsing ─────────────────────────────────────────────────
app.use(express.json())
app.use(express.urlencoded({ extended: false }))
app.use(cookieParser())

// ── Passport — stateless (no sessions; JWT only) ──────────────────────────
app.use(passport.initialize())

// ── Routes ────────────────────────────────────────────────────────────────
app.use('/auth', authRoutes)
app.use('/resume', resumeRoutes)

// ── Health check ──────────────────────────────────────────────────────────
app.get('/health', (_req, res) => res.json({ status: 'ok' }))

// ── 404 ───────────────────────────────────────────────────────────────────
app.use((_req, res) => res.status(404).json({ error: 'Not found' }))

// ── Global error handler ──────────────────────────────────────────────────
// eslint-disable-next-line no-unused-vars
app.use((err, _req, res, _next) => {
  console.error(err.stack)
  res.status(500).json({ error: 'Internal server error' })
})

// ── Start ─────────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 4000
connectDB().then(() => {
  app.listen(PORT, () =>
    console.log(`Auth server running on http://localhost:${PORT}`)
  )
})
