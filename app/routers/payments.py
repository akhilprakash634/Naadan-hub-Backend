from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from app.core.utils import gen_uuid, now_iso
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/{userId}")
def get_payment_methods(userId: str, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")
    docs = db().collection("payment_methods").where("user_id", "==", userId).stream()
    return {"items": [d.to_dict() for d in docs]}

@router.post("/{userId}")
def add_payment_method(userId: str, payload: dict, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    t = now_iso()
    pid = gen_uuid()

    doc = {
        "id": pid,
        "user_id": userId,
        "payment_type": payload.get("payment_type"),  # card/upi/netbanking
        "card_last_four": payload.get("card_last_four"),
        "card_brand": payload.get("card_brand"),
        "upi_id": payload.get("upi_id"),
        "is_default": bool(payload.get("is_default", False)),
        "created_at": t,
        "updated_at": t
    }
    if not doc["payment_type"]:
        raise HTTPException(400, detail="payment_type required")

    # if default => unset others
    if doc["is_default"]:
        others = db().collection("payment_methods").where("user_id", "==", userId).where("is_default", "==", True).stream()
        for o in others:
            db().collection("payment_methods").document(o.id).set({"is_default": False, "updated_at": t}, merge=True)

    db().collection("payment_methods").document(pid).set(doc)
    return {"message": "Payment method added", "id": pid}

@router.delete("/{userId}/{methodId}")
def delete_payment_method(userId: str, methodId: str, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    doc = db().collection("payment_methods").document(methodId).get()
    if doc.exists and (doc.to_dict() or {}).get("user_id") != userId:
        raise HTTPException(403, detail="Forbidden")

    db().collection("payment_methods").document(methodId).delete()
    return {"message": "Payment method deleted"}
