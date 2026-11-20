# The Market Journal: instructions for Claude

Public blog for Steven Smith, Team Smith, and The Market Real Estate Co. Goal: rank in Google and AI search nationally with genuinely useful, accurate real estate content. Site is static: `posts/*.md` → `python3 build.py` → `docs/` (GitHub Pages serves `/docs` on `main`).

## Daily post workflow
1. Read `posts/` (titles + summaries) so you never repeat a topic or angle. Check recent categories and rotate.
2. Pick one topic (see Topic mix). For anything involving rates, prices, laws, or market data, **WebSearch first** and use only what you retrieved. Cite sources inline as links and end the post with a `## Sources` list. If you can't verify a number, leave it out.
3. Write `posts/YYYY-MM-DD-slug.md` with front matter: `title`, `date` (today, America/Chicago), `category`, `summary` (1–2 sentences, under 160 characters, answers the question).
4. Run `python3 build.py` and confirm it builds with no errors. Open the new `docs/posts/<slug>/index.html` and check it.
5. Publishing mode: **AUTOMATIC** (Steven switched from review-first on Nov 19, 2026). Before publishing, re-read the post against Post standards and Hard rules: every number sourced and linked, verified production numbers only, no invented stories, correct sign-off, no lender names, Fair Housing. If anything fails and you cannot fix it, do not publish: push it to a `post/YYYY-MM-DD-slug` branch, open a pull request, and say why. Otherwise commit the post and `docs/` straight to `main` and push; it goes live in a couple of minutes.

## Post standards
- 600–1,000 words. Plain language, specific, useful. Lead with the answer. Use `##` headings, short paragraphs, and lists where they help. Written in Steven's voice ("we", "our team"), by Steven Smith.
- Personal experience line: in roughly 3–4 of every 10 posts (not every post), add one short, natural line from Steven's team experience, e.g. "My team has been through just about every kind of market interest rates can create," "In our experience…," "That's something my team has seen more times than we can count." Use only general lines that are true for a team with 22+ years in the business. Never invent a specific client, deal, date, or number. Check recent posts so these lines don't repeat word for word.
- Write for a national audience unless the topic is explicitly local. Local Louisiana/Alabama posts are fine occasionally (about 1 in 5).
- End with a short, practical takeaway. The page template adds the call-to-action; do not repeat contact info in the body.
- Title: clear and searchable, answer-style ("How much…", "What happens if…"). No clickbait.
- Answer-first structure suits AI search: a direct 1–2 sentence answer near the top, then detail. Use question-style `##` headings when natural.

## Topic mix (rotate)
Buyers (first-time buyers, offers, inspections, appraisals, closing costs, mortgage basics without naming lenders) · Sellers (pricing, prep, staging, negotiation, timing) · Market Updates (national or regional, sourced and dated) · Industry (AI in real estate, how to choose an agent, how teams work) · Agents (careers, training, working with a team, recruiting; include "Why Team Smith" angles sparingly) · Homeownership (maintenance, insurance, moving, seasonal checklists) · Investors and Relocation (high-level only). Categories must stay consistent: reuse existing category names before creating new ones.

## Hard rules (from Steven)
- Spell **Steven** with a v. Always.
- Team Smith production: only RealTrends Verified 2025 numbers: **322 sides and $109.14M**. Never use 325–350 closings or ~$125M. Reviews: "600+ five-star Zillow reviews" and "150+ five-star Google reviews" (never "5.0 stars" for Google).
- Sign-off/tagline is exactly **Team Smith | Experience Results**. Never "With Team Smith, you experience results."
- (225) 413-3376 is Steven Smith's personal cell: always label it "Steven Smith", never "Team Smith". Office number for The Market Real Estate Co.: (225) 953-8889. **No tap-to-call (`tel:`) links**; show numbers as plain text.
- The Market Real Estate Co. does **not** do property management. Never imply it does.
- Never name a specific lender; say "a lender" or "your lender."
- Never put down or grade vendors, partners, competitors, or other brokerages. Facts only.
- Never invent client stories, testimonials, quotes, statistics, or awards. Use only facts in this file, existing posts, or sources you retrieved and cite.
- Fair Housing: never steer by race, religion, familial status, disability, national origin, sex, or other protected class. Describe homes and areas by facts, not who "belongs." No legal, tax, or financial advice; say to consult a professional where relevant.
- Logo and brand color are dull gold (`#a8895a`); do not change the template colors.
- Markets: Greater Baton Rouge, Gulf Coast of Alabama, Greater Huntsville, Northshore (Mandeville, Madisonville, Covington). Licensed in Louisiana and Alabama. The team website your225market.com is Louisiana only; do not link to it as if it covers Alabama.

## Facts you may use
Steven Smith: broker/owner of The Market Real Estate Co. (independent boutique brokerage, residential and commercial, opened 2022); licensed in Louisiana and Alabama since 2004; 22+ years in real estate; named 2025 Broker of the Year by Baton Rouge Real Producers (his own bio). Team Smith: 25 agents (21 Louisiana, 4 Alabama), Zillow Preferred team, no team fees for agents. Steven and his wife Laura started the Christmas Give charity in 2008.

## Technical notes
- `config.json`: `site_url` and `custom_domain`. When a custom domain is connected, set both (e.g. `"site_url": "https://example.com"`, `"custom_domain": "example.com"`) and rebuild.
- Posts dated in the future are skipped by the build until their date.
- No dependencies: `build.py` is plain Python 3.
- Never edit files in `docs/` by hand. Always rebuild.
