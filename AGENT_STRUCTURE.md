# Mumble AI - Agent Structure & Architecture

**Complete Multi-Agent System for Language Learning**

---

## System Overview

Mumble AI uses a **15-agent orchestration system** built on the AGNO framework. Agents communicate via an event-driven architecture using Redis Pub/Sub, ensuring loose coupling and scalability.

```
┌─────────────────────────────────────────────────────────────┐
│              Main Orchestrator Agent (Team Lead)            │
│         FastAPI + AGNO Framework + Gemini 2.0 Flash         │
│  • Session lifecycle management                             │
│  • Agent coordination via event bus                         │
│  • User state tracking                                      │
│  • Delegation to specialized agents                         │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Event Bus       │
                    │  (Redis Pub/Sub)  │
                    │  • Async events   │
                    │  • Agent routing  │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼───────┐   ┌────────▼────────┐
│  Core Agents   │   │ Skill Agents   │   │ Support Agents  │
│  (3 agents)    │   │  (5 agents)    │   │   (7 agents)    │
└────────────────┘   └────────────────┘   └─────────────────┘
```

---

## Agent Catalog (15 Agents Total)

### 🎯 Core Agents (3)
| # | Agent | Status | Model | Purpose |
|---|-------|--------|-------|---------|
| 1 | User Profile Agent | 📋 Planned | Gemini 1.5 Flash | Initial assessment, goals, learning style |
| 2 | **Planning Agent** | ✅ Built | Gemini 2.0 Flash | Curriculum design, session planning |
| 3 | Session Manager Agent | 📋 Planned | Gemini 2.0 Flash | Session lifecycle, progress handoff |

### 🗣️ Skill Development Agents (5)
| # | Agent | Status | Model | Purpose |
|---|-------|--------|-------|---------|
| 4 | **Speaking Coach** | ✅ Built (as Conversation Agent) | OpenAI gpt-4o-audio | Voice conversation practice |
| 5 | Pronunciation Coach | 📋 Planned | Gemini 1.5 Flash + Speechace | Phoneme-level feedback |
| 6 | Listening Comprehension | 📋 Planned | Gemini 1.5 Flash | Audio content & comprehension |
| 7 | Reading Agent | 📋 Planned | Gemini 1.5 Flash | Text materials & vocabulary |
| 8 | Writing Coach | 📋 Planned | Gemini 2.0 Flash | Composition & feedback |

### 📚 Foundation Agents (2)
| # | Agent | Status | Model | Purpose |
|---|-------|--------|-------|---------|
| 9 | Vocabulary Manager | 📋 Planned | Gemini 1.5 Flash-8B | Spaced repetition system (SRS) |
| 10 | Grammar Tutor | 📋 Planned | Gemini 1.5 Flash | Rule teaching & error correction |

### 📊 Assessment & Feedback Agents (2)
| # | Agent | Status | Model | Purpose |
|---|-------|--------|-------|---------|
| 11 | Assessment Agent | 📋 Planned | Gemini 2.0 Flash | CEFR evaluation, progress tracking |
| 12 | Feedback & Correction | 📋 Planned | Gemini 2.0 Flash | Error handling, encouragement |

### 🛠️ Support Agents (3)
| # | Agent | Status | Model | Purpose |
|---|-------|--------|-------|---------|
| 13 | Content Agent | 📋 Planned | Gemini 2.0 Flash | AI content generation & curation |
| 14 | QA Agent | 📋 Planned | Gemini 1.5 Flash | Content validation, monitoring |
| 15 | Analytics Agent | 📋 Planned | Gemini 1.5 Flash-8B | Performance dashboards, insights |

**Legend:**
- ✅ Built = Implemented and operational
- 📋 Planned = Documented, ready for implementation
- ⚡ = Real-time agent (WebSocket)

---

## Detailed Agent Architecture

### 1. User Profile Agent 📋

**Purpose**: Comprehensive user profiling and preference learning

```
User Profile Agent
├── Initial Assessment Module
│   ├── CEFR level placement test (A1-C2)
│   ├── Skill-specific assessment
│   └── Learning history import
│
├── Goal Setting Module
│   ├── Target fluency level & timeline
│   ├── Primary use case (travel, business, academic)
│   └── Daily time commitment
│
├── Learning Style Profiler
│   ├── Visual vs auditory vs kinesthetic
│   ├── Pace preference (intensive vs relaxed)
│   └── Challenge tolerance
│
└── Interest Profiler
    ├── Topic preferences (sports, tech, culture, news)
    ├── Content format preferences
    └── Real-world scenarios needed
```

**Inputs**: User registration data, initial questionnaire
**Outputs**: Comprehensive user profile → Planning Agent
**Integration**: Provides profile to Planning Agent, updates from Analytics Agent

---

### 2. Planning Agent ✅ (EXISTING - Enhanced)

**Purpose**: Session curriculum design with session-to-session adaptation

```
Planning Agent (Gemini 2.0 Flash)
├── Session Planning Sub-agent
│   ├── Curriculum Generator
│   ├── Activity Sequencer (warm-up, core, cool-down)
│   ├── Skill Distribution Calculator (40% speaking, 30% input, etc.)
│   └── Time Allocator (15/30/45/60 min sessions)
│
├── Progress Integration Sub-agent ⭐ NEW
│   ├── Previous Session Analyzer
│   │   ├── Parse completion status
│   │   ├── Extract performance metrics
│   │   └── Process user feedback
│   ├── Weakness Identifier
│   │   ├── Recurring error pattern detector
│   │   ├── Skill gap analyzer
│   │   └── Plateau detector
│   └── Adaptive Curriculum Adjuster
│       ├── Difficulty re-calibrator
│       ├── Focus area shifter
│       └── Content type rotator
│
└── Plan Verification & Modification Sub-agent ⭐ NEW
    ├── Plan presenter (user-friendly format)
    ├── Modification handler (pre-session AND mid-session)
    ├── Plan validator (pedagogical soundness)
    └── Real-time adjustment engine
```

**Key Feature**: **Session Handoff** - Uses previous session data to plan next session

**Inputs**: User profile, previous session report, user preferences
**Outputs**: Session plan with activities, duration, focus areas
**Events Published**: `session.plan_created`, `session.plan_modified`
**Events Subscribed**: `session.create_requested`, `session.completed`

---

### 3. Session Manager Agent 📋

**Purpose**: Manages session lifecycle and inter-session state transitions

```
Session Manager Agent (Gemini 2.0 Flash)
├── Session Lifecycle Controller
│   ├── Session initialization (load plan, prepare content)
│   ├── Activity transitions (warm-up → core → cool-down)
│   ├── Session pause/resume state management
│   └── Session termination and cleanup
│
├── Progress Aggregator
│   ├── Collect performance data from all agents
│   ├── Aggregate scores, errors, time spent
│   ├── Generate session summary report
│   └── Trigger Assessment Agent evaluation
│
└── Plan Modification Handler
    ├── Accept user requests mid-session
    ├── Coordinate with Planning Agent
    └── Seamless transition to modified plan
```

**API Endpoints**:
- `POST /sessions/create` - Create new session
- `POST /sessions/{id}/start` - Start session
- `POST /sessions/{id}/next_activity` - Load next activity
- `POST /sessions/{id}/modify_plan` - Modify plan (mid-session supported)
- `POST /sessions/{id}/complete` - Complete and assess

**Inputs**: User requests, activity completion data
**Outputs**: Activity routing, session reports
**Events Published**: `session.started`, `session.activity_completed`, `session.completed`

---

### 4. Speaking Coach Agent ✅ (EXISTING - Split from Conversation Agent)

**Purpose**: Natural conversation practice with cultural context

```
Speaking Coach Agent (OpenAI gpt-4o-audio-preview) ⚡ Real-time
├── Dialogue Manager Sub-agent
│   ├── Context tracking (conversation memory)
│   ├── Turn-taking controller
│   └── Topic transition handler
│
├── Personality Module
│   ├── Friendly Tutor Mode
│   ├── Casual Friend Mode
│   ├── Professional Colleague Mode
│   └── Strict Teacher Mode
│
├── Scenario Generator
│   ├── Free Conversation (open-ended)
│   ├── Role-play Scenarios
│   │   ├── Ordering at restaurant
│   │   ├── Job interview
│   │   ├── Doctor's appointment
│   │   ├── Shopping/negotiating
│   │   ├── Travel situations
│   │   └── Social events
│   ├── Debate/Discussion
│   └── Storytelling (collaborative)
│
├── Cultural Context Module
│   ├── Idiom Explainer (real-time)
│   ├── Formality Level Detector (tu vs vous)
│   ├── Cultural Taboo Warner
│   ├── Gesture/Body Language Guide
│   └── Humor/Sarcasm Interpreter
│
├── Vocabulary Injector
│   ├── Target word usage promoter
│   ├── Synonym suggester
│   └── Natural phrase introducer
│
└── Fluency Metrics Sub-agent
    ├── Speaking speed analyzer (WPM)
    ├── Pause pattern detector
    ├── Filler word counter ("um", "uh")
    ├── Sentence complexity tracker
    └── Confidence score calculator
```

**WebSocket Endpoint**: `WS /agents/speaking_coach/{session_id}`

**Message Flow**:
```
Client → Server: audio_chunk (base64)
Server → Client: transcription + pronunciation_feedback
Server → Client: agent_response_audio (base64)
Server → Client: activity_complete (performance scores)
```

**Inputs**: User voice (audio stream)
**Outputs**: Voice responses, fluency scores, conversation quality rating
**Parallel Processing**: Pronunciation Coach runs simultaneously

---

### 5. Pronunciation Coach Agent 📋

**Purpose**: Phoneme-level pronunciation analysis and feedback

```
Pronunciation Coach Agent (Gemini 1.5 Flash + Speechace API) ⚡ Real-time
├── Phoneme Analyzer Sub-agent
│   ├── Individual sound accuracy checker
│   ├── IPA transcription generator
│   └── Common error identifier (e.g., "th" for Spanish speakers)
│
├── Intonation Tracker Sub-agent
│   ├── Pitch pattern analyzer
│   ├── Sentence stress detector
│   └── Question vs statement intonation checker
│
├── Accent Reduction Coach Sub-agent
│   ├── Native speaker comparison
│   ├── Targeted drill generator
│   └── Progress tracker (accent reduction over time)
│
├── Pronunciation Scoring System
│   ├── Real-time feedback (<200ms latency) ⚡
│   └── Improvement suggestions
│
└── Visual Feedback Generator
    ├── Waveform display
    ├── Pitch curve visualization
    └── Mouth position diagrams
```

**WebSocket Endpoint**: `WS /agents/pronunciation_coach/{session_id}`

**External Integration**: Speechace API for phoneme-level scoring

**Inputs**: User voice (audio)
**Outputs**: Phoneme accuracy scores, visual feedback, targeted drills
**Runs in Parallel**: With Speaking Coach during conversation

---

### 6. Listening Comprehension Agent 📋

**Purpose**: Develop listening skills through varied audio content

```
Listening Comprehension Agent (Gemini 1.5 Flash)
├── Content Selection Sub-agent
│   ├── Difficulty Matcher (CEFR level, speed, vocabulary)
│   ├── Interest Aligner (topics, format, length)
│   └── Content Source Manager
│       ├── AI-Generated (70%): Dialogues, stories, news
│       └── Curated External (30%): Podcasts, YouTube, news clips
│
├── Audio Processing Sub-agent
│   ├── Speed Controller (0.75x, 1.0x, 1.25x, 1.5x)
│   ├── Accent Variety Manager (standard, regional, non-native)
│   └── Background Noise Simulator (café, street, phone - advanced)
│
└── Comprehension Tester Sub-agent
    ├── Question Generator (multiple choice, true/false, short answer)
    ├── Interactive Transcript (click word for definition)
    └── Progress Tracker (accuracy, speed tolerance, vocab acquisition)
```

**Content Sources**:
- AI-Generated: Claude API for custom dialogues
- TTS: ElevenLabs for natural voices
- External: YouTube API, Podcast RSS feeds, News APIs

**Inputs**: User proficiency level, interests
**Outputs**: Audio content, comprehension questions, scores

---

### 7. Reading Agent 📋

**Purpose**: Build reading comprehension and vocabulary through diverse texts

```
Reading Agent (Gemini 1.5 Flash)
├── Text Selection Sub-agent
│   ├── Difficulty Calculator (Flesch-Kincaid, CEFR, vocabulary complexity)
│   ├── Content Type Selector (stories, news, blogs, academic, dialogues)
│   └── Topic Matcher (user interests, cultural relevance)
│
├── Vocabulary Extraction Sub-agent
│   ├── New Word Identifier (compare to user's known vocabulary)
│   ├── Frequency-based Prioritization
│   ├── In-text Annotation System
│   │   ├── Inline definitions (hover/click)
│   │   ├── Example sentences
│   │   ├── Visual aids (images)
│   │   └── Audio pronunciation
│   └── Vocabulary List Generator → sends to Vocabulary Manager
│
├── Comprehension Testing Sub-agent
│   ├── Question Generator (factual, inference, opinion, summary)
│   ├── Interactive Reading Features (sentence-by-sentence, highlighting)
│   └── Comprehension Scorer
│
└── Reading Analytics Sub-agent
    ├── Reading Speed Tracker (WPM)
    ├── Re-read Pattern Detector
    ├── Vocabulary Look-up Counter
    └── Preferred Content Type Identifier
```

**Content Sources**:
- AI-Generated: Claude API for custom stories/articles
- External: News APIs, Wikipedia API

**Inputs**: User level, interests
**Outputs**: Text materials, comprehension questions, new vocabulary list

---

### 8. Writing Coach Agent 📋

**Purpose**: Develop writing skills with detailed, constructive feedback

```
Writing Coach Agent (Gemini 2.0 Flash)
├── Grammar Checker Sub-agent
│   ├── Real-time Error Detection (syntax, conjugation, articles, prepositions)
│   ├── Error Explanation Generator (rule, correct version, examples)
│   └── Grammar Pattern Tracker → notifies Grammar Tutor Agent
│
├── Style Improvement Sub-agent
│   ├── Vocabulary Enhancer (synonym suggestions, precise words)
│   ├── Sentence Structure Improver (variety, complexity balance)
│   └── Tone Adjuster (formality, cultural appropriateness)
│
├── Structure Analyzer Sub-agent
│   ├── Format-specific Guidance (essay, email, story, report)
│   ├── Coherence Checker (logical flow, paragraph unity)
│   └── Length Manager (word count, conciseness/expansion suggestions)
│
└── Writing Exercise Generator Sub-agent
    ├── Prompt Generator (descriptive, narrative, argumentative, practical)
    ├── Guided Writing Mode (sentence starters, templates)
    └── Free Writing Mode (minimal guidance, comprehensive feedback)
```

**External Integration**: LanguageTool API (self-hosted) for grammar checking

**Inputs**: User writing submissions
**Outputs**: Detailed feedback, corrections, style suggestions, writing prompts

---

### 9. Vocabulary Manager Agent 📋

**Purpose**: Systematic vocabulary acquisition via spaced repetition

```
Vocabulary Manager Agent (Gemini 1.5 Flash-8B)
├── Spaced Repetition Sub-agent (SM-2 Algorithm)
│   ├── Review Scheduler
│   │   ├── Daily queue generator
│   │   ├── Overdue word prioritizer
│   │   └── New word introducer (pace controller)
│   ├── Lapse Handler
│   │   ├── Difficulty reset for forgotten words
│   │   ├── Re-teaching module trigger
│   │   └── Alternative mnemonic suggester
│   └── SM-2 Algorithm Implementation
│       ├── Initial interval: 1 day
│       ├── Second interval: 6 days
│       ├── Subsequent: previous * ease factor
│       └── Ease factor adjustment based on recall
│
├── Contextual Learning Sub-agent
│   ├── Word in Sentence Generator (multiple examples, different contexts)
│   ├── Story Embedder (short stories featuring target words)
│   └── Collocation Teacher (common word pairings, idioms)
│
├── Vocabulary Acquisition Sub-agent
│   ├── Word Frequency Analyzer (high-frequency priority)
│   ├── Mnemonic Generator
│   │   ├── Visual associations (AI-generated images)
│   │   ├── Sound-alike memory tricks
│   │   └── Etymology explanations
│   └── Word Family Teacher (root words, derivatives, clusters)
│
└── Vocabulary Assessment Sub-agent
    ├── Active vs Passive Tracker (recognition vs production)
    ├── Retention Rate Monitor (30/60/90 day tracking)
    └── Flashcard System (traditional, image, audio, sentence completion)
```

**Database**: `vocabulary` collection with SRS scheduling

**Inputs**: New words from Reading Agent, user reviews
**Outputs**: Daily review queue, flashcards, retention rates

---

### 10. Grammar Tutor Agent 📋

**Purpose**: Systematic grammar instruction and error pattern correction

```
Grammar Tutor Agent (Gemini 1.5 Flash)
├── Rule Explainer Sub-agent
│   ├── Grammar Point Selector (A1→C2 progression)
│   ├── Explanation Generator (simple language, visuals, comparisons)
│   └── Example Provider (positive/negative, user-relevant)
│
├── Exercise Generator Sub-agent
│   ├── Drill Type Selector
│   │   ├── Fill-in-the-blank
│   │   ├── Multiple choice
│   │   ├── Sentence transformation
│   │   ├── Error correction
│   │   └── Free production
│   ├── Difficulty Calibrator (isolated, mixed, contextual)
│   └── Adaptive Exercise Flow (success → harder, struggle → hints)
│
├── Error Pattern Detector Sub-agent ⭐ CRITICAL
│   ├── Cross-agent Error Aggregator
│   │   ├── Collect from Speaking Coach
│   │   ├── Collect from Writing Coach
│   │   └── Collect from exercises
│   ├── Pattern Analyzer
│   │   ├── Recurring error identifier (3 occurrences → trigger)
│   │   ├── Error frequency tracker
│   │   ├── Root cause analyzer
│   │   └── Fossilization detector (persistent errors)
│   └── Intervention Trigger
│       ├── Mini-lesson generator
│       ├── Targeted drill creator
│       └── Planning Agent notifier (adjust curriculum)
│
└── Progressive Complexity Manager
    ├── Grammar Curriculum Designer
    │   ├── Beginner (A1-A2): Present tense, basic questions, articles
    │   ├── Intermediate (B1-B2): Past tenses, conditionals, complex sentences
    │   └── Advanced (C1-C2): Subjunctive, passive voice, nuanced meanings
    ├── Mastery Tracker
    └── Integration Promoter (apply in speaking, writing, reading)
```

**Key Feature**: **3-Occurrence Rule** - Triggers intervention after 3 recurring errors

**Inputs**: Errors from Speaking, Writing, user exercises
**Outputs**: Grammar lessons, exercises, intervention triggers
**Events Published**: `grammar.intervention_created`, `grammar.point_mastered`

---

### 11. Assessment Agent 📋

**Purpose**: Continuous skill evaluation and CEFR level calculation

```
Assessment Agent (Gemini 2.0 Flash)
├── Continuous Evaluation Sub-agent
│   ├── Real-time Skill Monitoring (per activity)
│   ├── Micro-assessment Integration (every exercise scored)
│   └── Milestone Assessments (weekly, monthly, level-up)
│
├── Skill Level Calculator Sub-agent
│   ├── CEFR Level Evaluator (A1-C2 per skill + overall)
│   ├── Sub-skill Granularity
│   │   ├── Pronunciation accuracy
│   │   ├── Vocabulary breadth
│   │   ├── Grammar mastery
│   │   ├── Fluency score
│   │   └── Comprehension speed
│   └── Comparative Benchmarking
│       ├── Time-based progress (vs 1 month ago)
│       ├── Expected progress curve
│       └── Time-to-fluency estimator
│
├── Weakness Identifier Sub-agent
│   ├── Skill Gap Analyzer (speaking vs listening imbalance)
│   ├── Content Gap Analyzer (grammar gaps, vocabulary gaps)
│   └── Learning Style Mismatch Detector
│
└── Progress Tracker Sub-agent ⭐ CRITICAL for Session Handoff
    ├── Session Summary Generator
    │   ├── Skills practiced with duration
    │   ├── Accuracy scores
    │   ├── New vocabulary learned
    │   ├── Grammar points covered
    │   └── User subjective rating
    ├── Historical Progress Visualizer
    │   ├── Skill radar charts
    │   ├── Session completion streak
    │   ├── Total hours logged
    │   └── Level progression timeline
    └── Next Session Data Package
        ├── Performance metrics
        ├── Identified weaknesses
        ├── Mastered content
        └── Recommended focus areas
```

**Key Role**: Generates session reports that Planning Agent uses for next session

**Inputs**: Performance data from all skill agents
**Outputs**: Session reports, CEFR levels, weakness identification
**Events Published**: `session.completed`, `progress.level_up`, `progress.weakness_identified`

---

### 12. Feedback & Correction Agent 📋 ⚡ Real-time

**Purpose**: Intelligent error handling with auto-adjusting correction intensity

```
Feedback & Correction Agent (Gemini 2.0 Flash)
├── Error Categorizer Sub-agent
│   ├── Error Type Classifier (pronunciation, grammar, vocabulary, pragmatic, fluency)
│   ├── Severity Assessor (critical/meaning-changing, moderate, minor)
│   └── Frequency Tracker (one-off, occasional, recurring)
│
├── Correction Delivery Sub-agent
│   ├── Timing Controller
│   │   ├── Immediate (pronunciation in speaking practice)
│   │   ├── End-of-turn (preserve conversation flow)
│   │   ├── End-of-activity (comprehensive review)
│   │   └── Delayed (spaced review of past errors)
│   ├── Correction Style Selector
│   │   ├── Direct ("This is wrong. Say it this way.")
│   │   ├── Recast (repeat correctly without explicit correction)
│   │   ├── Elicitation ("Can you think of another way?")
│   │   ├── Metalinguistic ("Remember the rule about...")
│   │   └── Clarification request ("Did you mean...?")
│   └── Intensity Modulator with Auto-Adjustment ⭐ KEY FEATURE
│       ├── Default intensity by level (Beginner: gentle, Intermediate: balanced, Advanced: direct)
│       ├── Real-time Adjustment Based on User Reactions
│       │   ├── Frustration Markers: Long pauses, repeated errors, verbal cues ("I don't get it")
│       │   ├── Confidence Indicators: Fast responses, self-corrections, engagement
│       │   ├── Auto-adjust: Reduce corrections if frustrated, increase if user wants more
│       │   └── Learn per-user optimal style over sessions
│       └── Store per-user correction preferences in profile
│
├── Corrective Exercise Generator Sub-agent
│   ├── Targeted Drill Creator (specific error focus)
│   ├── Error Pattern Breaker (contrast drills, minimal pairs)
│   └── Reinforcement Scheduler (immediate, next session, long-term SRS)
│
├── Positive Reinforcement Manager
│   ├── Success Detector (correct difficult usage, improvement, natural fluency)
│   ├── Encouragement Generator (specific praise, progress highlighting)
│   └── Confidence Builder (emphasize strengths, frame errors as opportunities)
│
└── Mistake Pattern Logger
    ├── Error Database (timestamp, context, type, severity, correction)
    ├── Long-term Pattern Analyzer
    │   ├── Persistent errors (fossilization risk)
    │   ├── Improving errors (mastery in progress)
    │   ├── Resolved errors (mastered)
    │   └── Error clusters (related mistakes)
    └── Reporting to Other Agents (Grammar Tutor, Planning, Assessment)
```

**Key Feature**: **Auto-Adjusting Correction Intensity** based on frustration/confidence detection

**Inputs**: Errors from Speaking, Writing, exercises; user reactions
**Outputs**: Corrections, encouragement, error patterns
**Events Published**: `error.pattern_detected`, `error.corrected`

---

### 13. Content Agent 📋 (Async)

**Purpose**: Generate and curate engaging, level-appropriate learning materials

```
Content Agent (Gemini 2.0 Flash) - Runs in Background
├── AI Content Generator Sub-agent
│   ├── Story Generator (fiction, user interests, progressive difficulty)
│   ├── Article Generator (news-style, topic-based)
│   ├── Dialogue Generator (scenarios)
│   └── Exercise Generator (grammar drills, vocab quizzes, comprehension)
│
├── External Content Curator Sub-agent
│   ├── YouTube/Podcast Scraper (with difficulty rating)
│   ├── News Article Aggregator (BBC, Reuters with level classification)
│   └── Social Media Content (Reddit, Twitter trends for cultural immersion)
│
└── Content Adaptation Sub-agent
    ├── Difficulty Adjuster (simplify/complexify text)
    ├── Annotation Generator (inline explanations)
    └── Interactive Exercise Creator (questions, fill-blanks, prompts)
```

**Content Strategy**:
- **70% AI-Generated**: Precisely matched to user level and interests
- **30% Curated External**: Authentic native materials for immersion

**Pre-Generation**: Runs background jobs to build content library for common learning paths

**Inputs**: User level, interests, curriculum needs
**Outputs**: Stories, articles, dialogues, exercises (tagged with CEFR level)
**Events Subscribed**: `content.needed`

---

### 14. Quality Assurance Agent 📋

**Purpose**: Ensure system reliability and content quality

```
QA Agent (Gemini 1.5 Flash)
├── Content Accuracy Validator
│   ├── Grammar Correctness Checker
│   ├── Cultural Appropriateness Validator
│   └── CEFR Level Accuracy Verifier
│
├── Pronunciation Model Validator
│   ├── Compare Speechace scores with human ratings
│   ├── Detect false positives/negatives
│   └── Model drift detection
│
├── Exercise Difficulty Calibrator
│   ├── Track user success rates per exercise type
│   ├── Flag exercises that are too hard/easy
│   └── Recommend difficulty adjustments
│
└── Bug Pattern Detector
    ├── Agent failure pattern detection
    ├── User complaint aggregation
    └── Performance degradation alerts
```

**Monitoring**: Integrates with Sentry (errors) and DataDog (performance)

**Inputs**: Content samples, model outputs, user feedback
**Outputs**: Validation reports, quality scores, alerts

---

### 15. Analytics Agent 📋

**Purpose**: Provide actionable insights to users and system

```
Analytics Agent (Gemini 1.5 Flash-8B)
├── Performance Dashboard Generator
│   ├── Skill Radar Charts (visual progress)
│   ├── Session Completion Trends
│   ├── Accuracy Over Time Graphs
│   └── Vocabulary Acquisition Curve
│
├── Weakness Predictor
│   ├── Identify future problem areas based on patterns
│   └── Recommend preemptive practice
│
├── Learning Velocity Calculator
│   ├── Estimate time to next CEFR level
│   ├── Compare to typical learner progress
│   └── Identify acceleration/deceleration periods
│
└── Comparative Analyst
    ├── Compare to anonymized cohort data
    ├── Identify effective learning strategies
    └── Recommend adjustments
```

**Visualization**: D3.js, Recharts for dashboards

**Inputs**: Session reports, progress data, error patterns
**Outputs**: Dashboards, predictions, recommendations

---

## Event-Driven Communication

### Event Bus Architecture

```
Redis Pub/Sub (Event Bus)
│
├── Session Events
│   ├── session.created
│   ├── session.started
│   ├── session.activity_completed
│   ├── session.completed
│   └── session.plan_modified
│
├── Progress Events
│   ├── progress.skill_improved
│   ├── progress.level_up
│   ├── progress.weakness_identified
│   └── progress.milestone_reached
│
├── Error Events
│   ├── error.pattern_detected (3 occurrences)
│   ├── error.fossilization_risk
│   └── error.corrected
│
└── Content Events
    ├── content.generated
    ├── content.needed
    ├── vocabulary.word_learned
    └── grammar.point_mastered
```

### Agent Subscription Matrix

| Event | Publishers | Subscribers |
|-------|-----------|-------------|
| `session.completed` | Session Manager | Assessment, Analytics, Planning |
| `session.plan_created` | Planning Agent | Session Manager, UI |
| `error.pattern_detected` | Feedback Agent | Grammar Tutor, Planning, Assessment |
| `progress.level_up` | Assessment | Analytics, Planning, UI |
| `vocabulary.word_learned` | Vocabulary Manager | Assessment, Analytics |
| `content.needed` | Multiple | Content Agent |
| `grammar.point_mastered` | Grammar Tutor | Assessment, Planning |

---

## Technology Stack

### Agent Models

| Agent Category | Model | Cost Tier | Reasoning |
|---------------|-------|-----------|-----------|
| **High Intelligence** | Gemini 2.0 Flash | High | Complex reasoning (Orchestrator, Planning, Assessment, Feedback, Content) |
| **Balanced** | Gemini 1.5 Flash | Medium | Standard skill agents (Pronunciation, Listening, Reading, Grammar) |
| **Lightweight** | Gemini 1.5 Flash-8B | Low | Focused tasks (Vocabulary, Analytics) |
| **Voice Specialist** | OpenAI gpt-4o-audio-preview | High | Native audio modalities (Speaking Coach) |

### External Services

| Service | Purpose | Cost |
|---------|---------|------|
| **Speechace API** | Phoneme-level pronunciation analysis | $99/month |
| **ElevenLabs** | Natural TTS for agent voices | $99/month |
| **Whisper API** | Speech-to-text transcription | Usage-based |
| **LanguageTool** | Grammar checking (self-hosted) | Free |
| **YouTube API** | Educational video curation | Free tier |
| **News APIs** | Article curation | Free tier |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI + AGNO | Agent orchestration framework |
| **Database** | MongoDB (Atlas) | User data, sessions, progress, curricula |
| **Cache/Events** | Redis Cloud | Event bus + session state |
| **Storage** | AWS S3 | Audio recordings, generated content |
| **Real-time** | WebSocket (Socket.io) | Voice streaming, live feedback |
| **Monitoring** | Sentry + DataDog | Error tracking + performance |
| **Analytics** | Mixpanel | User behavior tracking |

---

## Session Flow with Agent Interactions

### Complete Session Lifecycle

```
1. SESSION PLANNING
   User clicks "Create New Session"
   ↓
   Session Manager → Planning Agent
   ↓
   Planning Agent:
   - Retrieves previous session report (from Assessment Agent)
   - Analyzes user's weaknesses
   - Generates new session plan
   ↓
   User approves plan (can modify pre-session or mid-session)

2. SESSION EXECUTION
   Session Manager loads activities sequentially:

   Activity 1: Vocabulary Review (5 min)
   → Vocabulary Manager Agent
   → Flashcard review with SRS

   Activity 2: Speaking Practice (12 min)
   → Speaking Coach Agent (conversation)
   → Pronunciation Coach Agent (parallel feedback)
   → Feedback Agent (real-time corrections)

   Activity 3: Grammar Exercises (8 min)
   → Grammar Tutor Agent
   → Targeted drills on weak areas
   → Feedback Agent (logs error patterns)

   Activity 4: Cool-down (5 min)
   → Session summary preview
   → Next session topic preview

3. SESSION COMPLETION
   Session Manager triggers assessment
   ↓
   Assessment Agent:
   - Aggregates data from all agents
   - Calculates per-skill performance
   - Identifies weaknesses (e.g., past tense errors)
   - Generates comprehensive session report
   ↓
   Analytics Agent updates dashboards
   ↓
   User sees "Create New Session" button

4. NEXT SESSION PLANNING (Handoff)
   User clicks "Create New Session"
   ↓
   Planning Agent receives:
   - Previous session performance (78% speaking, 67% grammar)
   - Identified weaknesses (past tense: high priority)
   - User feedback ("struggled but enjoyed")
   ↓
   Planning Agent generates new plan:
   - Focuses on past tense grammar (high priority)
   - Maintains speaking practice (user's strength)
   - Introduces future tense (gentle progression)
   ↓
   [Cycle repeats]
```

---

## Critical Agent Interactions

### Error Pattern Detection & Intervention Flow

```
1. User makes error in speaking
   → Speaking Coach logs error
   → Feedback Agent categorizes: "past_tense_verb"

2. Same error in writing
   → Writing Coach logs error
   → Feedback Agent: "past_tense_verb" (2nd occurrence)

3. Same error in speaking again
   → Feedback Agent: "past_tense_verb" (3rd occurrence)
   → Publishes: error.pattern_detected

4. Grammar Tutor Agent subscribes
   → Receives error pattern event
   → Creates mini-lesson on past tense
   → Publishes: grammar.intervention_created

5. Planning Agent subscribes
   → Adjusts next session curriculum
   → Adds more past tense practice

6. Session Manager (if mid-session)
   → Can insert mini-lesson immediately
```

### Session Handoff Data Flow

```
Session N Completion:

Assessment Agent generates report:
{
  "overall_performance": {
    "speaking": 78, "grammar": 67, "vocabulary": 85
  },
  "identified_weaknesses": [
    {"type": "grammar", "specific": "past_tense", "priority": "high"}
  ],
  "user_feedback": {
    "difficulty": "appropriate",
    "enjoyment": 4
  }
}

→ Stored in MongoDB session_reports collection
→ Published: session.completed event

Session N+1 Planning:

Planning Agent receives session.create_requested:
→ Retrieves report from MongoDB
→ Analyzes weaknesses
→ Generates plan:
{
  "focus_areas": ["past_tense_grammar"],
  "activities": [
    {"type": "grammar_drill", "duration": 10, "focus": "past_tense"},
    {"type": "speaking_practice", "scenario": "past_tense_storytelling"}
  ]
}
```

---

## Scalability & Performance

### Concurrency Support

- **Target**: 1000+ concurrent sessions
- **Strategy**:
  - Horizontal scaling of FastAPI instances
  - Redis cluster for event bus
  - MongoDB sharding for user data
  - CDN (CloudFront) for audio content

### Latency Targets

| Agent Type | Target Latency | Critical Path |
|-----------|---------------|---------------|
| **Real-time Voice** | <200ms (95th percentile) | Speaking Coach, Pronunciation Coach |
| **Session Planning** | <2 seconds | Planning Agent |
| **Event Delivery** | <50ms (95th percentile) | Redis Pub/Sub |
| **Database Queries** | <100ms (95th percentile) | MongoDB with indexes |

### Cost Optimization

**Monthly Cost Estimate (1000 active users, 5 sessions/week)**:
- LLM APIs: ~$6,000
- External Services: ~$200
- Infrastructure: ~$900
- **Total**: ~$7,100/month ($7.10 per active user)

---

## Implementation Status

### Phase 0: Foundation ✅ COMPLETE
- Main Orchestrator Agent
- Planning Agent (basic)
- Conversation Agent (basic)
- MongoDB connection
- Multi-language prompts

### Phase 1: Session Management 🚧 IN PROGRESS
- Event Bus (Redis)
- Session Manager Agent
- Enhanced Planning Agent (session handoff)
- API endpoints

### Phase 2-6: 📋 PLANNED
See [IMPLEMENTATION_PHASES.md](./IMPLEMENTATION_PHASES.md) for detailed 12-week roadmap

---

## Quick Reference

### Agent Quick Facts

| Metric | Value |
|--------|-------|
| **Total Agents** | 15 |
| **Built (Operational)** | 3 (Orchestrator, Planning, Conversation) |
| **Planned** | 12 |
| **Real-time Agents** | 3 (Speaking Coach, Pronunciation Coach, Feedback) |
| **Background Agents** | 1 (Content Agent) |
| **Languages Supported** | 5 (Spanish, French, German, Japanese, Mandarin) |
| **Events Defined** | 15+ event types |

### Key Features

- ✅ **Session Handoff**: Each session builds on previous performance
- ✅ **Mid-Session Modification**: Users can change plans during session
- ✅ **Auto-Adjusting Feedback**: Detects frustration/confidence automatically
- ✅ **3-Occurrence Rule**: Grammar interventions after 3 recurring errors
- ✅ **CEFR Tracking**: Per-skill level evaluation (A1-C2)
- ✅ **Spaced Repetition**: SM-2 algorithm for vocabulary retention
- ✅ **Voice-First**: Natural conversation with phoneme-level feedback

---

## Related Documentation

- [README.md](./README.md) - Project overview & setup
- [IMPLEMENTATION_PHASES.md](./IMPLEMENTATION_PHASES.md) - 12-week development roadmap
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Complete technical architecture
- [MULTILINGUAL_SUPPORT.md](./MULTILINGUAL_SUPPORT.md) - Language-pair implementation
- [~/.claude/plans/synchronous-hatching-spindle.md] - Detailed agent design plan

---

**Last Updated**: 2026-01-21
**Document Version**: 1.0
**Status**: Active Development - Phase 1 (Session Management)
