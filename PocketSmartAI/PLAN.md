# PocketSmart AI — Build Plan

## Source of truth
The uploaded PocketSmart AI design/project document is the primary source. It describes a budget-aware recommendation assistant for Home Interior, Party Planning, and Jewelry, using FastAPI/Jinja2, Gemini, authentication, sessions, and recommendation history.

## Implementation decisions
1. **Backend:** FastAPI, because the later milestones repeatedly define FastAPI routes, startup, Uvicorn, and Jinja2 templates. The document mentions Flask in an earlier architecture section; the implementation follows the later FastAPI specification.
2. **Frontend:** Server-rendered Jinja2 templates with HTML/CSS/vanilla JS to mirror the supplied screenshots closely and keep the app lightweight.
3. **Persistence:** SQLite with a small repository layer for users and recommendation history.
4. **Auth:** Cookie session + a `/token` JWT-compatible endpoint. Passwords are hashed with PBKDF2-HMAC using Python standard-library primitives.
5. **AI:** Optional Gemini integration through REST. The UI works without an API key using deterministic fallback recommendations. `GEMINI_MODEL` is configurable so the deployment can match the available Gemini model.
6. **Marketplace links:** Product/service cards expose search links to Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO and other platforms named by the design. No scraping is required for the demo; links are generated from the recommendation query.
7. **Jewelry image flow:** Optional image upload is validated, stored under `instance/uploads`, and included in Gemini multimodal requests when AI is enabled.
8. **No Git:** The project intentionally contains no Git repository or Git workflow.

## Screens / flows to reproduce
- Public home page
- Testimonials section + footer
- Register
- Login
- Authenticated dashboard
- Home planner form + home recommendation results
- Party planner form + party recommendation results
- Jewelry planner form + jewelry recommendation results
- Recommendation history + detail view
- Session info/data + token API

## Functional requirements
- Registration, login, logout
- Planner forms with validation
- Budget allocation and remaining-budget calculation
- Structured recommendation cards
- Platform shopping/search buttons
- Recommendation persistence to history
- History detail reuse
- Jewelry image upload
- Optional Gemini generation with graceful fallback
- Responsive desktop/mobile layout
- README + developer documentation + test coverage

## Visual fidelity targets
- Deep navy navigation bar
- Blue gradient hero/header areas
- Pale gray page backgrounds on authenticated screens
- White rounded cards with soft shadows
- Blue pill/gradient primary buttons
- Section cards with compact labels and icon headers
- Three-column planner/dashboard cards on desktop, stacked on mobile
- Typography, spacing, and content hierarchy modeled on the screenshots in the document
