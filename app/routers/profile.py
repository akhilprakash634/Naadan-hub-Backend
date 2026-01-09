from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from app.core.utils import gen_uuid, now_iso
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/{userId}")
def get_profile(userId: str, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    u = db().collection("users").document(userId).get()
    p = db().collection("user_profiles").document(userId).get()

    if not u.exists:
        raise HTTPException(404, detail="User not found")

    return {
        "user": u.to_dict(),
        "profile": p.to_dict() if p.exists else None
    }

@router.put("/{userId}")
def update_profile(userId: str, payload: dict, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    t = now_iso()
    # update users (safe fields)
    if any(k in payload for k in ["full_name", "phone", "status"]):
        db().collection("users").document(userId).set({
            **{k: payload[k] for k in ["full_name","phone","status"] if k in payload},
            "updated_at": t
        }, merge=True)

    # update user_profiles
    prof_fields = ["avatar_url","date_of_birth","gender","bio","preferences"]
    prof_update = {k: payload[k] for k in prof_fields if k in payload}
    if prof_update:
        prof_update["updated_at"] = t
        db().collection("user_profiles").document(userId).set(prof_update, merge=True)

    return {"message": "Profile updated"}

@router.get("/{userId}/addresses")
def get_addresses(userId: str, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    docs = db().collection("delivery_addresses").where("user_id", "==", userId).stream()
    return {"items": [d.to_dict() for d in docs]}

@router.post("/{userId}/addresses")
def add_or_update_address(userId: str, payload: dict, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    t = now_iso()
    addr_id = payload.get("id") or payload.get("address_id") or gen_uuid()

    doc = {
        "id": addr_id,
        "user_id": userId,
        "address_type": payload.get("address_type", "home"),
        "full_name": payload.get("full_name"),
        "phone": payload.get("phone"),
        "address_line1": payload.get("address_line1"),
        "address_line2": payload.get("address_line2"),
        "city": payload.get("city"),
        "state": payload.get("state"),
        "pincode": payload.get("pincode"),
        "landmark": payload.get("landmark"),
        "is_default": bool(payload.get("is_default", False)),
        "updated_at": t,
        "created_at": payload.get("created_at") or t
    }

    # if is_default true -> unset other defaults
    if doc["is_default"]:
        others = db().collection("delivery_addresses").where("user_id", "==", userId).where("is_default", "==", True).stream()
        for o in others:
            if o.id != addr_id:
                db().collection("delivery_addresses").document(o.id).set({"is_default": False, "updated_at": t}, merge=True)

    db().collection("delivery_addresses").document(addr_id).set(doc, merge=True)
    return {"message": "Address saved", "id": addr_id}

@router.delete("/{userId}/addresses/{addressId}")
def delete_address(userId: str, addressId: str, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    db().collection("delivery_addresses").document(addressId).delete()
    return {"message": "Address deleted"}
