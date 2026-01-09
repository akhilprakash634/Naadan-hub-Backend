from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from app.core.utils import now_iso
from app.core.deps import require_roles

router = APIRouter()

@router.get("/sellers")
def get_all_sellers(user=Depends(require_roles("admin"))):
    docs = db().collection("seller_profiles").stream()
    return {"items": [d.to_dict() for d in docs]}

@router.patch("/sellers/{id}/approve")
def approve_seller(id: str, user=Depends(require_roles("admin"))):
    t = now_iso()
    sdoc = db().collection("seller_profiles").document(id).get()
    if not sdoc.exists:
        raise HTTPException(404, detail="Seller profile not found")

    db().collection("seller_profiles").document(id).set({
        "approval_status": "approved",
        "rejection_reason": None,
        "is_verified": True,
        "updated_at": t
    }, merge=True)

    # ensure users role seller + active
    db().collection("users").document(id).set({
        "role": "seller",
        "status": "active",
        "updated_at": t
    }, merge=True)

    return {"message": "Seller approved"}

@router.patch("/sellers/{id}/reject")
def reject_seller(id: str, payload: dict, user=Depends(require_roles("admin"))):
    t = now_iso()
    reason = payload.get("rejection_reason") or payload.get("reason")

    db().collection("seller_profiles").document(id).set({
        "approval_status": "rejected",
        "rejection_reason": reason,
        "updated_at": t
    }, merge=True)

    return {"message": "Seller rejected"}

@router.patch("/sellers/{id}/status")
def update_seller_status(id: str, payload: dict, user=Depends(require_roles("admin"))):
    t = now_iso()
    status_ = payload.get("status")
    if not status_:
        raise HTTPException(400, detail="status required")

    # status in users table
    db().collection("users").document(id).set({"status": status_, "updated_at": t}, merge=True)
    return {"message": "Seller user status updated", "status": status_}

@router.get("/stats")
def admin_dashboard_stats(user=Depends(require_roles("admin"))):
    # simple counts (for big scale use aggregation)
    return {
        "users": len(list(db().collection("users").stream())),
        "user_profiles": len(list(db().collection("user_profiles").stream())),
        "sellers": len(list(db().collection("seller_profiles").stream())),
        "products": len(list(db().collection("products").stream())),
        "orders": len(list(db().collection("orders").stream())),
        "blogs": len(list(db().collection("blogs").stream())),
        "reviews": len(list(db().collection("reviews").stream())),
    }
