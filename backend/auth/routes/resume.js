const router = require('express').Router()
const rateLimit = require('express-rate-limit')
const requireAuth = require('../middleware/requireAuth')
const controller = require('../controllers/resumeController')

// Limit analysis endpoint — it may call OpenAI
const analyzeLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 20,
  message: { error: 'Too many analysis requests — please wait before re-analysing' },
  standardHeaders: true,
  legacyHeaders: false,
})

// All resume routes require authentication
router.use(requireAuth)

router.get('/', controller.list)
router.post('/', controller.createValidation, controller.create)
router.get('/:id', controller.getOne)
router.put('/:id', controller.updateValidation, controller.update)
router.delete('/:id', controller.remove)
router.post('/:id/primary', controller.setPrimary)
router.post('/:id/analyze', analyzeLimiter, controller.analyze)

module.exports = router
