import base64, json, mimetypes
import requests
from ..config import settings

class GeminiService:
    def __init__(self):
        self.enabled = bool(settings.gemini_api_key)

    def _call(self, prompt: str, image_path: str | None = None) -> str:
        if not self.enabled:
            raise RuntimeError("Gemini API key not configured")
        parts = [{"text": prompt}]
        if image_path:
            with open(image_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
            parts.append({"inline_data": {"mime_type": mime, "data": data}})
        body = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.35}}
        url = settings.gemini_api_url.format(model=settings.gemini_model)
        resp = requests.post(url, params={"key": settings.gemini_api_key}, json=body, timeout=45)
        resp.raise_for_status()
        payload = resp.json()
        return payload["candidates"][0]["content"]["parts"][0]["text"]

    def _json(self, text: str):
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)

    def generate(self, planner: str, data: dict, image_path: str | None = None):
        if not self.enabled:
            return None
        if planner == "home":
            prompt = f"""You are PocketSmart AI. Return ONLY valid JSON. Build a budget-aware home interior recommendation. Budget: {data['total_budget']}. Lights: {data.get('lights',0)}. Ceiling fans: {data.get('ceiling_fans',0)}. Furniture pieces: {data.get('furniture',0)}. Dining tables: {data.get('dining_tables',0)}. Rooms: {data.get('rooms',[])}. Notes: {data.get('notes','')}. JSON keys must be title,total_budget,allocated,remaining,budget_breakdown (list with category,allocation,items; each item has name,description,price,quantity),additional_suggestions. Keep allocated <= total_budget."""
        elif planner == "party":
            prompt = f"""You are PocketSmart AI. Return ONLY valid JSON. Plan a party budget. Budget: {data['total_budget']}. Guests: {data['guests']}. Party type: {data.get('party_type')}. Venue type: {data.get('venue_type')}. Needs: {data.get('needs')}. Notes: {data.get('notes','')}. JSON keys: title,total_budget,allocated,remaining,budget_breakdown (list with category,allocation,items; each item name,description,price,quantity),venue_suggestions,additional_suggestions. Keep allocated <= total_budget."""
        elif planner == "jewelry":
            prompt = f"""You are PocketSmart AI. Return ONLY valid JSON. Recommend jewelry for an occasion. Budget: {data['total_budget']}. Occasion: {data.get('occasion')}. Style preferences: {data.get('style_preferences')}. JSON keys: title,total_budget,allocated,remaining,outfit_analysis (colors,style,formality),items (list with name,description,price,style,shopping_query),styling_tips. Keep allocated <= total_budget."""
        else:
            raise ValueError(f"Unsupported planner: {planner}")
        try:
            parsed = self._json(self._call(prompt, image_path=image_path))
            if not isinstance(parsed, dict):
                raise ValueError("Gemini returned a non-object JSON response")
            parsed["total_budget"] = float(parsed.get("total_budget", data["total_budget"]))
            parsed["allocated"] = float(parsed.get("allocated", 0))
            parsed["remaining"] = max(float(parsed.get("remaining", parsed["total_budget"] - parsed["allocated"])), 0)
            if parsed["allocated"] > parsed["total_budget"]:
                parsed["allocated"] = parsed["total_budget"]
                parsed["remaining"] = 0
            parsed["total_budget_display"] = money_local(parsed["total_budget"])
            parsed["allocated_display"] = money_local(parsed["allocated"])
            parsed["remaining_display"] = money_local(parsed["remaining"])
            # Add links locally so JSON from the model never controls destination URLs.
            if planner == "jewelry":
                parsed.setdefault("outfit_analysis", {"colors": "not analyzed", "style": data.get("style_preferences") or "not specified", "formality": "not specified"})
                parsed.setdefault("items", [])
                for item in parsed["items"]:
                    q = item.get("shopping_query") or item.get("name") or "jewelry"
                    item["shopping_links"] = links_for_local(q)
                    item["price"] = float(item.get("price", 0))
                    item["price_display"] = money_local(item["price"])
                parsed.setdefault("styling_tips", [])
                if image_path:
                    parsed["outfit_image"] = data.get("outfit_image")
            else:
                parsed.setdefault("budget_breakdown", [])
                for category in parsed["budget_breakdown"]:
                    category.setdefault("items", [])
                    category["allocation"] = float(category.get("allocation", 0))
                    for item in category["items"]:
                        item["price"] = float(item.get("price", 0))
                        item["price_display"] = money_local(item["price"])
                        item["shopping_links"] = links_for_local(item.get("name", ""))
                parsed.setdefault("additional_suggestions", [])
            parsed["ai_used"] = True
            return parsed
        except Exception:
            return None

def links_for_local(query):
    from .platforms import links_for
    return links_for(query, ["Amazon", "Flipkart", "Ikea", "Myntra", "Google"])

def money_local(value):
    return f"₹{float(value):,.2f}"

gemini_service = GeminiService()
