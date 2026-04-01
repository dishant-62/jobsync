const passport = require('passport')
const GoogleStrategy = require('passport-google-oauth20').Strategy
const LinkedInStrategy = require('passport-linkedin-oauth2').Strategy
const LocalStrategy = require('passport-local').Strategy
const User = require('../models/User')

// ── Helper: find existing user or create a new one from OAuth data ────────
async function findOrCreateOAuthUser({ email, name, provider, provider_id, profile_pic }) {
  // 1. Try exact match on provider + provider_id (fastest path)
  let user = await User.findOne({ provider, provider_id })
  if (user) return user

  // 2. Same email already registered under any provider → link the account
  user = await User.findOne({ email })
  if (user) {
    user.provider_id = provider_id
    if (!user.profile_pic && profile_pic) user.profile_pic = profile_pic
    await user.save()
    return user
  }

  // 3. Brand-new user
  return User.create({ email, name, provider, provider_id, profile_pic })
}

// ── Google Strategy ───────────────────────────────────────────────────────
passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: process.env.GOOGLE_CALLBACK_URL || 'http://localhost:4000/auth/google/callback',
    },
    async (_accessToken, _refreshToken, profile, done) => {
      try {
        const email = profile.emails?.[0]?.value
        if (!email) return done(new Error('Google account has no email address'), null)

        const user = await findOrCreateOAuthUser({
          email,
          name: profile.displayName,
          provider: 'google',
          provider_id: profile.id,
          profile_pic: profile.photos?.[0]?.value ?? null,
        })

        done(null, user)
      } catch (err) {
        done(err, null)
      }
    }
  )
)

// ── LinkedIn Strategy ─────────────────────────────────────────────────────
// Uses OpenID Connect scopes supported by the current LinkedIn API.
passport.use(
  new LinkedInStrategy(
    {
      clientID: process.env.LINKEDIN_CLIENT_ID,
      clientSecret: process.env.LINKEDIN_CLIENT_SECRET,
      callbackURL: process.env.LINKEDIN_CALLBACK_URL || 'http://localhost:4000/auth/linkedin/callback',
      scope: ['openid', 'profile', 'email'],
    },
    async (_accessToken, _refreshToken, profile, done) => {
      try {
        const email = profile.emails?.[0]?.value
        if (!email) return done(new Error('LinkedIn account has no email address'), null)

        const user = await findOrCreateOAuthUser({
          email,
          name: profile.displayName,
          provider: 'linkedin',
          provider_id: profile.id,
          profile_pic: profile.photos?.[0]?.value ?? null,
        })

        done(null, user)
      } catch (err) {
        done(err, null)
      }
    }
  )
)

// ── Local (Email / Password) Strategy ────────────────────────────────────
passport.use(
  new LocalStrategy(
    { usernameField: 'email', passwordField: 'password' },
    async (email, password, done) => {
      try {
        const user = await User.findOne({ email: email.toLowerCase(), provider: 'local' })
        if (!user) return done(null, false, { message: 'Invalid email or password' })

        const valid = await user.comparePassword(password)
        if (!valid) return done(null, false, { message: 'Invalid email or password' })

        done(null, user)
      } catch (err) {
        done(err, null)
      }
    }
  )
)

module.exports = passport
