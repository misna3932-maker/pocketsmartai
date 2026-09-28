from typing import Any
from .platforms import links_for

HOME_CATALOG = {
    "lighting": [
        ("LED Bulb (Warm White)", "Energy-efficient LED bulbs for warm general lighting."),
        ("Ceiling Light", "Simple flush-mount light for living rooms and kitchens."),
    ],
    "ceiling_fans": [("Havells Ceiling Fan", "Basic, functional ceiling fan with efficient air delivery.")],
    "furniture": [
        ("Plastic Chair", "Stackable plastic chairs for kitchen or living room."),
        ("Small Wooden Table", "Simple wooden table for dining or side-table use."),
        ("Compact Storage Unit", "Space-saving storage for everyday essentials."),
    ],
    "dining_tables": [("4-Seater Dining Table", "Compact dining table for everyday meals.")],
}
PARTY_CATALOG = {
    "venue": [("Home", "Use the home as the event venue to minimize fixed venue costs.")],
    "catering": [("Home-cooked meal", "Simple home-cooked meal plan for small gatherings.")],
    "decoration": [("DIY decoration kit", "Balloons, lights and reusable decor accents."), ("Table decor bundle", "Simple table and backdrop styling kit.")],
    "entertainment": [("Streaming service subscription", "On-demand music/video for casual parties."), ("Board games/cards", "Purchase or reuse a board game or card game."), ("Music playlist", "Create a celebratory playlist on a music service.")],
    "contingency": [("Contingency fund", "Buffer for unexpected event expenses.")],
}
JEWELRY_CATALOG = [
    ("bracelet", "A simple, clean bracelet with light metal accents.", "casual"),
    ("ring", "A silver or dark-grey minimal ring for a restrained look.", "minimalist"),
    ("watch", "A classic watch with a leather or metal band.", "classic"),
]

def money(v: float) -> str:
    return f"₹{v:,.2f}"

def _item(name, desc, price, quantity, platforms, query):
    return {
        "name": name,
        "description": desc,
        "price": round(price, 2),
        "price_display": money(price),
        "quantity": quantity,
        "shopping_links": links_for(query, platforms),
    }

def home_fallback(data: dict[str, Any]) -> dict:
    budget = float(data["total_budget"])
    allocations = {
        "lighting": budget * 0.30,
        "ceiling_fans": budget * 0.20,
        "furniture": budget * 0.35,
        "dining_tables": budget * 0.15,
    }
    requested = {
        "lighting": int(data.get("lights", 0)),
        "ceiling_fans": int(data.get("ceiling_fans", 0)),
        "furniture": int(data.get("furniture", 0)),
        "dining_tables": int(data.get("dining_tables", 0)),
    }
    # Keep the visual shape from the reference; use real platform links for supported names.
    platforms = ["Amazon", "Flipkart", "Ikea", "Myntra", "Google"]
    categories = []
    for key, amount in allocations.items():
        qty = requested[key]
        if qty == 0:
            continue
        candidates = HOME_CATALOG[key]
        each = max(amount / max(qty, 1), 1)
        items = []
        for idx, (name, desc) in enumerate(candidates[:2]):
            units = 1 if qty == 1 else (qty if idx == 0 else 0)
            if units <= 0: continue
            price = round(each, 2)
            items.append(_item(name, desc, price, units, platforms, name))
        categories.append({
            "category": key.replace("_", " ").title(),
            "allocation": round(amount, 2),
            "items": items,
        })
    allocated = sum(c["allocation"] for c in categories)
    return {
        "title": "Your Personalized Budget Plan",
        "planner_type": "Home Interior Budget",
        "total_budget": budget,
        "total_budget_display": money(budget),
        "allocated": round(allocated, 2),
        "allocated_display": money(allocated),
        "remaining": round(budget - allocated, 2),
        "remaining_display": money(max(budget - allocated, 0)),
        "budget_breakdown": categories,
        "additional_suggestions": [
            "Consider purchasing used furniture for further cost savings.",
            "Look for sales and discounts on online marketplaces.",
            "Prioritize essential items and postpone non-essential purchases.",
        ],
        "ai_used": False,
    }

def party_fallback(data: dict[str, Any]) -> dict:
    budget = float(data["total_budget"])
    needs = set(data.get("needs", []))
    weights = {"venue": 0.20, "catering": 0.40, "decoration": 0.15, "entertainment": 0.25}
    cats = []
    for key, weight in weights.items():
        if key not in needs and needs:
            continue
        alloc = budget * weight
        catalog = PARTY_CATALOG[key]
        name, desc = catalog[0]
        qty = 1
        price = alloc
        cats.append({
            "category": key.title(),
            "allocation": round(alloc, 2),
            "items": [_item(name, desc, price, qty, ["Google", "Swiggy", "Zomato"] if key == "catering" else ["Amazon", "Flipkart", "BookMyShow"], name)],
        })
    # Always show contingency as the design does in party output.
    contingency = budget * 0.20 if "contingency" not in needs else budget * 0.20
    cats.append({
        "category": "Contingency",
        "allocation": round(contingency, 2),
        "items": [_item("Unexpected expenses", "Buffer for unforeseen costs.", contingency, 1, ["Amazon", "Google"], "party contingency")],
    })
    allocated = sum(c["allocation"] for c in cats)
    if allocated > budget:
        scale = budget / allocated
        for c in cats:
            c["allocation"] = round(c["allocation"] * scale, 2)
            for i in c["items"]:
                i["price"] = c["allocation"]
                i["price_display"] = money(c["allocation"])
        allocated = sum(c["allocation"] for c in cats)
    return {
        "title": "Your Party Budget Plan",
        "planner_type": "Party Planning Budget",
        "total_budget": budget,
        "total_budget_display": money(budget),
        "allocated": round(allocated, 2),
        "allocated_display": money(allocated),
        "remaining": round(budget - allocated, 2),
        "remaining_display": money(max(budget - allocated, 0)),
        "budget_breakdown": cats,
        "venue_suggestions": [{"name": "Home", "type": "Residential", "location": "User provided location", "website": links_for("Home event venue", ["Google"])[0]["url"]}],
        "additional_suggestions": [
            "Consider making the meal a potluck style if comfortable with guests to reduce catering costs.",
            "Look for discounts or offers on streaming services or board games.",
            "Homemade decorations can be a cost-effective alternative when a DIY setup works.",
        ],
        "ai_used": False,
    }

def jewelry_fallback(data: dict[str, Any]) -> dict:
    budget = float(data["total_budget"])
    picks = [
        (JEWELRY_CATALOG[0], budget * 0.16),
        (JEWELRY_CATALOG[1], budget * 0.23),
        (JEWELRY_CATALOG[2], budget * 0.55),
    ]
    items = []
    for (name, desc, style), price in picks:
        items.append({
            **_item(name, desc, price, 1, ["Amazon", "Flipkart", "Myntra", "Meesho"], f"{name} {data.get('occasion','')} {data.get('style_preferences','')} jewellery"),
            "style": style,
        })
    allocated = sum(i["price"] for i in items)
    return {
        "title": "Your Personalized Jewelry Recommendations",
        "planner_type": "Jewelry Budget",
        "total_budget": budget,
        "total_budget_display": money(budget),
        "allocated": round(allocated, 2),
        "allocated_display": money(allocated),
        "remaining": round(budget - allocated, 2),
        "remaining_display": money(max(budget - allocated, 0)),
        "outfit_analysis": {"colors": "blue, white", "style": data.get("style_preferences") or "casual", "formality": "informal"},
        "items": items,
        "styling_tips": [
            "Keep the jewelry minimal to match the overall outfit style.",
            "Consider whether a statement piece, choosing a design that reflects personal style.",
            "Ensure the metal tones of the ring and bracelet complement each other.",
        ],
        "ai_used": False,
        "outfit_image": data.get("outfit_image"),
    }
