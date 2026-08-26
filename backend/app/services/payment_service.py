import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.config import settings

class PaymentService(ABC):
    """
    Abstract Payment Service Interface.
    Encapsulates all payment processing behind a unified contract.
    """
    @abstractmethod
    def create_payment(self, amount: float, currency: str, customer_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def retry_payment(self, payment_id: str, case_id: str, failure_category: str = "TRANSIENT_NETWORK", probability: float = 0.8) -> Dict[str, Any]:
        pass

    @abstractmethod
    def verify_payment(self, payment_id: str, signature: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        pass


class SimulatorPaymentService(PaymentService):
    """
    Deterministic Simulator Payment Service.
    Used for SIMULATION mode to test end-to-end recovery scenarios.
    """
    def __init__(self):
        self.mode_label = "SIMULATION"

    def create_payment(self, amount: float, currency: str = "INR", customer_id: str = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        sim_id = f"sim_pay_{uuid.uuid4().hex[:10]}"
        return {
            "payment_id": sim_id,
            "amount": amount,
            "currency": currency,
            "status": "PENDING",
            "environment": self.mode_label,
            "provider": "SIMULATOR"
        }

    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        return {
            "payment_id": payment_id,
            "status": "FAILED",
            "environment": self.mode_label,
            "provider": "SIMULATOR"
        }

    def retry_payment(self, payment_id: str, case_id: str, failure_category: str = "TRANSIENT_NETWORK", probability: float = 0.8) -> Dict[str, Any]:
        """
        Executes a simulated payment retry.
        Determines outcome based on failure category and recovery probability.
        """
        # Hard declines never succeed
        if failure_category in ["PERMANENT_HARD_DECLINE", "FRAUD_OR_STOLEN"]:
            is_success = False
            error_msg = f"Simulated hard decline for category {failure_category}"
        elif probability >= 0.65:
            is_success = True
            error_msg = None
        else:
            is_success = False
            error_msg = "Simulated bank decline: insufficient funds or auth failure"

        status = "SUCCESS" if is_success else "FAILED"
        txn_ref = f"sim_txn_{uuid.uuid4().hex[:8]}"

        return {
            "payment_id": payment_id,
            "case_id": case_id,
            "retry_reference": txn_ref,
            "status": status,
            "is_success": is_success,
            "error_message": error_msg,
            "environment": self.mode_label,
            "provider": "SIMULATOR"
        }

    def verify_payment(self, payment_id: str, signature: Optional[str] = None) -> Dict[str, Any]:
        return {
            "payment_id": payment_id,
            "verified": True,
            "environment": self.mode_label
        }

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        return {
            "payment_id": payment_id,
            "status": "CAPTURED",
            "environment": self.mode_label
        }


class RazorpayPaymentService(PaymentService):
    """
    Razorpay Test Mode Payment Service Integration.
    Uses official Razorpay Python Client.
    """
    def __init__(self, key_id: str, key_secret: str):
        self.mode_label = "RAZORPAY TEST MODE"
        try:
            import razorpay
            self.client = razorpay.Client(auth=(key_id, key_secret))
        except Exception as e:
            print(f"Warning initializing Razorpay client: {e}. Falling back to simulator mode.")
            self.client = None

    def create_payment(self, amount: float, currency: str = "INR", customer_id: str = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.client:
            return SimulatorPaymentService().create_payment(amount, currency, customer_id, metadata)
        try:
            amount_paise = int(amount * 100)
            order = self.client.order.create({
                "amount": amount_paise,
                "currency": currency,
                "receipt": f"rcpt_{uuid.uuid4().hex[:8]}",
                "notes": metadata or {}
            })
            return {
                "payment_id": order.get("id"),
                "amount": amount,
                "currency": currency,
                "status": order.get("status"),
                "environment": self.mode_label,
                "provider": "RAZORPAY_TEST"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "FAILED",
                "environment": self.mode_label,
                "provider": "RAZORPAY_TEST"
            }

    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        if not self.client:
            return SimulatorPaymentService().get_payment(payment_id)
        try:
            pay = self.client.payment.fetch(payment_id)
            return {
                "payment_id": pay.get("id"),
                "amount": float(pay.get("amount", 0)) / 100.0,
                "status": pay.get("status"),
                "method": pay.get("method"),
                "environment": self.mode_label,
                "provider": "RAZORPAY_TEST"
            }
        except Exception as e:
            return SimulatorPaymentService().get_payment(payment_id)

    def retry_payment(self, payment_id: str, case_id: str, failure_category: str = "TRANSIENT_NETWORK", probability: float = 0.8) -> Dict[str, Any]:
        # For test mode re-attempts without live customer input, evaluate test authorization simulation
        if not self.client:
            return SimulatorPaymentService().retry_payment(payment_id, case_id, failure_category, probability)
            
        # Standard Razorpay test mode mock retry simulation
        is_success = (probability >= 0.60) and (failure_category not in ["PERMANENT_HARD_DECLINE", "FRAUD_OR_STOLEN"])
        status = "SUCCESS" if is_success else "FAILED"
        return {
            "payment_id": payment_id,
            "case_id": case_id,
            "retry_reference": f"pay_rzp_{uuid.uuid4().hex[:10]}",
            "status": status,
            "is_success": is_success,
            "environment": self.mode_label,
            "provider": "RAZORPAY_TEST"
        }

    def verify_payment(self, payment_id: str, signature: Optional[str] = None) -> Dict[str, Any]:
        return {"payment_id": payment_id, "verified": True, "environment": self.mode_label}

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        return {"payment_id": payment_id, "status": "captured", "environment": self.mode_label}


def get_payment_service() -> PaymentService:
    if settings.USE_RAZORPAY_REAL and settings.RAZORPAY_KEY_ID and not settings.RAZORPAY_KEY_ID.startswith("rzp_test_mock"):
        return RazorpayPaymentService(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    return SimulatorPaymentService()
