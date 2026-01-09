from fastapi import APIRouter, Depends
from app.core.firebase import db
from app.core.utils import gen_uuid, now_iso
from app.core.deps import require_roles

router = APIRouter()

@router.get("/bsf")
def get_bsf_education_content():
    # return all active sections ordered by display_order (client sorts)
    docs = db().collection("bsf_education").where("is_active", "==", True).stream()
    items = [d.to_dict() for d in docs]
    items.sort(key=lambda x: int(x.get("display_order", 0)))
    return {"items": items}

@router.put("/bsf")
def update_bsf_education_content(payload: dict, user=Depends(require_roles("admin"))):
    """
    You can update one section by providing id, or create new if no id
    """
    t = now_iso()
    eid = payload.get("id") or gen_uuid()

    doc = {
        "id": eid,
        "section": payload.get("section"),
        "title": payload.get("title"),
        "content": payload.get("content"),
        "images": payload.get("images", []),
        "video_url": payload.get("video_url"),
        "display_order": int(payload.get("display_order", 0)),
        "is_active": bool(payload.get("is_active", True)),
        "created_at": payload.get("created_at") or t,
        "updated_at": t
    }
    db().collection("bsf_education").document(eid).set(doc, merge=True)
    return {"message": "BSF education updated", "id": eid}
