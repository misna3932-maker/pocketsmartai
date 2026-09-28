from urllib.parse import quote_plus

PLATFORMS = {
    "Amazon": "https://www.amazon.in/s?k={q}",
    "Flipkart": "https://www.flipkart.com/search?q={q}",
    "Ikea": "https://www.ikea.com/in/en/search/?q={q}",
    "Myntra": "https://www.myntra.com/{q}",
    "Meesho": "https://www.meesho.com/search?q={q}",
    "Swiggy": "https://www.swiggy.com/search?query={q}",
    "Zomato": "https://www.zomato.com/search?city=India&query={q}",
    "OYO": "https://www.oyorooms.com/search?location={q}",
    "Google": "https://www.google.com/search?q={q}",
    "BookMyShow": "https://in.bookmyshow.com/search/?q={q}",
}

def search_link(platform: str, query: str) -> str:
    template = PLATFORMS.get(platform, PLATFORMS["Google"])
    return template.format(q=quote_plus(query))

def links_for(query: str, platforms: list[str]):
    return [{"name": p, "url": search_link(p, query)} for p in platforms]
