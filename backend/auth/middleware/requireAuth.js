const jwt = require('jsonwebtoken')
const User = require('../models/User')

/**
 * Protect a route by requiring a valid JWT cookie.
 * Attaches the Mongoose user document to req.user on success.
 */
const requireAuth = async (req, res, next) => {
  try {
    const token = req.cookies?.token
    if (!token) {
      return res.status(401).json({ error: 'Authentication required' })
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    const user = await User.findById(decoded.sub)
    if (!user) {
      return res.status(401).json({ error: 'User no longer exists' })
    }

    req.user = user
    next()
  } catch {
    // jwt.verify throws on invalid/expired tokens
    res.status(401).json({ error: 'Invalid or expired session' })
  }
}

module.exports = requireAuth
