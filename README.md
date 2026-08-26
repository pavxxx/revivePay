# RevivePay — Autonomous Revenue Recovery Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14%2B-000000.svg)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![scikit--learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E.svg)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0%2B-11557C.svg)](https://xgboost.readthedocs.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-4169E1.svg)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-D71F00.svg)](https://www.sqlalchemy.org/)
[![Razorpay](https://img.shields.io/badge/Razorpay-Test%20Mode-0C2340.svg)](https://razorpay.com/)

> **RevivePay detects at-risk revenue, predicts recovery probability, takes policy-controlled recovery actions, and measures the money actually recovered.**

RevivePay is an autonomous revenue recovery platform designed for high-volume merchant operations.

When a payment fails, RevivePay does more than identify the failure. It analyzes the payment and customer context, estimates the probability of successful recovery using machine learning, determines an appropriate intervention, validates that intervention against deterministic safety policies, executes the permitted action through a unified payment service, and records the complete decision trail.

### Core Loop

**Detect → Diagnose → Predict → Decide → Guard → Act → Measure → Audit**

---

## 🎯 The Problem

Payment failures create revenue leakage for merchants.

A failed payment does not necessarily mean permanently lost revenue. Some failures are temporary and recoverable, while others should not be retried automatically.

The challenge is therefore not simply:

> "Which payments failed?"

It is:

> **"Which failed payments are worth recovering, what action should be taken, when should automation stop, and how much revenue was actually recovered?"**

Traditional retry systems can repeatedly attempt unsuitable transactions, waste recovery opportunities, or lack sufficient visibility into why an action was taken.

RevivePay addresses this with a combination of:

- Machine learning-based recovery prediction
- Deterministic decision logic
- Policy and safety guardrails
- Controlled recovery execution
- Human escalation
- Batch-level revenue measurement
- End-to-end auditability

---

# 🚀 What RevivePay Does

For every eligible failed-payment case, RevivePay follows this workflow:

```text
Payment Failure
      ↓
Revenue-at-Risk Identification
      ↓
Customer + Payment Context
      ↓
Failure Classification
      ↓
ML Recovery Probability
      ↓
Recovery Decision
      ↓
Policy / Guardrail Validation
      ↓
┌─────────────┬──────────────┬────────────┐
│   APPROVE   │   ESCALATE   │    STOP    │
└──────┬──────┴───────┬──────┴─────┬──────┘
       ↓              ↓             ↓
   Execute         Human Ops      Close
       ↓
   Outcome
       ↓
Revenue Recovered
       ↓
Audit Trail
       ↓
Batch Metrics
