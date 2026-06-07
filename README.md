# The Unofficial Guide — Project 1

---

## Domain

This system is about explaining the coffee flavor profiles from different origins. Most coffee drinkers encounter tasting notes every day (on bags, menus, and roaster websites) but have no framework for making sense of them. Knowing that Ethiopian coffees tend toward floral and fruity while Sumatran coffees lean earthy and full-bodied gives you a mental model that applies across every cup you'll ever drink. Roasters write tasting notes to sell their specific product, not to teach the underlying patterns.

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->


| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Espresso Coffee Guide| Costa Rica Coffee | https://espressocoffeeguide.com/gourmet-coffee/coffees-of-the-americas/costa-rica-coffee/ |
| 2 | Wikipedia - History of Coffee | A history of coffee and how different coffee beans grew from its origins  | https://en.wikipedia.org/wiki/History_of_coffee |
| 3 | Sweet Maria's | Brazil Coffee bean profile | https://library.sweetmarias.com/coffee-producing-countries/south-america/brazil-coffee-overview/ |
| 4|  Suvie| yirgacheffe coffee | https://blog.suvie.com/a-beginners-guide-to-coffee-ethiopian-yirgacheffe|

| 5 | Cooper Coffee Co. | Columbian Coffee profile | https://www.cooperscoffeeco.com/discover-the-rich-flavors-what-does-colombian-coffee-taste-like/?srsltid=AfmBOoqFCzpmkRplljGdNdaaTQyQZ2x1HSRrR-zLVM15AFfF7d8Gvrgo |
| 6 | Kona Farm Direct | Hawaii Coffee Beans  | https://www.konafarmdirect.com/post/the-ultimate-guide-to-kona-coffee-what-makes-it-the-world-s-most-sought-after-bean |
| 7 | Sweet Maria's  |  Sumatra Coffee | https://library.sweetmarias.com/coffee-producing-countries/indonesia-se-asia/sumatra-coffee-overview/ |
| 8 | Lavazz | Comparison of Arabica vs Robusta | https://www.lavazzausa.com/en/recipes-and-coffee-hacks/difference-type-arabica-robusta-coffee|
| 9 | The Extraordinary Rise: How Yunnan Coffee Became Asia’s New Coffee Champion | Yunnan Coffee profile  | https://naturebrewescape.com/the-extraordinary-rise-how-yunnan-coffee-became-asias-new-coffee-champion/|
| 10| Homelandcoffee  | Uganda coffee profile| https://homelandcoffee.co/blogs/our-blog/the-flavor-profile-of-ugandan-coffee?srsltid=AfmBOoroFIhGPOwUCy1CI0jJrK29wnAiGw6Mu4n7gBtAuiDhUDfcr7Uw |
| 11| Sweet Maria's | Ecuador coffee profile | https://library.sweetmarias.com/coffee-producing-countries/south-america/ecuador-coffee-overview/|
| 12| Sweet Maria's | Kenya Coffee profile | https://library.sweetmarias.com/coffee-producing-countries/africa/kenya-coffee-overview/|

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
