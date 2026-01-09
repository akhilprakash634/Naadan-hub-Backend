from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from app.core.utils import gen_uuid, now_iso
from app.core.deps import require_roles

router = APIRouter()

def _ensure_unique_slug(slug: str, exclude_id: str | None = None):
    q = db().collection("blogs").where("slug", "==", slug).limit(1).stream()
    for d in q:
        if exclude_id and d.id == exclude_id:
            continue
        raise HTTPException(409, detail="slug must be unique")

@router.get("")
def get_all_blogs():
    # public: published only
    docs = db().collection("blogs").where("status", "==", "published").stream()
    return {"items": [d.to_dict() for d in docs]}

@router.get("/{id}")
def get_blog_by_id(id: str):
    doc = db().collection("blogs").document(id).get()
    if not doc.exists:
        raise HTTPException(404, detail="Blog not found")
    return doc.to_dict()

@router.post("")
def create_blog(payload: dict, user=Depends(require_roles("admin"))):
    t = now_iso()
    bid = gen_uuid()
    slug = payload.get("slug")
    if slug:
        _ensure_unique_slug(slug)

    doc = {
        "id": bid,
        "author_id": user["uid"],
        "title": payload.get("title"),
        "slug": slug,
        "excerpt": payload.get("excerpt"),
        "content": payload.get("content"),
        "featured_image": payload.get("featured_image"),
        "category": payload.get("category"),
        "tags": payload.get("tags", []),
        "status": payload.get("status", "draft"),
        "view_count": payload.get("view_count", 0),
        "seo_title": payload.get("seo_title"),
        "seo_description": payload.get("seo_description"),
        "seo_keywords": payload.get("seo_keywords"),
        "published_at": payload.get("published_at"),
        "created_at": t,
        "updated_at": t
    }
    db().collection("blogs").document(bid).set(doc)
    return {"message": "Blog created", "id": bid}

@router.put("/{id}")
def update_blog(id: str, payload: dict, user=Depends(require_roles("admin"))):
    if payload.get("slug"):
        _ensure_unique_slug(payload["slug"], exclude_id=id)
    payload["updated_at"] = now_iso()
    db().collection("blogs").document(id).set(payload, merge=True)
    return {"message": "Blog updated"}

@router.delete("/{id}")
def delete_blog(id: str, user=Depends(require_roles("admin"))):
    db().collection("blogs").document(id).delete()
    return {"message": "Blog deleted"}

@router.patch("/{id}/status")
def toggle_blog_status(id: str, payload: dict, user=Depends(require_roles("admin"))):
    status_ = payload.get("status")
    if not status_:
        raise HTTPException(400, detail="status required")
    db().collection("blogs").document(id).set({"status": status_, "updated_at": now_iso()}, merge=True)
    return {"message": "Blog status updated", "status": status_}
