# CrisisInbox Hackathon Roadmap

**Event:** OpenEnv Hackathon @ Shack15, SF
**Dates:** Saturday March 7 – Sunday March 8, 2026
**Team Size:** 2
**Problem Statement:** 3.2 (Personalized Tasks) + Patronus AI Sub-Theme (Schema Drift)

---

## PHASE 1: Foundation (11:30 AM – 2:00 PM Saturday)

### Person A — Environment Setup

- [x] Read OpenEnv 0.2.1 docs thoroughly — understand environment structure, observation/action spaces, step function
- [x] Get a minimal "hello world" OpenEnv environment running locally
- [x] Define the core data model:
  - [x] `Message` object: sender, channel (6 types), content, urgency (critical/high/medium/low), deadline, dependencies, drift_flag, supersedes
  - [x] Task state tracked via environment internals (`_handled`, `_visible_messages`, deadline expiry) — no separate Task object needed since messages and tasks are 1:1
  - [x] World state tracked via environment instance vars (`_current_hour`, `_all_messages`, `_visible_messages`, `_handled`, `_score`, `_fired_drifts`, `_superseded`) — exposed to agent through `get_status` tool
- [x] Deploy bare-bones environment to HF Spaces — confirmed at eptan-crisis-inbox.hf.space
- [ ] Push initial scaffold to GitHub

### Person B — Training Pipeline Setup

- [x] Open Unsloth GRPO Colab notebook and run with a toy example end-to-end
- [x] Confirm training loop works: environment → agent action → reward → update
- [x] Define the action space — simplified to free-form: model outputs `respond_to_message(msg_id, "response")`, parsed via regex
- [x] Define observation space: full inbox snapshot as text prompt with urgency grouping, deadline warnings, drift flags, stale markers
- [x] Implement reward function (integrated in notebook `score_action()`):
  - [x] Urgency base: critical=10, high=5, medium=3, low=1
  - [x] Deadline timing: early bonus (up to +50%), late penalty (-75%)
  - [x] Schema drift adaptation: +50% for handling drift-flagged messages
  - [x] Stale info penalty: -50% for acting on superseded messages
  - [x] Response quality: -50% for short/empty responses
  - [x] Priority penalty: -70% for choosing low-urgency when critical messages exist
- [ ] Push training scaffold to GitHub

### Checkpoint — 2:00 PM

- [x] ✅ OpenEnv minimal environment runs locally
- [x] ✅ HF Spaces deployment pipeline confirmed
- [x] ✅ Unsloth GRPO training loop configured in notebook (Qwen2.5-0.5B + LoRA + GRPO)
- [x] ✅ Data model and reward function defined
- [ ] 🚨 If OpenEnv is blocking: simplify to gym-style env, wrap in OpenEnv later
- [ ] 🚨 If Unsloth is blocking: fall back to HF TRL directly

---

## PHASE 2: Core Build (2:00 PM – 6:00 PM Saturday)

### Person A — Environment Logic

- [x] Build message generation system:
  - [x] Create 18 sender profiles (Mom, Boss, Sister, Neighbor Dave, FEMA, NWS, State Farm, Delta Airlines, Oakwood Elementary, HR, Landlord, Coworker Sarah, PG&E, Red Cross, Bank of America, CVS Pharmacy, Sacramento County, Comcast)
  - [x] Write 76 messages across 48-hour simulated timeline
  - [x] Each message has: sender, channel, timestamp, urgency, deadline, content, dependencies, drift_flag, supersedes
  - [x] Organized into waves: initial crisis (hour 0-2), escalation (2-6), post-evacuation chaos (6-12), conflicting demands (12-20), drift events (20-30), recovery (26-36), ongoing management (32-40), final stretch (44-48)
- [x] Implement episode timeline engine:
  - [x] Messages arrive at scheduled sim-hours
  - [x] Time costs per action: reading = 0.1h, responding = 0.25h, advance_time tool = 0.5-4.0h
  - [x] Dependencies gate actions (must handle prerequisites first)
  - [x] Episode ends at hour 48
- [x] Build 5 schema drift events:
  - [x] Hour 20: Insurance deadline shortened from 72h to 48h
  - [x] Hour 21: Evacuation zone expanded to include Zone B (workplace)
  - [x] Hour 22.5: Employer emergency leave expanded (PTO → 5 days paid leave)
  - [x] Hour 24.5: Airline extends free rebooking window from 48h to 7 days
  - [x] Hour 34: FEMA adds new documentation requirements
- [x] Randomization: each episode triggers 3 of 5 drift events (seed-controlled)
- [x] Add episode variation: +/-15% jitter on arrival times, +/-10% on deadlines (seed-controlled)
- [x] Integrate with OpenEnv API: `reset()`, `step()` implemented; 5 MCP tools (get_inbox, read_message, respond_to_message, get_status, advance_time)

### Person B — Reward & Training Integration

- [x] Reward function implemented in two places:
  - [x] Environment-side: `_calculate_reward()` in `crisis_inbox_environment.py` (used during live episodes)
  - [x] Training-side: `score_action()` in notebook (parses model output, scores against inbox state)
- [x] Episode generator (`generate_episodes.py`) produces offline training data:
  - [x] 50 episodes, 803 training prompts across 16 decision points per episode
  - [x] Full message content, drift flags, superseded markers, dependency info
  - [x] Prompts include urgency grouping, deadline warnings, stale markers
- [x] Connect to Unsloth GRPO: notebook loads episodes.json, builds HF Dataset, configures GRPOTrainer
- [ ] Run training on Colab with GPU and capture reward curves
- [ ] Log reward components separately to identify which signals are working

### Checkpoint — 6:00 PM (Dinner)

- [x] ✅ Environment generates realistic message streams (76 messages, 19 senders)
- [x] ✅ Schema drift events fire correctly (tested: superseded messages marked, drift rewards working)
- [x] ✅ Training notebook configured with GRPO, reward function, and evaluation
- [ ] ✅ First reward curves from actual GPU training run
- [ ] 🚨 If messages aren't generating: reduce to 30 messages, fewer senders
- [ ] 🚨 If training isn't connecting: hardcode environment responses, focus on reward signal

---

## PHASE 3: Integration & Iteration (6:00 PM – 10:00 PM Saturday)

### Person A — Environment Polish

- [x] Polish message content for realism and emotional impact (20+ messages rewritten)
  - [x] Mom: panicked texting, crying voicemails, medical anxiety, guilt-trip to Tahoe
  - [x] Boss (Greg): passive-aggressive emails with signature, softens after Meridian postpones
  - [x] Sister: desperation about kids, voice cracking in voicemail, genuine gratitude
  - [x] Neighbor Dave: casual bro tone, guilt about Whiskers, neighborhood solidarity
  - [x] Emma (niece, age 7): 3 kid-perspective messages — pillow fights, scared in the dark, rainbow drawing
  - [x] FEMA/NWS: kept formal and information-dense (already good)
- [x] Test all 5 drift events fire correctly and change environment state
- [x] Verify dependency chains work (23 messages with dependencies, gated in respond_to_message)
- [x] Edge case handling: stale info penalized (-50% reward), expired deadlines tracked in get_status
- [x] Redeploy updated environment to HF Spaces (73 messages, timeline engine, drift events)
- [x] Test HF Spaces deployment works end-to-end remotely (verified via client)

### Person B — Training Optimization

- [ ] Analyze initial reward curves — identify flat or noisy components
- [ ] Tune reward weights: if one signal dominates, rebalance
- [ ] If training is flat overall:
  - [ ] Simplify action space (reduce to 4 actions)
  - [ ] Increase reward magnitudes
  - [ ] Reduce episode length
- [ ] Log specific before/after agent behaviors:
  - [ ] Capture untrained agent: responds in order, ignores evacuation alert
  - [ ] Capture trained agent: triages safety first, adapts to drift
- [ ] Save training checkpoints and reward curve data for demo
- [ ] Target: 200-500 episodes with visible upward trend

### Checkpoint — 10:00 PM (Doors Close)

- [x] ✅ Environment fully functional with drift events on HF Spaces
- [ ] ✅ Training curves show upward trend (pending GPU run)
- [ ] ✅ At least 2 clear before/after behavior examples captured
- [ ] ✅ All code pushed to GitHub
- [ ] 🚨 If reward curves are flat: simplify environment overnight, retrain Sunday AM
- [ ] 🚨 If HF Spaces is broken: prepare local demo as backup
- [ ] Both teammates agree on Sunday morning priority list before leaving

---

## PHASE 4: Sunday Polish (9:00 AM – 12:00 PM Sunday)

### Person A — Demo & Presentation

- [x] Build demo display (`demo.py`): terminal-based visualization
  - [x] Color-coded urgency levels (red bg = critical, red = high, yellow = medium, green = low)
  - [x] Schema drift notifications with magenta banner
  - [x] Agent action visualization with blue banner and reward display
  - [x] Two strategies: smart triage vs naive (arrival order)
  - [x] Comparison mode shows 55% improvement (157.8 vs 101.8 pts)
  - [x] Coverage breakdown by urgency with ASCII progress bars
- [x] HF Spaces deployment live with polished environment
- [x] Write repo README:
  - [x] Scenario hook, three layers of difficulty, sender profiles table
  - [x] MCP tools table, reward function table, episode variation details
  - [x] Quick start (hosted + local), repo structure, tech stack
- [ ] Draft the 3-minute pitch outline:
  - [ ] 0:00-0:30 — The scenario hook ("A wildfire just hit. You have 47 unread messages.")
  - [ ] 0:30-1:30 — Show the environment: message stream, drift events, conflicting tasks
  - [ ] 1:30-2:15 — Untrained vs trained agent comparison
  - [ ] 2:15-2:45 — Reward curves and training results
  - [ ] 2:45-3:00 — Why this matters (real-world impact close)

### Person B — Training & Artifacts

- [ ] Run final training session for cleanest possible reward curves
- [ ] Export reward curve plots (all 5 components + composite)
- [ ] Export 3 specific before/after examples with clear narrative:
  - [ ] Example 1: Untrained ignores FEMA evacuation → Trained prioritizes it first
  - [ ] Example 2: Untrained misses insurance deadline after policy change → Trained adapts
  - [ ] Example 3: Untrained sends form-letter reply to Mom → Trained matches emotional tone
- [x] Finalize Colab notebook:
  - [x] Clean, commented code with markdown sections
  - [x] Reward function with test cases (good action vs bad action vs junk)
  - [x] Evaluation cell comparing trained model choices
  - [ ] Reward curves visible when run (pending GPU run)
- [ ] Verify all required artifacts exist:
  - [ ] Public GitHub repo
  - [ ] HF Spaces deployment
  - [ ] Colab training notebook
  - [ ] YouTube video (not yet recorded)

### Checkpoint — 12:00 PM

- [x] ✅ Demo runs smoothly end-to-end (smart vs naive comparison, 55% improvement)
- [ ] ✅ Reward curves are clean and trend upward (pending GPU run)
- [ ] ✅ Before/after examples are compelling (pending GPU run)
- [x] ✅ README is complete
- [x] ✅ Colab notebook is clean (14 cells, markdown sections, reward function tests)
- [ ] 🚨 If demo is buggy: simplify to scripted walkthrough of one episode
- [ ] 🚨 If reward curves are still flat: show qualitative behavior improvement instead

---

## PHASE 5: Record & Submit (12:00 PM – 1:00 PM Sunday)

### Both Together

- [ ] Record one-minute YouTube video:
  - [ ] Person A: voiceover narration
  - [ ] Person B: screen capture / screen share
  - [ ] Structure:
    - [ ] 0:00-0:15 — "CrisisInbox: training AI to triage personal tasks during disasters"
    - [ ] 0:15-0:35 — Show environment: messages arriving, drift event firing
    - [ ] 0:35-0:50 — Before/after: untrained fails → trained succeeds
    - [ ] 0:50-1:00 — Flash reward curves, close with impact statement
  - [ ] Upload to YouTube (unlisted is fine)
- [ ] Rehearse 3-minute live pitch at least twice out loud
- [ ] Prepare for Q&A — practice answers to:
  - [ ] "Why is this hard for LLMs?"
  - [ ] "How does schema drift work specifically?"
  - [ ] "What would you build next with more time?"
  - [ ] "How is this different from a standard chatbot?"
  - [ ] "How does the reward function handle edge cases?"
- [ ] **SUBMIT via Cerebral Valley form:**
  - [ ] GitHub repo URL (public)
  - [ ] HF Spaces URL
  - [ ] YouTube video URL
  - [ ] Colab notebook URL
  - [ ] Select problem statement 3.2 + Patronus AI sub-theme
  - [ ] Confirm submission received

---

## FINAL CHECKLIST — Before Judging Starts (1:15 PM Sunday)

- [ ] GitHub repo is public and all code is pushed
- [ ] HF Spaces deployment is live and accessible
- [ ] Colab notebook runs end-to-end
- [ ] YouTube video is uploaded and link works
- [ ] Submission form completed
- [ ] Both teammates can explain every part of the project
- [ ] Laptop charged for demo
- [ ] Demo runs without internet (backup plan if WiFi fails)

---

## EMERGENCY FALLBACKS

| Problem | Fallback |
|---------|----------|
| OpenEnv won't work | Build gym-style env, wrap in OpenEnv interface last |
| HF Spaces deploy fails | Run demo locally, screenshot HF attempt for judges |
| Training won't converge | Simplify to 3 actions, 20 messages, 2 drift events |
| Reward curves flat | Show qualitative behavior change, explain reward design |
| YouTube upload fails | Screen-record on phone, upload from mobile |
| One teammate burns out | Other covers — both should understand full stack |

---

## KEY RULE

**If something isn't working after 45 minutes, simplify. A working simple version always beats a broken ambitious one.**
