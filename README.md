# RevivePay — Autonomous AI Revenue Recovery Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-000000.svg)](https://nextjs.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-11557C.svg)](https://xgboost.readthedocs.io)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D70A53.svg)](https://www.sqlalchemy.org)
[![Razorpay](https://img.shields.io/badge/Razorpay-Test%20Mode-0C2340.svg)](https://razorpay.com)

**RevivePay** is an autonomous revenue recovery platform engineered for high-volume merchant operations. It detects payment failures, predicts recovery probability using machine learning, executes deterministic interventions guarded by policy rules, interacts with payment gateways via a unified `PaymentService` abstraction, and maintains an immutable audit trail.

> **Zero LLM in Financial Decision Path**: All financial decision making, ML probability inference, policy enforcement, and payment execution operate 100% deterministically without relying on LLMs.
> **Environment Label**: Operating in **SIMULATION** / **RAZORPAY TEST MODE**. All monetary figures are generated dynamically from database records.

---

## Key Features

1. **Autonomous Core Loop**: **Detect → Diagnose → Predict → Decide → Guard → Act → Measure → Audit**
2. **Machine Learning Model Engine**:
   - Feature extraction across customer tenure, payment history, failure categories, and prior recovery attempts.
   - Evaluates Logistic Regression, Random Forest, and XGBoost models.
   - Validated metrics report: Precision, Recall, F1 Score, ROC-AUC, Confusion Matrix, and Calibration Curve.
3. **Deterministic Decision Engine**:
   - Maps probability score, failure category, customer history, and retry counts to explicit actions: `RETRY`, `WAIT_AND_RETRY`, `SEND_RECOVERY_NOTIFICATION`, `REQUEST_CUSTOMER_ACTION`, `ESCALATE`, `STOP`.
4. **Policy Guardrail Engine**:
   - Mandatory safety check enforcing max automated retry limits (default 3), probability floors (e.g. <0.40 -> STOP), high-value amount thresholds (e.g. >= ₹50,000 -> ESCALATE), permanent failure hard stops, and cooldown periods.
5. **Unified PaymentService Abstraction**:
   - Single interface wrapping both live Razorpay Test Mode API and a deterministic scenario simulator.
6. **Immutable Audit Trail**:
   - Records every event with actor context (`SYSTEM`, `ML_MODEL`, `DECISION_ENGINE`, `POLICY_ENGINE`, `PAYMENT_SERVICE`, `HUMAN_OPERATOR`), action, reasoning, and metadata.
7. **Batch Evaluation Engine**:
   - Executes 500-event demo batches and computes all aggregate KPIs live from database tables.

---

## System Architecture

```mermaid
graph TD
    A[Payment Ingestion / Webhook] --> B[FastAPI Agent Workflow]
    B --> C[Context Collection & Customer History DB]
    C --> D[ML Feature Extractor]
    D --> E[XGBoost / ML Model Predictor P(Recovery)]
    E --> F[Deterministic Decision Engine]
    F --> G{Policy Guardrail Engine}
    
    G -- Violation / High Amount --> H[Escalate to Human Ops Review]
    G -- Hard Decline / Low Prob --> I[Stop Recovery Automation]
    G -- Approved Action --> J[PaymentService Abstraction]
    
    J -- Test Mode / Sim --> K[Razorpay / Simulator Gateway]
    K --> L[Outcome Recorder & DB Audit Event Stream]
    L --> M[Next.js Fintech Dashboard]
```

---

## Agent Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> EVENT_RECEIVED: Failed Payment Ingested
    EVENT_RECEIVED --> CONTEXT_COLLECTION: Fetch Customer & Payment History
    CONTEXT_COLLECTION --> FAILURE_ANALYSIS: Classify Decline Category
    FAILURE_ANALYSIS --> RECOVERY_PREDICTION: Calculate P(Recovery) via ML
    RECOVERY_PREDICTION --> RECOVERY_PLAN: Select Recommended Intervention
    RECOVERY_PLAN --> POLICY_CHECK: Evaluate Guardrail Safety Rules
    
    POLICY_CHECK --> EXECUTE: Policy Approved
    POLICY_CHECK --> ESCALATE: Rule Violated / High Value Breach
    POLICY_CHECK --> STOP: Permanent Decline / Prob < Floor
    
    EXECUTE --> MEASURE: Execute via PaymentService
    MEASURE --> AUDIT: Record Recovered Revenue & Retries
    ESCALATE --> HUMAN_REVIEW: Merchant Ops Manual Action
    
    HUMAN_REVIEW --> EXECUTE: Manual Approve
    HUMAN_REVIEW --> STOP: Manual Stop
    
    AUDIT --> [*]
    STOP --> [*]
```

---

## Decision Flow Chart

```mermaid
flowchart TD
    Start[Input: Case Data + P(Recovery)] --> PermCheck{Category in Permanent Failures?}
    PermCheck -- Yes (Fraud/Stolen) --> StopAct[Action: STOP]
    PermCheck -- No --> AmtCheck{Amount >= ₹50,000?}
    
    AmtCheck -- Yes --> EscAct[Action: ESCALATE]
    AmtCheck -- No --> RetryCheck{Retry Count >= 3?}
    
    RetryCheck -- Yes --> EscAct
    RetryCheck -- No --> ProbCheck{P(Recovery) < 0.40?}
    
    ProbCheck -- Yes --> StopAct
    ProbCheck -- No --> CatCheck{Failure Category?}
    
    CatCheck -- TRANSIENT_NETWORK --> Retry[Action: RETRY]
    CatCheck -- INSUFFICIENT_FUNDS --> WaitRetry[Action: WAIT_AND_RETRY]
    CatCheck -- AUTHENTICATION_REQUIRED --> AuthAction[Action: REQUEST_CUSTOMER_ACTION]
    CatCheck -- CARD_EXPIRED --> Notif[Action: SEND_RECOVERY_NOTIFICATION]
```
---

## Demo Scenario Verification Matrix

When running the **Run Demo Batch (500 Events)** action from the UI, the following deterministic scenarios are exercised:

| Scenario | Condition / Inputs | Agent State Transition | Final Status |
| :--- | :--- | :--- | :--- |
| **Scenario A** | Strong history + Transient network failure | `PREDICT` → `DECIDE(RETRY)` → `POLICY_PASS` → `EXECUTE` | `RECOVERED` |
| **Scenario B** | Poor history + Low probability (<0.40) | `PREDICT` → `DECIDE(STOP)` → `POLICY_STOP` | `STOPPED` |
| **Scenario C** | High Amount (>₹50,000) or 3 Retries | `PREDICT` → `DECIDE(ESCALATE)` → `POLICY_ESCALATE` | `ESCALATED` |
| **Scenario D** | Permanent failure (Card Stolen/Hard Decline) | `PREDICT` → `DECIDE(STOP)` → `POLICY_STOP` | `STOPPED` |
| **Scenario E** | Subscription renewal + Insufficient funds | `PREDICT` → `DECIDE(WAIT_AND_RETRY)` → `POLICY_PASS` | `IN_PROGRESS` / `RECOVERED` |

---

## Local Setup & Quickstart

### Prerequisites
- Python 3.10+
- Node.js v18+ & npm

### 1. Environment Configuration
Copy the example environment file:
```bash
cp .env.example .env
```

### 2. Backend Setup & Test Execution
```bash
cd backend
python -m pip install -r requirements.txt

# Run Unit & Integration Tests (18 tests)
python -m pytest -v

# Start FastAPI Backend Server
python -m uvicorn app.main:app --reload --port 8000
```
Backend Swagger API Documentation available at: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup & Launch
```bash
cd frontend
npm install
npm run dev
```
Open Web Application in browser: `http://localhost:3000`

