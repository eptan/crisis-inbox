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

- [ ] Open Unsloth GRPO Colab notebook and run with a toy example end-to-end
- [ ] Confirm training loop works: environment → agent action → reward → update
- [ ] Define the action space (discrete, 6 options):
  - [ ] `RESPOND_URGENT` — handle highest urgency message
  - [ ] `RESPOND_SPECIFIC(id)` — handle a specific message
  - [ ] `DEFER` — push current top message to later
  - [ ] `BATCH_RESPOND` — send quick replies to low-urgency messages
  - [ ] `CHECK_UPDATES` — scan for policy/schema changes
  - [ ] `TAKE_ACTION` — execute a multi-step task (e.g., take photos → submit claim)
- [ ] Define observation space: current inbox snapshot, time remaining, active tasks, recent drift events
- [ ] Draft reward function with 5 components:
  - [ ] Safety priority: +10 responding to safety messages in top 3 actions, -10 ignoring
  - [ ] Deadline compliance: +5 per task completed before deadline, -5 per miss
  - [ ] Schema drift adaptation: +10 for changing behavior after policy update, -10 for acting on stale info
  - [ ] Tone appropriateness: +3 for matching tone to recipient, -3 for mismatch
  - [ ] Coverage: +2 per task addressed, -1 per task completely ignored
- [ ] Push training scaffold to GitHub

### Checkpoint — 2:00 PM

- [x] ✅ OpenEnv minimal environment runs locally
- [x] ✅ HF Spaces deployment pipeline confirmed
- [ ] ✅ Unsloth GRPO training loop runs end-to-end with toy env
- [x] ✅ Data model and reward function defined
- [ ] 🚨 If OpenEnv is blocking: simplify to gym-style env, wrap in OpenEnv later
- [ ] 🚨 If Unsloth is blocking: fall back to HF TRL directly

---

## PHASE 2: Core Build (2:00 PM – 6:00 PM Saturday)

### Person A — Environment Logic

- [x] Build message generation system:
  - [x] Create 18 sender profiles (Mom, Boss, Sister, Neighbor Dave, FEMA, NWS, State Farm, Delta Airlines, Oakwood Elementary, HR, Landlord, Coworker Sarah, PG&E, Red Cross, Bank of America, CVS Pharmacy, Sacramento County, Comcast)
  - [x] Write 73 messages across 48-hour simulated timeline
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
- [ ] Add episode variation: slight randomization of message arrival times and deadlines
- [x] Integrate with OpenEnv API: `reset()`, `step()` implemented; 5 MCP tools (get_inbox, read_message, respond_to_message, get_status, advance_time)

### Person B — Reward & Training Integration

- [ ] Implement reward function as standalone module (`reward.py`):
  - [ ] `calc_safety_priority(action, inbox_state) → float`
  - [ ] `calc_deadline_compliance(completed_tasks, current_time) → float`
  - [ ] `calc_drift_adaptation(action, drift_events, agent_beliefs) → float`
  - [ ] `calc_tone_score(response, recipient) → float`
  - [ ] `calc_coverage(addressed_tasks, total_tasks) → float`
  - [ ] `total_reward() → weighted sum`
- [ ] Connect Person A's environment to Unsloth GRPO training script
- [ ] Start initial training runs as soon as env is minimally functional (even with placeholder messages)
- [ ] Log reward components separately to identify which signals are working
- [ ] Begin iterating on reward weights based on early curves

### Checkpoint — 6:00 PM (Dinner)

- [x] ✅ Environment generates realistic message streams (73 messages, 18 senders)
- [x] ✅ Schema drift events fire correctly (tested: superseded messages marked, drift rewards working)
- [ ] ✅ Training script runs against real environment
- [ ] ✅ First reward curves exist (even if noisy)
- [ ] 🚨 If messages aren't generating: reduce to 30 messages, fewer senders
- [ ] 🚨 If training isn't connecting: hardcode environment responses, focus on reward signal

---

## PHASE 3: Integration & Iteration (6:00 PM – 10:00 PM Saturday)

### Person A — Environment Polish

- [ ] Polish message content for realism and emotional impact
  - [ ] Mom messages should feel like a real panicking parent
  - [ ] Boss messages should feel passive-aggressive then shift after policy change
  - [ ] FEMA messages should be formal and information-dense
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

- [ ] ✅ Environment fully functional with drift events on HF Spaces
- [ ] ✅ Training curves show upward trend
- [ ] ✅ At least 2 clear before/after behavior examples captured
- [ ] ✅ All code pushed to GitHub
- [ ] 🚨 If reward curves are flat: simplify environment overnight, retrain Sunday AM
- [ ] 🚨 If HF Spaces is broken: prepare local demo as backup
- [ ] Both teammates agree on Sunday morning priority list before leaving

---

## PHASE 4: Sunday Polish (9:00 AM – 12:00 PM Sunday)

### Person A — Demo & Presentation

- [ ] Build demo display: clean readable output showing inbox state during an episode
  - [ ] Color-coded urgency levels (red = safety, yellow = urgent, green = low)
  - [ ] Visible drift event notifications
  - [ ] Show agent's action choices in real-time
- [ ] Final HF Spaces deployment with polished environment
- [ ] Write repo README:
  - [ ] Project description (2-3 sentences)
  - [ ] The problem (why this matters)
  - [ ] Environment design (message system, drift events, dependencies)
  - [ ] Reward function (5 components)
  - [ ] Tech stack (OpenEnv 0.2.1, Unsloth GRPO, HF Spaces)
  - [ ] Team names
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
- [ ] Finalize Colab notebook:
  - [ ] Clean, commented code
  - [ ] Reward curves visible when run
  - [ ] Easy for judges to follow
- [ ] Verify all required artifacts exist:
  - [ ] Public GitHub repo
  - [ ] HF Spaces deployment
  - [ ] Colab training notebook
  - [ ] YouTube video (not yet recorded)

### Checkpoint — 12:00 PM

- [ ] ✅ Demo runs smoothly end-to-end
- [ ] ✅ Reward curves are clean and trend upward
- [ ] ✅ Before/after examples are compelling
- [ ] ✅ README is complete
- [ ] ✅ Colab notebook is clean
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
