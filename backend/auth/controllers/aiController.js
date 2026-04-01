/**
 * AI Analysis Controller
 *
 * Uses OpenAI GPT when OPENAI_API_KEY is set.
 * Falls back to a deterministic rule-based analyser so the feature
 * works end-to-end with no API key during development.
 */

// ── OpenAI client (lazy-loaded so the server starts without the key) ──────────
let openaiClient = null
function getOpenAI() {
  if (openaiClient) return openaiClient
  if (!process.env.OPENAI_API_KEY) return null
  try {
    // openai^4 package
    const { OpenAI } = require('openai')
    openaiClient = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
    return openaiClient
  } catch {
    return null
  }
}

// ── Score helpers ─────────────────────────────────────────────────────────────

const GRADE_LABELS = { A: 'Excellent', B: 'Good', C: 'Average', D: 'Needs Work', F: 'Poor' }

function computeScoreFromSuggestions(suggestions) {
  const urgent = suggestions.filter((s) => s.type === 'urgent').length
  const critical = suggestions.filter((s) => s.type === 'critical').length
  if (urgent === 0 && critical === 0) return 'A'
  if (urgent === 0 && critical <= 2) return 'B'
  if (urgent <= 1 && critical <= 4) return 'C'
  if (urgent <= 3) return 'D'
  return 'F'
}

// ── Rule-based fallback analyser ──────────────────────────────────────────────

const WEAK_VERBS = ['worked', 'helped', 'assisted', 'did', 'made', 'was responsible for', 'handled']
const STRONG_VERBS = ['developed', 'engineered', 'led', 'built', 'optimised', 'delivered', 'reduced']
const FILLER_WORDS = ['team player', 'hard-working', 'motivated', 'passionate', 'detail-oriented']

function ruleBasedAnalysis(content, targetJobTitle) {
  const suggestions = []

  // ── Contact section ───────────────────────────────────────────
  const { contact = {} } = content
  if (!contact.linkedin) {
    suggestions.push({
      section: 'Contact',
      type: 'optional',
      issue: 'No LinkedIn URL provided',
      suggestion: 'Add your LinkedIn profile URL to improve recruiter trust.',
      improved_text: 'linkedin.com/in/your-handle',
    })
  }
  if (!contact.github) {
    suggestions.push({
      section: 'Contact',
      type: 'optional',
      issue: 'No GitHub profile linked',
      suggestion: 'Adding GitHub signals technical credibility for engineering roles.',
      improved_text: 'github.com/your-handle',
    })
  }

  // ── Summary ───────────────────────────────────────────────────
  if (!content.summary || content.summary.trim().length < 30) {
    suggestions.push({
      section: 'Summary',
      type: 'critical',
      issue: 'Missing or too-short professional summary',
      suggestion:
        'Add a 2–3 sentence summary highlighting your key skills and career objective.',
      improved_text:
        targetJobTitle
          ? `Results-driven professional targeting ${targetJobTitle} roles with a track record of delivering impactful solutions.`
          : 'Experienced professional with a proven track record of delivering impactful, high-quality results.',
    })
  } else {
    const lowerSummary = content.summary.toLowerCase()
    const fillerFound = FILLER_WORDS.filter((w) => lowerSummary.includes(w))
    if (fillerFound.length > 0) {
      suggestions.push({
        section: 'Summary',
        type: 'urgent',
        issue: `Cliché phrases detected: "${fillerFound.join('", "')}"`,
        suggestion:
          'Replace generic soft-skill terms with specific achievements and measurable impact.',
        improved_text: content.summary
          .replace(/team player/gi, 'cross-functional collaborator')
          .replace(/hard-working/gi, 'delivery-focused'),
      })
    }
  }

  // ── Experience ────────────────────────────────────────────────
  const { experience = [] } = content
  if (experience.length === 0) {
    suggestions.push({
      section: 'Experience',
      type: 'urgent',
      issue: 'No work experience entries found',
      suggestion: 'Add at least one role to give recruiters context about your background.',
      improved_text: '',
    })
  } else {
    experience.forEach((exp, i) => {
      const label = exp.title || `Experience #${i + 1}`

      // Bullet count
      if (!exp.bullets || exp.bullets.length < 2) {
        suggestions.push({
          section: 'Experience',
          type: 'critical',
          issue: `"${label}" has fewer than 2 bullet points`,
          suggestion: 'Add 3–5 quantified bullet points showcasing your impact.',
          improved_text: '• Increased API response time by 40% through caching optimisation.',
        })
      }

      // Weak verbs
      if (exp.bullets) {
        const weakFound = exp.bullets.flatMap((b) =>
          WEAK_VERBS.filter((v) => b.toLowerCase().startsWith(v))
        )
        if (weakFound.length > 0) {
          suggestions.push({
            section: 'Experience',
            type: 'urgent',
            issue: `Weak opening verbs in "${label}": "${weakFound[0]}"`,
            suggestion: `Replace with stronger action verbs like: ${STRONG_VERBS.slice(0, 3).join(', ')}.`,
            improved_text: exp.bullets[0]
              ? exp.bullets[0].replace(/^worked on/i, 'Engineered').replace(/^helped/i, 'Contributed to')
              : '',
          })
        }

        // No numbers/metrics
        const hasMetrics = exp.bullets.some((b) => /\d+/.test(b))
        if (!hasMetrics && exp.bullets.length > 0) {
          suggestions.push({
            section: 'Experience',
            type: 'critical',
            issue: `No quantified results in "${label}"`,
            suggestion: 'Add metrics (%, $, time saved, users served) to every bullet.',
            improved_text: exp.bullets[0]
              ? `${exp.bullets[0].replace(/\.$/, '')} — resulting in a 30% improvement in performance.`
              : '',
          })
        }
      }
    })
  }

  // ── Skills ────────────────────────────────────────────────────
  const { skills = [] } = content
  if (skills.length < 5) {
    suggestions.push({
      section: 'Skills',
      type: 'critical',
      issue: `Only ${skills.length} skill${skills.length === 1 ? '' : 's'} listed`,
      suggestion: 'List 8–15 skills including both technical and domain-specific ones.',
      improved_text: '',
    })
  }

  // ── Education ─────────────────────────────────────────────────
  const { education = [] } = content
  if (education.length === 0) {
    suggestions.push({
      section: 'Education',
      type: 'optional',
      issue: 'No education entries found',
      suggestion: 'Add your educational background even if experience is your primary qualification.',
      improved_text: '',
    })
  }

  // ── Projects ──────────────────────────────────────────────────
  const { projects = [] } = content
  if (projects.length === 0) {
    suggestions.push({
      section: 'Projects',
      type: 'optional',
      issue: 'No projects listed',
      suggestion: 'Adding personal or open-source projects demonstrates initiative and skills.',
      improved_text: '',
    })
  }

  const score = computeScoreFromSuggestions(suggestions)
  const urgentCount = suggestions.filter((s) => s.type === 'urgent').length
  const criticalCount = suggestions.filter((s) => s.type === 'critical').length

  return {
    score,
    score_label: GRADE_LABELS[score],
    summary:
      urgentCount === 0 && criticalCount === 0
        ? 'Your resume is in great shape! Only minor optional improvements remain.'
        : `Found ${urgentCount} urgent and ${criticalCount} critical issues. Addressing these will significantly improve your interview call rate.`,
    suggestions,
  }
}

// ── OpenAI-powered analyser ───────────────────────────────────────────────────

async function openaiAnalysis(content, targetJobTitle) {
  const openai = getOpenAI()
  if (!openai) return null

  const resumeText = JSON.stringify(content, null, 2)
  const jobContext = targetJobTitle ? ` The candidate is targeting: "${targetJobTitle}".` : ''

  const systemPrompt = `You are an expert ATS resume reviewer.${jobContext} You only respond with valid JSON — no markdown, no explanation outside the JSON object.`

  const userPrompt = `Analyse this resume and return JSON in this exact shape:
{
  "score": "A"|"B"|"C"|"D"|"F",
  "score_label": "Excellent"|"Good"|"Average"|"Needs Work"|"Poor",
  "summary": "<2-sentence overview>",
  "suggestions": [
    {
      "section": "<section name>",
      "type": "urgent"|"critical"|"optional",
      "issue": "<concise problem>",
      "suggestion": "<actionable advice>",
      "improved_text": "<rewritten text or empty string>"
    }
  ]
}

Resume:
${resumeText}`

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.3,
      response_format: { type: 'json_object' },
    })

    const result = JSON.parse(response.choices[0].message.content)
    // Validate shape
    if (!result.score || !result.suggestions) return null
    return result
  } catch (err) {
    console.error('OpenAI analysis failed, falling back to rule-based:', err.message)
    return null
  }
}

// ── Public export ─────────────────────────────────────────────────────────────

exports.analyzeResume = async (content, targetJobTitle = '') => {
  // Prefer OpenAI; fall back to rule-based
  const aiResult = await openaiAnalysis(content, targetJobTitle)
  return aiResult || ruleBasedAnalysis(content, targetJobTitle)
}
