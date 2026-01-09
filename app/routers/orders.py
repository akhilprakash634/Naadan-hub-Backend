from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.firebase import db
from app.core.utils import gen_uuid, now_iso
from app.core.deps import get_current_user, require_roles, require_seller_approved

router = APIRouter()

def _make_order_number():
    # simple format: ORD-YYYY-<short>
    from datetime import datetime
    y = datetime.utcnow().year
    short = gen_uuid().split("-")[0].upper()
    return f"ORD-{y}-{short}"

@router.post("")
def create_order(payload: dict, user=Depends(get_current_user)):
    """
    Creates:
    - orders/{id}
    - order_items/{id} (multiple)
    - order_tracking/{id} initial
    - transactions/{id} optional (if online)
    """
    t = now_iso()
    oid = gen_uuid()
    order_number = _make_order_number()

    seller_id = payload.get("seller_id")
    if not seller_id:
        raise HTTPException(400, detail="seller_id required (single seller per order)")

    items = payload.get("items", [])
    if not items:
        raise HTTPException(400, detail="items required")

    order_doc = {
        "id": oid,
        "order_number": order_number,
        "user_id": user["uid"],
        "seller_id": seller_id,
        "status": payload.get("status", "pending"),
        "payment_status": payload.get("payment_status", "pending"),
        "payment_method": payload.get("payment_method", "cod"),
        "subtotal": payload.get("subtotal", 0),
        "delivery_fee": payload.get("delivery_fee", 0),
        "tax_amount": payload.get("tax_amount", 0),
        "discount_amount": payload.get("discount_amount", 0),
        "total_amount": payload.get("total_amount", 0),
        "delivery_address": payload.get("delivery_address", {}),
        "customer_phone": payload.get("customer_phone"),
        "customer_email": payload.get("customer_email") or user.get("email"),
        "notes": payload.get("notes"),
        "cancellation_reason": None,
        "estimated_delivery_date": payload.get("estimated_delivery_date"),
        "actual_delivery_date": None,
        "tracking_number": payload.get("tracking_number"),
        "courier_partner": payload.get("courier_partner"),
        "created_at": t,
        "updated_at": t
    }
    db().collection("orders").document(oid).set(order_doc)

    # order_items
    for it in items:
        item_id = gen_uuid()
        prod_id = it.get("product_id")
        if not prod_id:
            raise HTTPException(400, detail="Each item needs product_id")

        # Snapshot data
        prod_doc = db().collection("products").document(prod_id).get()
        pdata = prod_doc.to_dict() if prod_doc.exists else {}

        item_doc = {
            "id": item_id,
            "order_id": oid,
            "product_id": prod_id,
            "product_variant_id": it.get("product_variant_id"),
            "product_name": it.get("product_name") or pdata.get("name"),
            "product_image": it.get("product_image") or (pdata.get("images") or [None])[0],
            "quantity": int(it.get("quantity", 1)),
            "unit_price": float(it.get("unit_price", pdata.get("price", 0))),
            "total_price": float(it.get("total_price", 0)),
            "created_at": t
        }
        db().collection("order_items").document(item_id).set(item_doc)

    # order_tracking initial
    track_id = gen_uuid()
    db().collection("order_tracking").document(track_id).set({
        "id": track_id,
        "order_id": oid,
        "status": order_doc["status"],
        "location": payload.get("tracking_location"),
        "description": "Order created",
        "updated_by": user["uid"],
        "created_at": t
    })

    # optional transaction create
    if order_doc["payment_method"] in ["online", "upi"]:
        txid = gen_uuid()
        db().collection("transactions").document(txid).set({
            "id": txid,
            "order_id": oid,
            "user_id": user["uid"],
            "transaction_id": payload.get("transaction_id"),
            "payment_method": order_doc["payment_method"],
            "amount": order_doc["total_amount"],
            "status": "pending",
            "gateway_response": payload.get("gateway_response", {}),
            "created_at": t,
            "updated_at": t
        })

    return {"message": "Order created", "id": oid, "order_number": order_number}

@router.get("/user/{userId}")
def get_user_orders(userId: str, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")
    docs = db().collection("orders").where("user_id", "==", userId).stream()
    return {"items": [d.to_dict() for d in docs]}

@router.get("/seller/{sellerId}")
def get_seller_orders(sellerId: str, user=Depends(require_seller_approved)):
    if user["role"] == "seller" and user["uid"] != sellerId:
        raise HTTPException(403, detail="Forbidden")
    docs = db().collection("orders").where("seller_id", "==", sellerId).stream()
    return {"items": [d.to_dict() for d in docs]}

@router.get("")
def get_all_orders(user=Depends(require_roles("admin"))):
    docs = db().collection("orders").stream()
    return {"items": [d.to_dict() for d in docs]}

@router.patch("/{id}/status")
def update_order_status(id: str, payload: dict, user=Depends(require_seller_approved)):
    odoc = db().collection("orders").document(id).get()
    if not odoc.exists:
        raise HTTPException(404, detail="Order not found")
    o = odoc.to_dict() or {}

    # seller can update only their orders
    if user["role"] == "seller" and o.get("seller_id") != user["uid"]:
        raise HTTPException(403, detail="Forbidden")

    status_ = payload.get("status")
    if not status_:
        raise HTTPException(400, detail="status required")

    t = now_iso()
    db().collection("orders").document(id).set({"status": status_, "updated_at": t}, merge=True)

    # track history row
    tid = gen_uuid()
    db().collection("order_tracking").document(tid).set({
        "id": tid,
        "order_id": id,
        "status": status_,
        "location": payload.get("location"),
        "description": payload.get("description"),
        "updated_by": user["uid"],
        "created_at": t
    })
    return {"message": "Order status updated", "status": status_}

@router.get("/track")
def track_order(orderId: str = Query(...), phone: str = Query(...)):
    odoc = db().collection("orders").document(orderId).get()
    if not odoc.exists:
        raise HTTPException(404, detail="Order not found")
    o = odoc.to_dict() or {}

    if str(o.get("customer_phone")) != str(phone):
        raise HTTPException(403, detail="Phone mismatch")

    # return current order + tracking history
    tracks = db().collection("order_tracking").where("order_id", "==", orderId).stream()
    history = [t.to_dict() for t in tracks]
    return {"order": o, "tracking": history}

@router.get("/{id}")
def get_order_details(id: str, user=Depends(get_current_user)):
    odoc = db().collection("orders").document(id).get()
    if not odoc.exists:
        raise HTTPException(404, detail="Order not found")
    o = odoc.to_dict() or {}

    # owner checks
    if user["role"] != "admin" and user["uid"] not in [o.get("user_id"), o.get("seller_id")]:
        raise HTTPException(403, detail="Forbidden")

    items = db().collection("order_items").where("order_id", "==", id).stream()
    item_list = [d.to_dict() for d in items]
    tracks = db().collection("order_tracking").where("order_id", "==", id).stream()
    history = [d.to_dict() for d in tracks]

    return {"order": o, "items": item_list, "tracking": history}
