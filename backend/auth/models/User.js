const mongoose = require('mongoose')
const bcrypt = require('bcrypt')

const SALT_ROUNDS = 10

const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
    },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
    },
    /** 'local' = email/password; 'google' | 'linkedin' = OAuth */
    provider: {
      type: String,
      enum: ['google', 'linkedin', 'local'],
      required: true,
    },
    /** OAuth provider's user ID — null for local accounts */
    provider_id: {
      type: String,
      default: null,
    },
    profile_pic: {
      type: String,
      default: null,
    },
    /** Only set for provider === 'local'. Hashed before save. */
    password: {
      type: String,
      default: null,
    },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
  }
)

// ── Password hashing ──────────────────────────────────────────────────────
userSchema.pre('save', async function (next) {
  if (!this.isModified('password') || !this.password) return next()
  this.password = await bcrypt.hash(this.password, SALT_ROUNDS)
  next()
})

// ── Compare plain-text password against stored hash ───────────────────────
userSchema.methods.comparePassword = async function (candidate) {
  if (!this.password) return false
  return bcrypt.compare(candidate, this.password)
}

// ── Strip sensitive fields from JSON output ───────────────────────────────
userSchema.methods.toJSON = function () {
  const obj = this.toObject()
  delete obj.password
  delete obj.__v
  return obj
}

module.exports = mongoose.model('User', userSchema)
