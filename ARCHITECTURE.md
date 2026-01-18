# Mumble AI - Language Tutor Architecture

> **Voice-First AI Language Tutor with Skill-Based Multi-Agent Architecture**

Version: 1.0
Last Updated: 2026-01-18
Status: Design Complete, Implementation Phase 1

---

## Table of Contents

1. [Project Vision](#project-vision)
2. [Core Architecture Principles](#core-architecture-principles)
3. [Agent Structure](#agent-structure)
4. [Communication Patterns](#communication-patterns)
5. [Database Schema](#database-schema)
6. [Technology Stack](#technology-stack)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Cost Analysis](#cost-analysis)
9. [Multi-Language Support](#multi-language-support)

---

## Project Vision

Build a **100% human-like AI language tutor** that provides:

- **Voice-first interaction** (text optional)
- **Specialized coaching** for writing, pronunciation, reading, speaking, vocabulary
- **Real-time feedback** where pedagogically appropriate
- **Complete session transparency** - full history with audio/transcripts
- **Adaptive learning** - tracks weak areas, provides targeted practice
- **Proactive recommendations** with user control

### Key User Experience Flow

**Session Creation:**
```
1. User signs in → Views Sessions Dashboard (all past sessions)
2. User clicks "Create New Session"
3. Language Selection Page → User selects target language (e.g., English)
4. MainAgent starts voice conversation:
   - Asks user's proficiency level (beginner/intermediate/advanced)
   - Asks focus areas (pronunciation, writing, reading, speaking)
   - Proposes personalized plan for today's session
   - User confirms plan verbally
5. Session begins with continuous voice conversation
```

**Continuous Voice Conversation (No Manual Triggers):**
```
MainAgent: "Hi! What's your current level - beginner, intermediate, or advanced?"
User: "I'm a beginner" [speaks naturally, no button press]

MainAgent: "Great! What would you like to focus on?"
User: "Pronunciation and writing"

MainAgent: "Perfect! Here's today's plan:
  1. 15 minutes pronunciation practice on 'th' sounds
  2. 10 minutes writing sentences using past tense
  Does this sound good?"
User: "Yes, let's start"

MainAgent: "Awesome! Handing you to your pronunciation coach."

[Seamless transition to PronunciationCoachAgent]

PronunciationCoachAgent: "Hello! Say this word: 'think'"
User: [speaks "think"] [automatic voice detection, no button press]

[Waveform visualization + phoneme breakdown appears dynamically]

PronunciationCoachAgent: "Good! Your 'th' score is 70%.
  Place your tongue between your teeth..."
[Articulation diagram appears]

User: [practices again] [continuous back-and-forth]

PronunciationCoachAgent: "Excellent! You improved to 85%!
  Handing you back to your main tutor."

[Returns to MainAgent]

MainAgent: "Great work! Ready for writing practice?"
User: "Yes"

[Drawing board/text editor appears automatically]

MainAgent: "Write about what you did yesterday."
[User writes]

User: "Done" [or submits via UI]

WritingCoachAgent: "Nice! Let me review this..."
[Feedback displayed with inline highlights]

[Session continues with natural voice flow]
```

**Key Features:**
- ✅ **100% hands-free voice conversation** (Voice Activity Detection handles turn-taking)
- ✅ **Dynamic UI elements** appear when needed (drawing board, waveform, etc.)
- ✅ **Session history button** (top-right) - view full transcript, audio playback, all activities
- ✅ **Seamless agent transitions** - feels like talking to different specialist tutors
- ✅ **No screen interaction required** during conversation (truly voice-first)

---

## Core Architecture Principles

### 1. **Skill-Based Agent Architecture**

**Why Skill-Based?**
- Each language skill (pronunciation, writing, reading, speaking) has unique pedagogy
- Different tools and feedback mechanisms per skill
- Natural for users ("I want to practice pronunciation" not "I want receptive skills practice")
- Easily extensible to new languages (tools change, agents stay the same)
- Avoids code duplication across languages

**Decision Criteria:**

| Use **Agent** When | Use **Tool** When |
|-------------------|------------------|
| Needs conversation & adaptation | Deterministic processing |
| Multi-turn dialogue required | API wrapper/integration |
| Pedagogical reasoning needed | Data operations (CRUD) |
| Real-time encouragement & feedback | No conversational context |

### 2. **Direct Sub-Agent Interaction**

Users interact **directly** with specialized sub-agents during activities:

```
Session Flow:
1. User ←→ MainAgent (orchestration)
2. MainAgent delegates to Sub-Agent
3. User ←→ Sub-Agent (direct activity interaction)
4. Sub-Agent completes → returns results to MainAgent
5. MainAgent logs progress, decides next activity
```

**Benefits:**
- ✅ Lower latency (no MainAgent routing overhead)
- ✅ Better specialization (agent maintains fine-grained activity state)
- ✅ More natural UX (feels like specialist tutors)
- ✅ Cost efficient (MainAgent doesn't process every exchange)

### 3. **Agent vs Tool vs Service**

| Type | When to Use | Examples |
|------|-------------|----------|
| **Full AGNO Agent** | Conversational, adaptive, multi-turn | MainAgent, PronunciationCoach, WritingCoach |
| **Tool** | Deterministic analysis, API wrappers | PhonemeAnalysisTool, GrammarAnalysisTool |
| **Background Service** | Async batch processing, no real-time | CurriculumArchitect, AssessmentEngine |

---

## Agent Structure

### Architecture Diagram

```
                         User (Voice/Text)
                                |
                                ↓
                         ┌──────────────┐
                         │  MainAgent   │  (Orchestrator)
                         │  🎯 Tutor    │
                         └──────┬───────┘
                                |
                ┌───────────────┼───────────────┐
                ↓               ↓               ↓
        ┌───────────────┐ ┌───────────────┐ ┌──────────────┐
        │Pronunciation  │ │   Writing     │ │   Reading    │
        │  Coach 🗣️     │ │   Coach ✍️    │ │   Coach 📖   │
        └───────┬───────┘ └───────┬───────┘ └──────┬───────┘
                │                 │                 │
        ┌───────▼────────┐ ┌──────▼─────────┐ ┌────▼────────┐
        │ Speechace API  │ │ LanguageTool   │ │  Reading    │
        │ IPA Tool       │ │ Grammar Tool   │ │  Fluency    │
        │ Articulation   │ │ Error Explain  │ │  Comprehend │
        └────────────────┘ └────────────────┘ └─────────────┘

        ┌───────────────┐ ┌───────────────┐
        │   Speaking    │ │  Vocabulary   │
        │   Coach 💬    │ │   Coach 📚    │
        └───────┬───────┘ └───────┬───────┘
                │                 │
        ┌───────▼────────┐ ┌──────▼─────────┐
        │ STT/TTS        │ │ Flashcards     │
        │ Fluency Tool   │ │ SRS Scheduler  │
        │ Conversation   │ │ Mastery Track  │
        └────────────────┘ └────────────────┘

Background Services (Async):
├─ CurriculumArchitect 🗓️  (Generate learning paths)
└─ AssessmentEngine 📊     (Progress reports)
```

---

## Agent Specifications

### 1. MainAgent 🎯

**Type:** Full AGNO Agent
**Role:** Orchestrator with tutor personality

**Responsibilities:**
- Welcome users, establish rapport
- Load personalized curriculum
- Decide next activity based on progress & weak areas
- Delegate to specialized sub-agents
- Collect feedback, log progress
- Provide encouragement & motivation
- Handle session management

**Tools:**
- `SessionManagerTool` - Start/pause/resume/end sessions
- `CurriculumLoaderTool` - Load daily lesson plans
- `ProgressTrackerTool` - Log activity results
- `WeakAreaAnalysisTool` - Identify error patterns
- `SessionHistoryTool` - Retrieve past sessions
- `RecommendationEngineTool` - Suggest targeted practice

**AGNO Implementation:**
```python
from agno import Agent, MongoDb
from agno.models.google import Gemini

main_agent = Agent(
    name="MainAgent",
    model=Gemini(id="gemini-2.0-flash"),
    team=[
        pronunciation_coach,
        writing_coach,
        reading_coach,
        speaking_coach,
        vocabulary_coach
    ],
    tools=[
        SessionManagerTool(),
        CurriculumLoaderTool(),
        ProgressTrackerTool(),
        WeakAreaAnalysisTool()
    ],
    instructions="""
    You are a warm, encouraging language tutor. Your role:
    1. Greet users and understand their learning goals
    2. Follow their personalized curriculum
    3. Delegate activities to specialist coaches
    4. Track progress and identify weak areas
    5. Provide motivation and celebrate achievements
    6. Suggest practice based on weak areas (but let user choose)

    Always be conversational, supportive, and adaptive to user's needs.
    """,
    db=MongoDb(db_url=MONGODB_URL),
    enable_user_memories=True,
    enable_agentic_memory=True,
    add_history_to_context=True
)
```

**Cost:** ~$0.30-0.50 per session

---

### 2. PronunciationCoachAgent 🗣️

**Type:** Full AGNO Agent
**Role:** Real-time phoneme-level pronunciation coaching

**Responsibilities:**
- Present target words/phrases for practice
- Capture and analyze user audio
- Provide phoneme-level accuracy scores
- Show articulation guidance (tongue/mouth position)
- Generate IPA transcriptions
- Track pronunciation improvement

**Tools:**
- `PhonemeAnalysisTool` - Speechace API integration (phoneme scoring)
- `IPATranscriptionTool` - Generate IPA representations
- `ArticulationGuideTool` - Mouth/tongue positioning guides
- `PronunciationExerciseGeneratorTool` - Create targeted drills
- `AudioRecorderTool` - Capture user audio
- `AudioPlaybackTool` - Compare user vs native pronunciation

**Feedback Pattern:** **Real-time** via WebSocket

**UI Components:**
- Waveform visualization
- Phoneme-by-phoneme breakdown
- Articulation diagrams
- Side-by-side IPA comparison
- Progress score display

**AGNO Implementation:**
```python
pronunciation_coach = Agent(
    name="PronunciationCoach",
    model=Gemini(id="gemini-1.5-flash"),  # Medium intelligence
    tools=[
        PhonemeAnalysisTool(),
        IPATranscriptionTool(),
        ArticulationGuideTool()
    ],
    instructions="""
    You are a pronunciation specialist. Your role:
    1. Present clear pronunciation targets (words/phrases)
    2. Analyze user's pronunciation with phoneme-level detail
    3. Provide encouraging feedback even for small improvements
    4. Explain articulation (tongue position, airflow, etc.)
    5. Adapt difficulty based on user's accuracy
    6. Celebrate progress and motivate continued practice

    Be patient, specific, and encouraging. Use IPA when helpful.
    Adapt explanations based on user's native language.
    """,
    db=MongoDb(db_url=MONGODB_URL),
    enable_user_memories=True
)
```

**Example Interaction:**
```
Agent: "Let's practice the 'th' sound in 'think'. Listen: [audio]"
User: [says "tink"]
Agent: [analyzes → /t/ instead of /θ/]
       "Good try! You're making a 't' sound. For 'th', place your
        tongue between your teeth and blow air gently. Try again?"
User: [attempts → 60% accuracy on /θ/]
Agent: "Much better! I can hear the improvement. Let's do it once more."
User: [attempts → 85% accuracy]
Agent: "Excellent! You've got it. Your 'th' sound improved from 40% to 85%!"
→ Returns to MainAgent with results
```

**Cost:** ~$0.10-0.20 per activity

---

### 3. WritingCoachAgent ✍️

**Type:** Full AGNO Agent
**Role:** Grammar, structure, and style feedback

**Responsibilities:**
- Present writing prompts (sentences → paragraphs → essays)
- Provide drawing board / text editor interface
- Analyze grammar, spelling, punctuation
- Evaluate structure and coherence
- Explain errors pedagogically
- Track writing skill progression

**Tools:**
- `GrammarAnalysisTool` - LanguageTool API integration
- `ErrorExplanationTool` - Explain why errors are wrong
- `StructureAnalyzerTool` - Check paragraph/essay organization
- `VocabularyRichnessTool` - Analyze word variety
- `WritingPromptGeneratorTool` - Create level-appropriate prompts

**Feedback Pattern:** **Post-activity** via HTTP (writing needs uninterrupted composition time)

**UI Components:**
- Text editor or drawing board
- Inline error highlighting (red/yellow underlines)
- Side panel with explanations
- Revision suggestions
- Score/improvement metrics

**AGNO Implementation:**
```python
writing_coach = Agent(
    name="WritingCoach",
    model=Gemini(id="gemini-1.5-flash"),
    tools=[
        GrammarAnalysisTool(),
        ErrorExplanationTool(),
        StructureAnalyzerTool(),
        WritingPromptGeneratorTool()
    ],
    instructions="""
    You are a writing coach specializing in {target_language}. Your role:
    1. Present clear, level-appropriate writing prompts
    2. Analyze writing for grammar, structure, and style
    3. Explain errors pedagogically (not just "this is wrong")
    4. Provide specific, actionable improvement suggestions
    5. Celebrate strengths while addressing weaknesses
    6. Reference user's native language for common error patterns

    Be constructive, specific, and encouraging. Focus on learning, not perfection.
    """,
    db=MongoDb(db_url=MONGODB_URL),
    enable_user_memories=True
)
```

**Example Interaction:**
```
Prompt: "Write about what you did yesterday"
User submits: "Yesterday, I go to the park and see my friend."
→ Agent analyzes via LanguageTool
Agent: "Great sentence structure! I noticed you used 'go' and 'see' -
        but since you're talking about yesterday (past), we need past tense:
        'went' and 'saw'.

        Rule: When talking about completed actions in the past, use past tense.

        Try rewriting: 'Yesterday, I ___ to the park and ___ my friend.'"
```

**Cost:** ~$0.05-0.10 per activity

---

### 4. ReadingCoachAgent 📖

**Type:** Full AGNO Agent
**Role:** Reading fluency and comprehension

**Responsibilities:**
- Present reading materials (sentences → paragraphs → stories)
- User reads aloud (audio captured)
- Evaluate fluency, pace, accuracy
- Ask comprehension questions
- Provide vocabulary support
- Track reading progress (WPM, accuracy)

**Tools:**
- `ReadingMaterialGeneratorTool` - Create level-appropriate texts
- `ReadingAccuracyAnalysisTool` - Compare user reading to text
- `FluencyAnalyzerTool` - Assess pace and smoothness
- `ComprehensionQuestionGeneratorTool` - Create questions
- `VocabularyHighlighterTool` - Identify difficult words

**Feedback Pattern:** **Real-time** via WebSocket (immediate correction helps fluency)

**UI Components:**
- Reading material display with highlighting
- Current sentence indicator
- Comprehension quiz interface
- Vocabulary popup definitions
- WPM and accuracy meters

**AGNO Implementation:**
```python
reading_coach = Agent(
    name="ReadingCoach",
    model=Gemini(id="gemini-1.5-flash"),
    tools=[
        ReadingMaterialGeneratorTool(),
        ReadingAccuracyAnalysisTool(),
        ComprehensionQuestionGeneratorTool()
    ],
    instructions="""
    You are a reading coach. Your role:
    1. Present level-appropriate reading materials
    2. Listen to user read aloud, provide gentle corrections
    3. Ask comprehension questions to check understanding
    4. Explain difficult vocabulary in context
    5. Track fluency improvements (speed, smoothness)
    6. Adapt difficulty based on performance

    Be encouraging. Reading is about comprehension, not perfection.
    """,
    db=MongoDb(db_url=MONGODB_URL),
    enable_user_memories=True
)
```

**Cost:** ~$0.08-0.15 per activity

---

### 5. SpeakingCoachAgent 💬

**Type:** Full AGNO Agent
**Role:** Conversational fluency and natural speaking

**Responsibilities:**
- Engage in natural conversation on various topics
- Evaluate fluency and naturalness
- Provide gentle grammar corrections without breaking flow
- Identify filler words, hesitations
- Track speaking confidence metrics
- Generate conversation scenarios

**Tools:**
- `SpeechToTextTool` - Real-time transcription
- `FluencyAnalysisTool` - Assess pauses, filler words, pace
- `ConversationManagerTool` - Maintain dialog context
- `TopicGeneratorTool` - Create conversation scenarios
- `GrammarCheckerTool` - Light grammar checking
- `TextToSpeechTool` - Agent speaks naturally

**Feedback Pattern:** **Real-time** via WebSocket (conversation is inherently real-time)

**UI Components:**
- Live conversation transcript
- Real-time waveform visualization
- Post-conversation feedback panel
- Grammar/fluency issues highlighted in transcript
- Speaking time metrics

**AGNO Implementation:**
```python
speaking_coach = Agent(
    name="SpeakingCoach",
    model=Gemini(id="gemini-2.0-flash"),  # High intelligence for conversation
    tools=[
        SpeechToTextTool(),
        FluencyAnalysisTool(),
        ConversationManagerTool()
    ],
    instructions="""
    You are a conversation coach. Your role:
    1. Engage in natural, interesting conversations
    2. Gently correct errors without interrupting flow
    3. Ask follow-up questions to encourage speaking
    4. Adapt topic difficulty based on user's level
    5. Provide subtle grammar/vocabulary suggestions
    6. Celebrate fluency improvements

    Be conversational, natural, and engaging. The goal is confidence and fluency.
    Make the user WANT to keep talking.
    """,
    db=MongoDb(db_url=MONGODB_URL),
    enable_user_memories=True,
    enable_agentic_memory=True
)
```

**Example Interaction:**
```
Agent: "Let's talk about your hobbies. What do you like to do in your free time?"
User: "I like to play soccer and read book."
Agent: "That's great! Soccer is fun. Do you play in a team or just with friends?
        (By the way, we say 'read books' - plural when talking generally 😊)"
User: "I play with friends on weekends."
Agent: "Wonderful! How long have you been playing soccer?"
→ Conversation continues naturally
```

**Cost:** ~$0.20-0.40 per session (highest cost due to multi-turn conversation)

---

### 6. VocabularyCoach 📚

**Type:** Hybrid (Tool mode for MVP, Agent mode for word introductions later)

**Role:** Vocabulary acquisition with spaced repetition

**Responsibilities:**
- Introduce new words with context
- Create flashcard exercises
- Test recall at optimal intervals (SRS algorithm)
- Track word mastery levels (0-5)
- Provide mnemonics and etymology

**Tools:**
- `VocabularyExerciseGeneratorTool` - Create flashcards, fill-in-blanks
- `SpacedRepetitionSchedulerTool` - Calculate optimal review intervals (SM-2 algorithm)
- `MasteryTrackerTool` - Track word familiarity levels
- `ContextGeneratorTool` - Create example sentences
- `EtymologyTool` - Provide word origins

**Feedback Pattern:** Instant (flashcard review)

**UI Components:**
- Flashcard interface (flip animations)
- Multiple choice / fill-in-blank exercises
- Mastery level progress bars
- Personal dictionary view
- Review schedule calendar

**Implementation Strategy:**
- **MVP (Phase 1):** Tool-based flashcards (no LLM needed, cost = $0)
- **Phase 3:** Upgrade to Agent for personalized word introductions

**Tool Mode (MVP):**
```python
# Simple flashcard tool (no agent)
class VocabularyTool:
    def show_flashcard(self, word_id):
        word = db.vocabulary.find_one({"_id": word_id})
        return {"word": word["word"], "definition": word["definition"]}

    def check_answer(self, word_id, user_answer):
        correct = self.validate_answer(word_id, user_answer)
        self.update_mastery(word_id, correct)
        self.schedule_next_review(word_id)
        return {"correct": correct, "next_review": ...}
```

**Agent Mode (Phase 3):**
```python
vocabulary_coach = Agent(
    name="VocabularyCoach",
    model=Gemini(id="gemini-1.5-flash-8b"),  # Lightweight model
    tools=[VocabularyExerciseTool(), MasteryTrackerTool()],
    instructions="""
    You are a vocabulary specialist. Your role:
    1. Introduce new words with memorable context
    2. Create engaging example sentences
    3. Provide etymology/mnemonics to aid memory
    4. Test recall with varied exercise types
    5. Celebrate mastery milestones

    Make vocabulary learning fun and memorable!
    """
)
```

**Cost:**
- Tool mode: ~$0.00-0.02 per drill (MVP)
- Agent mode: ~$0.05-0.10 per introduction session (Phase 3)

---

### 7. CurriculumArchitect 🗓️

**Type:** Async Background Service (NOT a real-time agent)

**Role:** Generate and adapt personalized learning paths

**Responsibilities:**
- Create initial curriculum based on user level & goals
- Adapt curriculum based on progress & weak areas
- Balance skill types (pronunciation, writing, reading, speaking)
- Implement spaced repetition for review
- Generate weekly/daily lesson plans

**Tools:**
- `CurriculumGeneratorTool` - Create structured 30-day learning paths
- `AdaptivePlanningTool` - Adjust based on performance data
- `LevelAssessmentTool` - Determine proficiency (A1-C2)
- `GoalMappingTool` - Align curriculum with user goals

**Trigger Points:**
- User onboarding (initial curriculum)
- Weekly (adaptive adjustments)
- After assessments (major adjustments)

**Implementation:**
```python
# Background service (not a real-time agent)
class CurriculumArchitect:
    def generate_curriculum(self, user_profile, progress_data):
        """Generate 30-day curriculum via single LLM call"""
        prompt = f"""
        Generate a personalized English learning curriculum:
        - User level: {user_profile.proficiency_level}
        - Learning goals: {user_profile.learning_goals}
        - Weak areas: {progress_data.weak_areas}
        - Available time: 30 minutes/day

        Create 30-day lesson plan with:
        - Day-by-day activities (pronunciation, writing, reading, speaking)
        - Progressive difficulty
        - Spaced repetition of weak areas
        - Balanced skill practice

        Return JSON format: {...}
        """

        llm_response = gemini.generate(prompt)
        curriculum = self.parse_curriculum(llm_response)
        db.curricula.insert_one(curriculum)
        return curriculum

    def adapt_curriculum(self, user_id):
        """Weekly adaptation based on progress"""
        progress = db.progress.find({"user_id": user_id})
        weak_areas = self.analyze_weak_areas(progress)

        # Adjust upcoming lessons to focus on weak areas
        db.curricula.update_one(
            {"user_id": user_id},
            {"$set": {"lesson_plan": adjusted_plan}}
        )
```

**Cost:** ~$0.10-0.20 per curriculum generation (infrequent)

---

### 8. AssessmentEngine 📊

**Type:** Async Background Service

**Role:** Progress reports and analytics

**Responsibilities:**
- Conduct placement tests (initial level assessment)
- Perform periodic skill assessments
- Generate detailed progress reports
- Create data visualizations
- Identify long-term trends and plateaus

**Tools:**
- `PlacementTestGeneratorTool` - Create comprehensive level tests
- `ProgressReportGeneratorTool` - Compile performance data
- `VisualizationTool` - Create charts/graphs
- `TrendAnalyzerTool` - Identify patterns over time

**Trigger Points:**
- User onboarding (placement test)
- Weekly (progress summary)
- Monthly (comprehensive report)
- User-requested

**Implementation:**
```python
class AssessmentEngine:
    def generate_progress_report(self, user_id, period="week"):
        """Generate progress report for user"""
        # Query all sessions for period
        sessions = db.sessions.find({
            "user_id": user_id,
            "start_time": {"$gte": period_start}
        })

        # Calculate metrics
        metrics = {
            "pronunciation_score": self.calc_pronunciation(sessions),
            "writing_score": self.calc_writing(sessions),
            "reading_score": self.calc_reading(sessions),
            "speaking_score": self.calc_speaking(sessions),
            "weak_areas": self.identify_weak_areas(sessions),
            "improvement_trends": self.calc_trends(sessions)
        }

        # Generate narrative summary via LLM
        summary = gemini.generate(f"""
        Summarize this user's progress in an encouraging way:
        {json.dumps(metrics)}

        Highlight improvements, celebrate achievements, suggest focus areas.
        """)

        return ProgressReport(metrics, summary, visualizations)
```

**Cost:** ~$0.05 per report

---

## Communication Patterns

### Agent Delegation Flow

```python
# Standard delegation pattern using AGNO Teams

# 1. User interacts with MainAgent
user_message = "I want to practice pronunciation"

# 2. MainAgent processes request
main_agent_response = main_agent.chat(user_message, session_id="sess_123")
# MainAgent's LLM decides: "User needs pronunciation practice"
# MainAgent's response triggers delegation

# 3. AGNO Teams automatically delegates to PronunciationCoach
# - Saves MainAgent context
# - Loads PronunciationCoach with session context
# - Routes subsequent messages to PronunciationCoach

# 4. User interacts directly with PronunciationCoach
user_audio = capture_audio()
pronunciation_response = pronunciation_coach.process_audio(
    audio=user_audio,
    session_id="sess_123"
)
# Multiple turns between user and PronunciationCoach...

# 5. PronunciationCoach completes activity
results = pronunciation_coach.complete_activity(
    activity_id="act_001",
    results={
        "target_phoneme": "/θ/",
        "attempts": 3,
        "scores": [0.40, 0.65, 0.85],
        "weak_areas": []
    }
)

# 6. AGNO Teams returns control to MainAgent
# - PronunciationCoach results passed to MainAgent
# - MainAgent context restored
# - User now interacts with MainAgent again

# 7. MainAgent logs progress and decides next activity
main_agent.chat(
    "[System: PronunciationCoach completed. Results: {...}]",
    session_id="sess_123"
)
# MainAgent: "Excellent! You improved 45%! Ready for writing practice?"
```

### Session State Management

```python
class SessionStateManager:
    """Manages state transitions between agents"""

    def __init__(self, db: MongoDb, redis: Redis):
        self.db = db
        self.redis = redis

    async def delegate_to_agent(
        self,
        session_id: str,
        from_agent: str,
        to_agent: str,
        context: dict
    ):
        """Delegate session to a sub-agent"""
        # Update MongoDB (persistent state)
        await self.db.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "current_agent": to_agent,
                    "agent_context": context,
                    "last_transition": datetime.utcnow()
                }
            }
        )

        # Cache in Redis (fast access)
        await self.redis.setex(
            f"session:{session_id}:current_agent",
            3600,  # 1 hour TTL
            to_agent
        )

    async def complete_activity(
        self,
        session_id: str,
        activity_id: str,
        results: dict
    ):
        """Mark activity complete, return to MainAgent"""
        await self.db.sessions.update_one(
            {"session_id": session_id, "activities.activity_id": activity_id},
            {
                "$set": {
                    "activities.$.status": "completed",
                    "activities.$.ended_at": datetime.utcnow(),
                    "activities.$.results": results,
                    "current_agent": "main_agent"
                }
            }
        )
```

---

## Database Schema

### MongoDB Collections

#### `users`
```javascript
{
  _id: ObjectId,
  name: String,
  email: String,
  native_language: String,       // "es", "fr", "zh", etc.
  target_language: String,       // "en", "es", "fr", etc.
  ui_language: String,           // Interface language
  proficiency_level: String,     // "A1", "A2", "B1", "B2", "C1", "C2"
  learning_goals: [String],      // ["improve pronunciation", "business English"]
  preferences: {
    voice_first: Boolean,
    daily_practice_minutes: Number,
    preferred_topics: [String]
  },
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes:**
- `email` (unique)
- `target_language`

#### `sessions`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  language: String,              // Target language selected ("en", "es", etc.)
  start_time: DateTime,
  end_time: DateTime,
  current_agent: String,         // "main_agent", "pronunciation_coach", etc.

  // User's confirmed plan for this session (created during onboarding conversation)
  plan: {
    level: String,               // "beginner", "intermediate", "advanced"
    focus_areas: [String],       // ["pronunciation", "writing"]
    activities: [
      {
        skill: String,           // "pronunciation", "writing", etc.
        topic: String,           // "th sounds", "past tense"
        duration_minutes: Number,
        status: String           // "pending", "in_progress", "completed"
      }
    ]
  },

  // Full conversation transcript (everything said - for session history button)
  conversation_history: [
    {
      role: String,              // "agent" or "user"
      agent: String,             // "main_agent", "pronunciation_coach", etc.
      text: String,              // Transcript
      audio_url: String,         // S3 URL for audio playback
      timestamp: DateTime
    }
  ],

  // Activity-specific data (writing submissions, pronunciation scores, etc.)
  activities: [
    {
      activity_id: String,       // "act_001"
      agent: String,             // "pronunciation_coach"
      activity_type: String,     // "phoneme_practice", "writing_exercise", etc.
      user_input: {
        type: String,            // "audio" or "text"
        s3_url: String,          // Audio file location (if audio)
        transcript: String,      // Transcription (if audio)
        text: String             // User's text (if text)
      },
      agent_feedback: {
        scores: Object,          // Activity-specific scores
        errors: [String],
        suggestions: [String],
        encouragement: String
      },
      weak_areas: [String],      // ["/θ/ phoneme", "past tense"]
      timestamp: DateTime,
      duration_seconds: Number,
      status: String             // "in_progress", "completed"
    }
  ],
  session_summary: String,
  overall_performance: {
    pronunciation: Number,
    writing: Number,
    reading: Number,
    speaking: Number
  }
}
```

**Indexes:**
- `user_id`
- `start_time` (desc)
- `current_agent`

#### `progress`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  skill: String,                 // "pronunciation", "writing", "reading", "speaking", "vocabulary"
  overall_score: Number,         // 0-100
  recent_trend: String,          // "improving", "stable", "declining"
  weak_areas: [
    {
      area: String,              // "/θ/ phoneme", "past tense grammar"
      occurrences: Number,       // How many times struggled
      last_seen: DateTime,
      improvement_rate: Number,  // 0.15 = 15% improvement
      priority: String           // "high", "medium", "low"
    }
  ],
  historical_scores: [
    {
      date: DateTime,
      score: Number
    }
  ],
  last_updated: DateTime
}
```

**Indexes:**
- `user_id, skill` (compound, unique)
- `weak_areas.priority`

#### `curricula`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  language: String,              // Target language
  current_level: String,         // "A2"
  target_level: String,          // "B1"
  lesson_plan: [
    {
      day: Number,               // 1-30
      week: Number,
      activities: [
        {
          skill: String,         // "pronunciation", "writing", etc.
          topic: String,         // "th sounds", "past tense"
          duration_minutes: Number,
          difficulty: String,    // "easy", "medium", "hard"
          completed: Boolean,
          completed_at: DateTime
        }
      ]
    }
  ],
  created_at: DateTime,
  last_updated: DateTime
}
```

**Indexes:**
- `user_id` (unique)
- `lesson_plan.day, lesson_plan.activities.completed`

#### `vocabulary`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  word: String,
  language: String,              // "en", "es", etc.
  translations: Object,          // { "es": "serendipia", "fr": "sérendipité" }
  definition: String,
  example_sentences: [String],
  mastery_level: Number,         // 0-5 (Spaced Repetition System levels)
  next_review_date: DateTime,
  times_reviewed: Number,
  times_correct: Number,
  times_incorrect: Number,
  added_date: DateTime,
  last_reviewed: DateTime
}
```

**Indexes:**
- `user_id, word` (compound, unique)
- `next_review_date` (for scheduling reviews)
- `mastery_level`

---

## Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI | Async HTTP + WebSocket support |
| **Agent Framework** | AGNO | Multi-agent orchestration |
| **Database** | MongoDB | User data, sessions, progress |
| **Cache** | Redis (Phase 2) | WebSocket state, caching |
| **Storage** | AWS S3 / GCS | Audio file storage |
| **Task Queue** | Celery (Phase 3) | Background jobs (curriculum generation) |

### AI/ML Services

| Service | Purpose | Cost |
|---------|---------|------|
| **Gemini 2.0 Flash** | Primary LLM (native audio) | Variable by usage |
| **Speechace API** | Phoneme-level pronunciation | $99/month |
| **LanguageTool** | Grammar checking | Free (self-hosted) |

**Multi-Model Strategy (Cost Optimization):**
```python
# High intelligence agents (MainAgent, SpeakingCoach)
model = Gemini(id="gemini-2.0-flash")  # $0.30/1M input tokens

# Medium intelligence (PronunciationCoach, ReadingCoach, WritingCoach)
model = Gemini(id="gemini-1.5-flash")  # $0.075/1M input tokens

# Simple tasks (VocabularyCoach agent mode in Phase 3)
model = Gemini(id="gemini-1.5-flash-8b")  # $0.0375/1M input tokens
```

### API Architecture

#### HTTP Endpoints

```
POST   /api/users                      # Create user
GET    /api/users/{id}                 # Get user profile
PATCH  /api/users/{id}                 # Update user

POST   /api/sessions                   # Start session
GET    /api/sessions/{id}              # Get session details
PATCH  /api/sessions/{id}              # Update session
DELETE /api/sessions/{id}              # End session
GET    /api/sessions/user/{user_id}    # Get user's sessions

POST   /api/sessions/{id}/writing      # Submit writing activity
GET    /api/sessions/{id}/history      # Get session history

GET    /api/users/{id}/progress        # Get progress dashboard
GET    /api/users/{id}/weak-areas      # Get weak areas
GET    /api/users/{id}/curriculum      # Get curriculum

GET    /api/vocabulary/{user_id}       # Get vocabulary list
POST   /api/vocabulary/{user_id}       # Add word
GET    /api/vocabulary/{user_id}/due   # Get due reviews
```

#### WebSocket Endpoints

```
/ws/sessions/{session_id}  # Single persistent connection for entire session
```

**WebSocket Message Format (Bidirectional):**

```javascript
// CLIENT → SERVER Messages

// 1. User audio stream (continuous)
{
  "type": "user_audio",
  "audio_chunk": "<base64_audio>",
  "timestamp": "2026-01-18T10:30:00Z"
}

// 2. User actions (writing submitted, reading complete, etc.)
{
  "type": "user_action",
  "action": "writing_submitted",
  "content": "Yesterday, I went to the store...",
  "timestamp": "2026-01-18T10:35:00Z"
}

// 3. Session control
{
  "type": "session_control",
  "action": "pause" | "resume" | "end"
}

// SERVER → CLIENT Messages

// 1. Agent audio (voice response)
{
  "type": "agent_audio",
  "audio_chunk": "<base64_audio>",
  "agent": "main_agent" | "pronunciation_coach" | "writing_coach",
  "transcript": "Great job! You improved to 85%!"
}

// 2. Agent text (transcript only, no audio)
{
  "type": "agent_text",
  "text": "Let me show you the articulation guide...",
  "agent": "pronunciation_coach"
}

// 3. UI commands (dynamic UI switching)
{
  "type": "ui_command",
  "command": "show_drawing_board" | "show_waveform" | "show_pronunciation_viz" | "show_reading",
  "config": {
    "prompt": "Write about what you did yesterday",
    "duration_minutes": 10
  }
}

// 4. Real-time feedback (scores, phoneme analysis, etc.)
{
  "type": "feedback",
  "data": {
    "phoneme_scores": {
      "/θ/": 0.70,
      "/ɪ/": 0.95,
      "/ŋ/": 0.88
    },
    "waveform": [...],
    "ipa_target": "/θɪŋk/",
    "ipa_actual": "/tɪŋk/",
    "articulation_guide_url": "..."
  }
}

// 5. Activity complete (transition back to MainAgent)
{
  "type": "activity_complete",
  "activity_id": "act_001",
  "agent": "pronunciation_coach",
  "summary": {
    "target_phoneme": "/θ/",
    "attempts": 3,
    "scores": [0.40, 0.65, 0.85],
    "improvement": 0.45
  }
}

// 6. Session history update (for real-time transcript)
{
  "type": "transcript_update",
  "entry": {
    "role": "agent",
    "agent": "pronunciation_coach",
    "text": "Excellent! You improved to 85%!",
    "timestamp": "2026-01-18T10:32:00Z"
  }
}
```

**Voice Activity Detection (VAD):**
- Frontend uses `@ricky0123/vad-web` or similar library
- Automatically detects when user starts/stops speaking
- No manual "Record" or "Send" button required
- Streams audio chunks to backend in real-time

### Frontend (Not in Scope)

**Recommended Stack:**
- React/Vue/Svelte
- Web Audio API (recording/playback)
- WebSocket client
- Canvas API (drawing board for writing)
- Tailwind CSS (UI)

---

## Implementation Roadmap

### Phase 1: MVP - Pronunciation + Writing (Weeks 1-6)

**Goal:** Launch minimal viable product with 2 core skills

**Deliverables:**
1. ✅ Enhanced MainAgent with delegation logic
2. ✅ PronunciationCoachAgent (full agent) + WebSocket endpoint
3. ✅ WritingCoachAgent (full agent) + HTTP endpoint
4. ✅ Tools: SessionManager, PhonemeAnalysis (Speechace), GrammarAnalysis (LanguageTool)
5. ✅ MongoDB schemas: users, sessions, progress
6. ✅ Basic frontend: pronunciation UI, writing editor

**Critical Files:**
- `src/agents/mainAgent.py` - Enhance with AGNO Teams
- `src/agents/pronunciationAgent.py` - NEW
- `src/agents/writingAgent.py` - NEW
- `src/tools/session_tools.py` - NEW
- `src/tools/pronunciation_tools.py` - NEW
- `src/tools/writing_tools.py` - NEW
- `src/api/websocket.py` - NEW
- `src/api/routes.py` - NEW
- `src/models/database.py` - NEW
- `src/main.py` - Update with WebSocket + HTTP routes

**Launch Criteria:**
- ✅ User can create account
- ✅ User can practice pronunciation with real-time feedback
- ✅ User can write and receive grammar feedback
- ✅ Session history stored and viewable
- ✅ Basic progress tracking

**Effort:** 2 developers × 6 weeks = 480 hours

---

### Phase 2: Core Skills - Reading + Speaking (Weeks 7-12)

**Goal:** Complete all 4 core skill agents

**Deliverables:**
1. ✅ ReadingCoachAgent + WebSocket
2. ✅ SpeakingCoachAgent + WebSocket
3. ✅ Tools: ReadingAnalysis, FluencyAnalysis, ConversationManager
4. ✅ Frontend: reading interface, conversation view
5. ✅ Agent handoff optimization

**Launch Criteria:**
- ✅ All 4 skills functional (pronunciation, writing, reading, speaking)
- ✅ Seamless agent transitions (user doesn't notice handoffs)
- ✅ Real-time feedback working reliably (<100ms latency)
- ✅ Conversation feels natural

**Effort:** 2 developers × 6 weeks = 480 hours

---

### Phase 3: Intelligence - Curriculum + Vocabulary (Weeks 13-16)

**Goal:** Adaptive learning and vocabulary system

**Deliverables:**
1. ✅ CurriculumArchitect (background service)
2. ✅ VocabularyCoach (tool mode → agent mode)
3. ✅ WeakAreaAnalysisTool
4. ✅ SpacedRepetitionSchedulerTool (SM-2 algorithm)
5. ✅ Adaptive curriculum updates
6. ✅ AssessmentEngine (progress reports)

**Launch Criteria:**
- ✅ Personalized curriculum generated on onboarding
- ✅ Vocabulary flashcards functional
- ✅ Weak area identification working
- ✅ Proactive practice recommendations (with user control)
- ✅ Weekly progress reports

**Effort:** 2 developers × 4 weeks = 320 hours

---

### Phase 4: Polish + Scale (Weeks 17-20)

**Goal:** Production-ready, optimized, scalable

**Deliverables:**
1. ✅ Cost optimization (caching, model selection)
2. ✅ Performance optimization (database indexes, query optimization)
3. ✅ Error handling and recovery
4. ✅ Load testing (1000+ concurrent users)
5. ✅ UI/UX refinement
6. ✅ Mobile responsiveness
7. ✅ Complete documentation

**Launch Criteria:**
- ✅ Cost per user < $11/month
- ✅ 99.5% uptime SLA
- ✅ <100ms WebSocket latency
- ✅ Mobile responsive (iOS, Android)
- ✅ Complete API documentation
- ✅ Security audit passed

**Effort:** 3 developers × 4 weeks = 480 hours

---

## Cost Analysis

### Optimized Cost Structure (1000 users, 30 sessions/user/month)

| Component | Monthly Cost | Per-User Cost |
|-----------|--------------|---------------|
| MainAgent (orchestration) | $4,000 | $4.00 |
| PronunciationCoach | $750 | $0.75 |
| WritingCoach | $400 | $0.40 |
| ReadingCoach | $400 | $0.40 |
| SpeakingCoach | $1,000 | $1.00 |
| VocabularyCoach (tool mode) | $70 | $0.07 |
| Speechace API | $167 | $0.17 |
| LanguageTool (self-hosted) | $0 | $0.00 |
| MongoDB Atlas (M30) | $300 | $0.30 |
| Redis (ElastiCache) | $100 | $0.10 |
| S3 Storage (150GB audio) | $10 | $0.01 |
| Hosting (AWS EC2 t3.large × 2) | $200 | $0.20 |
| **TOTAL** | **$10,260** | **$10.26** |

### Pricing Model

| Tier | Price | Cost | Margin |
|------|-------|------|--------|
| **Free** | $0/month | $3.40/user | -$3.40 (acquisition) |
| | (10 sessions limit) | | |
| **Premium** | $14.99/month | $10.26/user | **$4.73 (32%)** |
| | (unlimited sessions) | | |

### Cost Optimization Strategies

1. **Agent Call Reduction** (~30% savings)
   - Direct sub-agent interaction (no MainAgent routing)
   - Batch activity results
   - Cache curriculum decisions

2. **Multi-Model Strategy** (~40% savings)
   - Use appropriate model tier per agent
   - Gemini 2.0 Flash for MainAgent/SpeakingCoach
   - Gemini 1.5 Flash for PronunciationCoach/ReadingCoach/WritingCoach
   - Gemini 1.5 Flash-8B for VocabularyCoach

3. **Smart Caching** (~15% savings)
   - Cache grammar explanations (common errors)
   - Cache articulation guides (phonemes don't change)
   - Cache curriculum templates
   - Use AGNO's memory to reduce context length

4. **Async Background Processing** (~5% savings)
   - Progress reports generated overnight
   - Curriculum adaptation via weekly batch job
   - Spaced repetition scheduling via daily batch

**Result:** 51% cost reduction vs naive implementation ($20.86 → $10.26)

---

## Multi-Language Support

### Architecture Strategy

**Key Insight:** Skill-based agents are **language-agnostic**. Teaching pronunciation is the same process regardless of language - only the **data** (phonemes, words, grammar rules) changes.

### Language-Specific vs Universal

| Universal (Same for All Languages) | Language-Specific |
|-----------------------------------|-------------------|
| Agent logic & pedagogy | Phoneme sets (IPA) |
| UI components | Grammar rules |
| Database schemas | Vocabulary databases |
| Session management | Curriculum content |
| Progress tracking | Error patterns |
| WebSocket/HTTP architecture | Speechace/LanguageTool configs |

### Implementation Approach

```python
def get_pronunciation_coach(user):
    """Create language-aware pronunciation coach"""

    # Language-aware prompt
    prompt = f"""
    You are a {user.target_language} pronunciation coach.
    Your student's native language is {user.native_language}.

    Teaching approach:
    - Use {user.target_language} primarily
    - When explaining difficult sounds, reference {user.native_language}
    - Be aware of common pronunciation challenges for
      {user.native_language} speakers learning {user.target_language}

    Examples:
    - Spanish speakers learning English often struggle with /θ/ and /ð/
    - English speakers learning Spanish struggle with /r/ vs /rr/
    - Mandarin speakers learning English struggle with /l/ vs /r/
    """

    # Language-specific tools
    tools = [
        PhonemeAnalysisTool(
            language=user.target_language,
            phoneme_set=get_ipa_phonemes(user.target_language)
        ),
        IPATranscriptionTool(language=user.target_language),
        ArticulationGuideTool(language=user.target_language)
    ]

    return Agent(
        name="PronunciationCoach",
        model=Gemini("gemini-1.5-flash"),
        instructions=prompt,
        tools=tools,
        db=MongoDb(db_url=MONGODB_URL)
    )
```

### Database Schema for Multi-Language

```javascript
// User
{
  native_language: "es",    // Spanish
  target_language: "en",    // Learning English
  ui_language: "es"         // Interface in Spanish
}

// Vocabulary
{
  word: "serendipity",
  language: "en",
  translations: {
    "es": "serendipia",
    "fr": "sérendipité",
    "zh": "意外发现"
  }
}

// Curriculum
{
  language: "en",
  level: "A2",
  lesson_plan: [...]
}
```

### Expansion Path

1. **Phase 1:** English (best tool support, largest market)
2. **Phase 2:** Spanish (large market, good tool support)
3. **Phase 3:** French (good tool support, established CEFR standards)
4. **Phase 4:** Mandarin (huge market, requires specialized pronunciation tools)
5. **Phase 5:** German (good tool support)

**Adding a New Language:**
1. Add language phoneme set to `PhonemeAnalysisTool`
2. Configure Speechace API for new language
3. Add grammar rules to `GrammarAnalysisTool`
4. Add vocabulary database for new language
5. Update agent prompts with language-specific teaching tips

**No new agents needed!** ✅

---

## Testing & Verification

### End-to-End Test Scenarios

#### Test 1: Pronunciation Practice Flow
```
1. User starts session → MainAgent greets
2. User: "Let's practice pronunciation"
3. MainAgent delegates to PronunciationCoachAgent
4. UI switches to pronunciation interface
5. User speaks target phrase "think"
6. PronunciationCoachAgent analyzes via Speechace
7. Real-time feedback displayed (phoneme scores, IPA, guidance)
8. User practices 3 times → improvement tracked (40% → 65% → 85%)
9. Agent completes activity → returns to MainAgent
10. MainAgent logs to session history with audio files
11. User can view session history with audio playback
✅ PASS if all steps complete successfully
```

#### Test 2: Writing Practice Flow
```
1. MainAgent suggests: "Let's work on past tense writing"
2. MainAgent delegates to WritingCoachAgent
3. UI switches to writing editor/drawing board
4. User writes paragraph with past tense errors
5. User submits
6. WritingCoachAgent analyzes via LanguageTool
7. Feedback displayed (errors highlighted, explanations shown)
8. Agent completes → returns to MainAgent
9. MainAgent identifies "past tense" as weak area
10. Progress updated in database
✅ PASS if past tense identified as weak area
```

#### Test 3: Weak Area Recommendation
```
1. User has struggled with "/θ/ phoneme" 3 times
2. WeakAreaAnalysisTool identifies pattern
3. MainAgent proactively suggests: "I noticed you struggle with 'th' sounds. Practice now?"
4. User accepts OR declines and chooses different topic
5. If accepted → delegates to PronunciationCoachAgent with /θ/ focus
6. Targeted drills on /θ/ phoneme
7. Improvement tracked over time
✅ PASS if recommendation appears and can be accepted/declined
```

### Performance Metrics (Target SLAs)

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| WebSocket latency | <100ms | <200ms |
| HTTP response time | <2 seconds | <5 seconds |
| Session state transitions | <50ms | <100ms |
| Database query time | <100ms | <500ms |
| Audio upload/download | <500ms | <2 seconds |
| Agent response time | <1 second | <3 seconds |

### Cost Monitoring Alerts

- Daily LLM API usage tracking
- Per-agent cost breakdown
- Alert if cost exceeds $12/user/month (20% buffer)
- Weekly cost optimization review
- Anomaly detection (sudden cost spikes)

---

## Security & Privacy

### Data Protection

1. **User Data Encryption**
   - Encrypt sensitive fields (email, passwords) at rest
   - Use HTTPS for all API communication
   - Audio files encrypted in S3

2. **Session Management**
   - JWT tokens for authentication
   - Session expiration (24 hours)
   - Rate limiting on API endpoints

3. **GDPR Compliance**
   - User data export functionality
   - Right to deletion (purge all user data)
   - Consent management for data collection

### API Security

```python
# Authentication middleware
@app.middleware("http")
async def authenticate(request: Request, call_next):
    token = request.headers.get("Authorization")
    if not verify_jwt(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)

# Rate limiting
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    user_id = get_user_from_request(request)
    if await redis.get(f"rate_limit:{user_id}") > 100:
        raise HTTPException(status_code=429, detail="Too many requests")
    await redis.incr(f"rate_limit:{user_id}", ex=60)
    return await call_next(request)
```

---

## Monitoring & Observability

### Logging

```python
import structlog

logger = structlog.get_logger()

# Log all agent interactions
logger.info(
    "agent_interaction",
    agent=agent_name,
    user_id=user_id,
    session_id=session_id,
    activity_type=activity_type,
    duration_ms=duration,
    success=success
)

# Log errors
logger.error(
    "agent_error",
    agent=agent_name,
    error=str(exception),
    traceback=traceback.format_exc()
)
```

### Metrics (Datadog / Prometheus)

- Request rate per endpoint
- Agent response time distribution
- WebSocket connection count
- LLM API latency
- Database query performance
- Cost per user per day

### Error Tracking (Sentry)

```python
import sentry_sdk

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1
)

# Automatic error capture
try:
    result = agent.chat(message)
except Exception as e:
    sentry_sdk.capture_exception(e)
    raise
```

---

## Deployment

### Infrastructure (AWS)

```yaml
# docker-compose.yml (development)
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongo
      - redis

  mongo:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7.2
    ports:
      - "6379:6379"

volumes:
  mongo_data:
```

### Production (Kubernetes)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mumble-ai-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mumble-ai-api
  template:
    metadata:
      labels:
        app: mumble-ai-api
    spec:
      containers:
      - name: api
        image: mumbleai/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: mumble-secrets
              key: mongodb-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

---

## Appendix

### Glossary

- **AGNO**: Multi-agent framework for orchestrating AI agents
- **IPA**: International Phonetic Alphabet
- **SRS**: Spaced Repetition System (algorithm for optimal review timing)
- **CEFR**: Common European Framework of Reference for Languages (A1-C2)
- **STT**: Speech-to-Text
- **TTS**: Text-to-Speech
- **SM-2**: Spaced Repetition algorithm (SuperMemo 2)

### References

- [AGNO Framework Documentation](https://docs.agno.com/)
- [Speechace API Documentation](https://www.speechace.com/docs/)
- [LanguageTool API](https://languagetool.org/http-api/)
- [CEFR Levels Explained](https://www.coe.int/en/web/common-european-framework-reference-languages)
- [SM-2 Algorithm](https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-supermemo-method)

---

## Contact

For questions or contributions, please refer to the project repository or contact the development team.

**Last Updated:** 2026-01-18
**Version:** 1.0
**Status:** ✅ Architecture Complete, Ready for Implementation
