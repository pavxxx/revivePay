import os
from sqlalchemy.orm import Session
from app.db.database import engine, Base, SessionLocal
from app.db.models import User, RecoveryPolicy, Customer, Payment, Subscription
from app.services.batch_service import run_demo_batch

def init_db(db: Session):
    """
    Initializes DB tables and seeds default user, policies, and initial demo batch data.
    Also applies any required one-time schema migrations for existing databases.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # One-time migration: rename policy_violations_prevented -> guardrail_interventions
    # (SQLite does not support column renaming directly; we ADD the new column if missing.)
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            cols = [
                row[1] for row in conn.execute(text("PRAGMA table_info(batch_runs)")).fetchall()
            ]
            if "guardrail_interventions" not in cols:
                conn.execute(text(
                    "ALTER TABLE batch_runs ADD COLUMN guardrail_interventions INTEGER DEFAULT 0"
                ))
                if "policy_violations_prevented" in cols:
                    conn.execute(text(
                        "UPDATE batch_runs SET guardrail_interventions = policy_violations_prevented"
                    ))
                conn.commit()
    except Exception:
        pass  # Non-SQLite databases or already migrated; skip silently.

    
    # Check default user
    admin_user = db.query(User).filter(User.email == "admin@revivepay.io").first()
    if not admin_user:
        admin_user = User(
            email="admin@revivepay.io",
            name="Merchant Ops Admin",
            role="ops_admin"
        )
        db.add(admin_user)

    # Check default policies
    default_policy = db.query(RecoveryPolicy).filter(RecoveryPolicy.rule_name == "STANDARD_FINTECH_GUARDRAILS").first()
    if not default_policy:
        default_policy = RecoveryPolicy(
            rule_name="STANDARD_FINTECH_GUARDRAILS",
            max_automated_retries=3,
            probability_floor=0.40,
            min_amount_escalate=50000.0,
            cooldown_hours=24,
            permanent_failure_categories_json=["PERMANENT_HARD_DECLINE", "FRAUD_OR_STOLEN"],
            is_active=True
        )
        db.add(default_policy)
        
    db.commit()

    # Seed initial demo batch if DB has 0 cases
    from app.db.models import RecoveryCase
    existing_cases = db.query(RecoveryCase).count()
    if existing_cases == 0:
        print("Seeding database with initial deterministic batch (150 events)...")
        run_demo_batch(db, batch_size=150)
        print("Database initial seeding complete.")

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    db.close()
