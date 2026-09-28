# PocketSmart AI — Design-to-Implementation Mapping

The uploaded design/project document is the source of truth for the screen inventory and functional flow. The implementation keeps the visual language of the supplied screenshots: deep navy navigation, blue gradient hero bars, pale gray authenticated backgrounds, rounded white cards, blue pill actions, compact planner sections, and structured recommendation blocks.

| Design screen / requirement | Implementation |
|---|---|
| Public Home Page | `app/templates/home.html` at `/` |
| Testimonials | Included in Home page `#testimonials` section |
| Footer | Public footer plus authenticated footer variants |
| Register Page | `app/templates/auth/register.html` at `/register` |
| Login Page | `app/templates/auth/login.html` at `/login` |
| User Dashboard | `app/templates/dashboard.html` at `/dashboard` |
| Home Interior Budget Planner | `planner_home.html` + `/planner/home` |
| Home Interior Recommendations | `results_home.html` + `/generate-home` |
| Party Budget Planner | `planner_party.html` + `/planner/party` |
| Party Budget Recommendations | `results_party.html` + `/generate-party` |
| Jewelry Budget Planner | `planner_jewelry.html` + `/planner/jewelry` |
| Jewelry Budget Recommendations | `results_jewelry.html` + `/generate-jewelry` |
| Recommendation History | `history.html` + `/history` |
| Full recommendation reuse | `/recommendations/{rec_id}` |
| Recommendation details API | `/recommendations-details?id=...` |
| Login/register/logout | `/register`, `/login`, `/logout` |
| Token endpoint | `/token` |
| Session info/data | `/session-info`, `/session-data` |
| CORS setup | FastAPI `CORSMiddleware` |
| Startup behavior | FastAPI lifespan + `/startup` status endpoint |
| AI-generated suggestions | `app/services/gemini.py` |
| Mock/simulated platform sourcing | server-generated search links in `app/services/platforms.py` |
| Modular model/service layer | `app/models/` and `app/services/` |
| Responsive HTML/CSS/JS frontend | Jinja2 templates + `app/static/css/app.css` + `app/static/js/app.js` |

## Intentional small changes

The design document contains a mixed Flask/FastAPI narrative. The later milestones repeatedly specify FastAPI, Uvicorn, Jinja2, and FastAPI-style routes, so the implementation follows that later direction.

The design document also describes platform integrations but explicitly allows mock/simulated calls. The app therefore generates useful marketplace search links rather than scraping retailer pages or requiring retailer API credentials.

The source screenshots use sample imagery. The dashboard uses cropped copies of the user-provided reference images from the design document so the visual composition remains close without adding an unrelated external asset dependency.
