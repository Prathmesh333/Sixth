"""Explicit fixture calendar/catalog and transactionally executed sandbox store."""

import hashlib
import json

from .models import now
from .storage import Store

RECIPES = [
    {
        "id": "lemon-orzo",
        "name": "Roasted tomato & lemon orzo",
        "description": "Slow-roasted tomatoes, fresh basil and a little parmesan.",
        "minutes": 30,
        "vegetarian": True,
        "dairy_free": False,
        "servings": 4,
        "ingredients": [
            {"id": "orzo", "name": "Orzo", "quantity": 320, "unit": "g", "price_per_unit": 0.35},
            {
                "id": "tomatoes",
                "name": "Cherry tomatoes",
                "quantity": 400,
                "unit": "g",
                "price_per_unit": 0.25,
            },
            {"id": "parmesan", "name": "Parmesan", "quantity": 60, "unit": "g", "price_per_unit": 1.2},
        ],
    },
    {
        "id": "chickpea-rice",
        "name": "Golden chickpea & rice bowls",
        "description": "Crisp chickpeas, fragrant rice and a lemon-tahini dressing.",
        "minutes": 35,
        "vegetarian": True,
        "dairy_free": True,
        "servings": 4,
        "ingredients": [
            {"id": "rice", "name": "Basmati rice", "quantity": 300, "unit": "g", "price_per_unit": 0.18},
            {"id": "chickpeas", "name": "Chickpeas", "quantity": 400, "unit": "g", "price_per_unit": 0.2},
            {
                "id": "tomatoes",
                "name": "Cherry tomatoes",
                "quantity": 200,
                "unit": "g",
                "price_per_unit": 0.25,
            },
        ],
    },
]


def calendar():
    return [
        {
            "id": "calendar-dinner",
            "title": "Dinner at home",
            "starts_at": "2026-10-17T19:00:00+05:30",
            "ends_at": "2026-10-17T21:00:00+05:30",
            "mode": "fixture",
            "source_id": "fixture-calendar",
        },
        {
            "id": "calendar-coffee",
            "title": "Coffee with Sam",
            "starts_at": "2026-10-17T11:00:00+05:30",
            "ends_at": "2026-10-17T11:45:00+05:30",
            "mode": "fixture",
            "source_id": "fixture-calendar",
        },
    ]


def build_menu(facts: list[dict], guests: int, subject: str, owner: str):
    relevant = [f for f in facts if f["subject"].casefold() in {subject.casefold(), owner.casefold(), "me"}]
    dietary = [f for f in relevant if f["predicate"] in {"diet", "avoids", "allergy"}]
    supported = {"vegetarian", "vegan", "dairy", "dairy-free", "dairy free"}
    unknown = [f for f in dietary if f["value"].casefold() not in supported]
    if unknown:
        return (
            None,
            [],
            relevant,
            "The local recipe catalog cannot verify this restriction: "
            + ", ".join(f["value"] for f in unknown),
        )
    dairy_free = any(f["value"].casefold() in {"vegan", "dairy", "dairy-free", "dairy free"} for f in dietary)
    recipe = RECIPES[1 if dairy_free else 0]
    items = []
    for ingredient in recipe["ingredients"]:
        required = round(ingredient["quantity"] * guests / recipe["servings"], 2)
        stock = 200 if ingredient["id"] == "rice" else 0
        quantity = max(0, required - stock)
        items.append(
            {
                **ingredient,
                "required": required,
                "pantry": stock,
                "quantity": quantity,
                "amount_minor": round(quantity * ingredient["price_per_unit"]),
            }
        )
    return recipe, items, relevant, ""


def fingerprint(owner: str, plan_id: str, revision: int, items: list[dict], evidence: list[str]):
    payload = {
        "owner": owner,
        "plan_id": plan_id,
        "revision": revision,
        "items": items,
        "evidence": sorted(evidence),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def execute_cart(store: Store, owner: str, action: dict):
    """Local provider mutation and ledger commit share one SQLite transaction.

    A real merchant adapter needs provider idempotency and reconciliation instead.
    """
    with store.transaction() as db:
        existing = db.execute(
            "SELECT data FROM action_ledger WHERE owner=? AND fingerprint=?", (owner, action["fingerprint"])
        ).fetchone()
        if existing:
            return json.loads(existing[0])
        cart = {
            "id": "cart-" + action["plan_id"],
            "plan_id": action["plan_id"],
            "revision": action["plan_revision"],
            "items": action["arguments"]["items"],
            "currency": "INR",
            "mode": "sandbox",
            "simulation": True,
            "updated_at": now(),
        }
        store.put_tx(db, owner, "cart", cart)
        observed = db.execute(
            "SELECT data FROM records WHERE owner=? AND kind='cart' AND id=?", (owner, cart["id"])
        ).fetchone()
        verified = json.loads(observed[0])
        if verified["items"] != action["arguments"]["items"]:
            raise RuntimeError("Cart contents failed verification")
        result = {
            "id": action["action_id"],
            "status": "succeeded",
            "mode": "sandbox",
            "simulation": True,
            "data": verified,
            "verified_at": now(),
            "retryable": False,
            "evidence": [{"source_id": cart["id"], "captured_at": now()}],
        }
        db.execute(
            "INSERT INTO action_ledger VALUES (?,?,?,?)",
            (owner, action["action_id"], action["fingerprint"], json.dumps(result)),
        )
        store.put_tx(db, owner, "outbox", {"id": action["action_id"], "status": "pending", "result": result})
        return result
