# PocketSmart AI — QA Record

## Automated test coverage

Run:

```bash
pytest -q
```

The test suite covers:

- public home page
- health/startup endpoints
- CORS preflight
- registration and session cookie creation
- all three planner pages
- all three recommendation-generation flows
- recommendation history
- session info/data APIs
- JWT token issuance and bearer-token authentication
- recommendation details API
- recommendation detail page
- logout and post-logout access behavior

## Visual QA

The uploaded DOCX was rendered to page images and its embedded reference screenshots were inspected before implementation.

For a repeatable local visual smoke check, the current test flow renders each major screen through FastAPI's `TestClient`, then loads the resulting standalone HTML in Chromium and captures a screenshot. The captured pages cover Home, Dashboard, all three planners, all three recommendation views, and History.

Direct browser navigation to the local Uvicorn process was blocked by the execution environment's browser policy, so standalone HTML rendering was used for visual inspection instead of claiming a live-browser run against localhost.

## Manual acceptance checklist

1. Start the app and open `/`.
2. Create an account.
3. Open Home, Party, and Jewelry planners.
4. Generate a plan in each planner with and without Gemini configured.
5. Verify result pages show budget, remaining amount, recommendations, and shopping links.
6. Upload an outfit image in Jewelry and verify local preview + persisted request path.
7. Open History and a stored detail page.
8. Call `/token` and use its bearer token with `/session-data`.
9. Log out and verify protected pages redirect.
