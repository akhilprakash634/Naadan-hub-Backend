from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from app.core.utils import gen_uuid, now_iso
from app.core.deps import require_roles

router = APIRouter()

@router.get("/{section}")
def get_site_content_section(section: str):
    # section is unique field; we store doc id = section for easier access
    doc = db().collection("site_content").document(section).get()
    if not doc.exists:
        return {"id": None, "section": section, "content": {}}
    return doc.to_dict()

@router.put("/{section}")
def update_site_content_section(section: str, payload: dict, user=Depends(require_roles("admin"))):
    t = now_iso()
    doc = {
        "id": payload.get("id") or section,
        "section": section,
        "content": payload.get("content", payload),
        "updated_at": t,
        "created_at": payload.get("created_at") or t
    }
    db().collection("site_content").document(section).set(doc, merge=True)
    return {"message": "Site content updated", "section": section}

@router.get("")
def get_all_site_content():
    docs = db().collection("site_content").stream()
    return {"items": [d.to_dict() for d in docs]}
