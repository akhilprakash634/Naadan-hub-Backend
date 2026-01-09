from fastapi import APIRouter, Depends, HTTPException
import httpx
from firebase_admin import auth

from app.core.config import settings
from app.core.firebase import db
from app.core.utils import now_iso
from app.core.deps import get_current_user

router = APIRouter()

async def firebase_password_login(email: str, password: str):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, json=payload)
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return r.json()

@router.post("/register")
def user_register(payload: dict):
    # Required: email, password, full_name (phone optional)
    email = payload.get("email")
    password = payload.get("password")
    full_name = payload.get("full_name")
    phone = payload.get("phone")

    if not email or not password or not full_name:
        raise HTTPException(400, detail="email, password, full_name are required")

    user = auth.create_user(email=email, password=password, display_name=full_name)
    uid = user.uid
    t = now_iso()

    db().collection("users").document(uid).set({
        "id": uid,
        "email": email,
        "password_hash": None,
        "full_name": full_name,
        "phone": phone,
        "role": "user",
        "google_id": None,
        "email_verified": False,
        "status": "active",
        "created_at": t,
        "updated_at": t
    })

    db().collection("user_profiles").document(uid).set({
        "id": uid,
        "user_id": uid,
        "avatar_url": None,
        "date_of_birth": None,
        "gender": None,
        "bio": None,
        "preferences": {},
        "created_at": t,
        "updated_at": t
    })

    return {"message": "User registered", "id": uid}

@router.post("/login")
async def user_login(payload: dict):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(400, detail="email and password required")
    return await firebase_password_login(email, password)

@router.post("/admin/login")
async def admin_login(payload: dict):
    res = await user_login(payload)
    uid = res.get("localId")
    udoc = db().collection("users").document(uid).get()
    if not udoc.exists:
        raise HTTPException(403, detail="Not an admin")
    u = udoc.to_dict() or {}
    if u.get("role") != "admin":
        raise HTTPException(403, detail="Not an admin")

    # optional: ensure admin_users exists
    adoc = db().collection("admin_users").document(uid).get()
    if not adoc.exists:
        db().collection("admin_users").document(uid).set({
            "id": uid,
            "user_id": uid,
            "permissions": [],
            "last_login": now_iso(),
            "created_at": now_iso(),
            "updated_at": now_iso()
        }, merge=True)
    else:
        db().collection("admin_users").document(uid).set({"last_login": now_iso(), "updated_at": now_iso()}, merge=True)

    return res

@router.post("/seller/register")
def seller_register(payload: dict):
    # Required: email, password, full_name, farm_name (others optional)
    email = payload.get("email")
    password = payload.get("password")
    full_name = payload.get("full_name")
    phone = payload.get("phone")
    farm_name = payload.get("farm_name")

    if not email or not password or not full_name or not farm_name:
        raise HTTPException(400, detail="email, password, full_name, farm_name required")

    user = auth.create_user(email=email, password=password, display_name=full_name)
    uid = user.uid
    t = now_iso()

    db().collection("users").document(uid).set({
        "id": uid,
        "email": email,
        "password_hash": None,
        "full_name": full_name,
        "phone": phone,
        "role": "seller",
        "google_id": None,
        "email_verified": False,
        "status": "active",
        "created_at": t,
        "updated_at": t
    })

    db().collection("seller_profiles").document(uid).set({
        "id": uid,
        "user_id": uid,
        "farm_name": farm_name,
        "farm_description": payload.get("farm_description"),
        "farm_location": payload.get("farm_location"),
        "farm_address": payload.get("farm_address"),
        "farm_size": payload.get("farm_size"),
        "certification_type": payload.get("certification_type"),
        "certification_number": payload.get("certification_number"),
        "certification_document_url": payload.get("certification_document_url"),
        "bank_account_name": payload.get("bank_account_name"),
        "bank_account_number": payload.get("bank_account_number"),
        "bank_name": payload.get("bank_name"),
        "ifsc_code": payload.get("ifsc_code"),
        "gst_number": payload.get("gst_number"),
        "pan_number": payload.get("pan_number"),
        "approval_status": "pending",
        "rejection_reason": None,
        "rating": 0,
        "total_sales": 0,
        "total_orders": 0,
        "is_verified": False,
        "created_at": t,
        "updated_at": t
    })

    return {"message": "Seller registered (pending approval)", "id": uid}

@router.post("/seller/login")
async def seller_login(payload: dict):
    res = await user_login(payload)
    uid = res.get("localId")
    udoc = db().collection("users").document(uid).get()
    if not udoc.exists:
        raise HTTPException(403, detail="Not a seller")
    u = udoc.to_dict() or {}
    if u.get("role") != "seller":
        raise HTTPException(403, detail="Not a seller")

    sdoc = db().collection("seller_profiles").document(uid).get()
    if not sdoc.exists:
        raise HTTPException(403, detail="Seller profile missing")
    s = sdoc.to_dict() or {}
    if s.get("approval_status") != "approved":
        raise HTTPException(403, detail=f"Seller not approved: {s.get('approval_status')}")
    return res

@router.post("/google")
def google_oauth(payload: dict):
    # payload: { idToken: "<firebase-id-token>" } (client already did Google sign-in)
    id_token = payload.get("idToken")
    if not id_token:
        raise HTTPException(400, detail="idToken required")
    decoded = auth.verify_id_token(id_token)
    uid = decoded["uid"]
    t = now_iso()

    uref = db().collection("users").document(uid)
    if not uref.get().exists:
        uref.set({
            "id": uid,
            "email": decoded.get("email"),
            "password_hash": None,
            "full_name": decoded.get("name") or (decoded.get("email") or "").split("@")[0],
            "phone": None,
            "role": "user",
            "google_id": decoded.get("sub"),
            "email_verified": bool(decoded.get("email_verified", True)),
            "status": "active",
            "created_at": t,
            "updated_at": t
        })
        db().collection("user_profiles").document(uid).set({
            "id": uid,
            "user_id": uid,
            "avatar_url": decoded.get("picture"),
            "date_of_birth": None,
            "gender": None,
            "bio": None,
            "preferences": {},
            "created_at": t,
            "updated_at": t
        })
    else:
        uref.set({"updated_at": t}, merge=True)

    return {"message": "Google OAuth success", "id": uid}

@router.post("/logout")
def logout(user=Depends(get_current_user)):
    # revoke refresh tokens (client should also signOut)
    auth.revoke_refresh_tokens(user["uid"])
    return {"message": "Logged out (tokens revoked)"}

@router.get("/me")
def me(user=Depends(get_current_user)):
    return user
