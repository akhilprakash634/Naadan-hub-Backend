from fastapi import Depends, Header, HTTPException, status
from firebase_admin import auth
from .firebase import db

def get_current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.replace("Bearer ", "").strip()
    try:
        decoded = auth.verify_id_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid/expired token")

    uid = decoded["uid"]
    udoc = db().collection("users").document(uid).get()
    role = "user"
    status_ = "active"
    if udoc.exists:
        data = udoc.to_dict() or {}
        role = data.get("role", "user")
        status_ = data.get("status", "active")

    return {"uid": uid, "email": decoded.get("email"), "role": role, "status": status_}

def require_roles(*roles: str):
    def _dep(user=Depends(get_current_user)):
        if user.get("status") != "active":
            raise HTTPException(status_code=403, detail=f"Account status: {user.get('status')}")
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _dep

def require_seller_approved(user=Depends(require_roles("seller", "admin"))):
    # Admin bypass
    if user["role"] == "admin":
        return user
    sdoc = db().collection("seller_profiles").document(user["uid"]).get()
    if not sdoc.exists:
        raise HTTPException(403, detail="Seller profile missing")
    sdata = sdoc.to_dict() or {}
    if sdata.get("approval_status") != "approved":
        raise HTTPException(403, detail=f"Seller not approved: {sdata.get('approval_status')}")
    return user
