# CrisisInbox

An reinforcement learning environment built on OpenEnv 0.2.1 for training language models to manage personal task overload during natural disasters.

## The Problem

When disaster strikes, people are overwhelmed with competing demands — evacuation alerts, insurance deadlines, employer communications, family coordination, travel rebooking — all arriving simultaneously with shifting rules and shrinking timelines. Most people make poor decisions under this cognitive load, missing critical deadlines and deprioritizing safety.

## The Environment

CrisisInbox simulates a 48-hour post-disaster scenario where an agent must triage and respond to a stream of messages across multiple channels. The environment features:

- **Realistic message streams** from family, employers, government agencies, insurance companies, and service providers
- **Conflicting obligations** with no clean solutions — forcing genuine prioritization
- **Schema drift** — policies, deadlines, and rules change mid-episode (evacuation zones expand, insurance requirements update, employer policies shift)
- **Dependency chains** — some actions require completing prerequisites first
- **Cognitive overload** — more tasks arrive than can be handled, requiring strategic triage

## Reward Function

Multi-signal reward based on: safety prioritization, deadline compliance, schema drift adaptation, tone appropriateness, and task coverage.

## Stack

- **Environment:** OpenEnv 0.2.1 deployed on HF Spaces
- **Training:** Unsloth GRPO via Google Colab
- **Problem Statement:** 3.2 (Personalized Tasks) + Patronus AI Sub-Theme (Schema Drift)

## Team

Built at the OpenEnv Hackathon, March 7-8, 2026