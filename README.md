# RevivePay — Autonomous AI Revenue Recovery Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14%2B-000000.svg)](https://nextjs.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E.svg)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0%2B-11557C.svg)](https://xgboost.readthedocs.io)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-D70A53.svg)](https://www.sqlalchemy.org)
[![Razorpay](https://img.shields.io/badge/Razorpay-Test%20Mode-0C2340.svg)](https://razorpay.com)

**RevivePay** is an autonomous revenue recovery platform built for high-volume merchant operations. It detects failed payments, predicts recovery probability using machine learning, selects the safest intervention, executes approved actions, and maintains a complete audit trail.

> **Zero LLM in Financial Decision Path:** Financial decisions, ML predictions, policy enforcement, and payment execution operate without LLMs.

> **Environment:** Simulation / Razorpay Test Mode. All monetary values are generated dynamically from database records.

---

## Key Features

- **Autonomous Recovery Loop:** Detect → Diagnose → Predict → Decide → Guard → Act → Measure → Audit
- **ML Prediction:** Logistic Regression, Random Forest, and XGBoost for recovery probability.
- **Deterministic Decision Engine:** Selects actions such as Retry, Wait & Retry, Customer Action, Escalate, or Stop.
- **Policy Guardrails:** Retry limits, probability thresholds, high-value escalation, permanent-failure stops, and cooldown rules.
- **PaymentService:** Unified abstraction for Razorpay Test Mode and deterministic simulation.
- **Audit Trail:** Records decisions, actions, reasoning, policy results, and outcomes.
- **Batch Evaluation:** Supports 500-event demo batches with live recovery KPIs.

---

## System Architecture

```mermaid
flowchart TD
    A["Payment Ingestion / Webhook"] --> B["FastAPI Agent Workflow"]
    B --> C["Customer & Payment History"]
    C --> D["ML Feature Extraction"]
    D --> E["ML Model Predictor"]
    E --> F["Deterministic Decision Engine"]
    F --> G{"Policy Guardrails"}

    G -->|"Approved"| H["PaymentService"]
    G -->|"Escalate"| I["Human Operations Review"]
    G -->|"Stop"| J["Stop Recovery"]

    I -->|"Manual Approval"| H
    H --> K["Razorpay Test Mode / Simulator"]
    K --> L["Outcome Recorder + Audit Trail"]
    L --> M["Next.js Dashboard"]
```

## Agent Workflow

stateDiagram-v2
    [*] --> Received

    Received --> Context: Payment Failed
    Context --> Analysis: Fetch History
    Analysis --> Prediction: Classify Failure
    Prediction --> Plan: Calculate Recovery Probability
    Plan --> Policy: Select Intervention

    Policy --> Execute: Approved
    Policy --> Escalate: Rule Violated
    Policy --> Stop: Unsafe / Low Probability

    Execute --> Measure: PaymentService
    Measure --> Audit: Record Outcome

    Escalate --> HumanReview: Merchant Review
    HumanReview --> Execute: Approve
    HumanReview --> Stop: Reject

    Audit --> [*]
    Stop --> [*]
