# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Regional flavor profiles of coffee

This knowledge is valuable because most coffee drinkers encounter tasting notes every day (on bags, menus, and roaster websites) but have no framework for making sense of them. Knowing that Ethiopian coffees tend toward floral and fruity while Sumatran coffees lean earthy and full-bodied gives you a mental model that applies across every cup you'll ever drink.

It's hard to find through official channels because the information is scattered and inconsistent. Roasters write tasting notes to sell their specific product, not to teach the underlying patterns. The Specialty Coffee Association has rigorous educational materials, but they're designed for industry professionals, not everyday drinkers. No single authoritative source draws the complete map — you have to triangulate across dozens of roasters, importers, and review sites to piece it together yourself.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Espresso Coffee Guide| Costa Rica Coffee | https://espressocoffeeguide.com/gourmet-coffee/coffees-of-the-americas/costa-rica-coffee/ |
| 2 | Wikipedia - History of Coffee | A history of coffee and how different coffee beans grew from its origins  | https://en.wikipedia.org/wiki/History_of_coffee |
| 3 | Sweet Maria's | Brazil Coffee bean profile | https://library.sweetmarias.com/coffee-producing-countries/south-america/brazil-coffee-overview/ |
| 4 | Coffee Review | Kenneth Davids' long-running review site with thousands of scored coffees organized by origin | coffeereview.com |
| 5 | Cooper Coffee Co. | Columbian Coffee profile | https://www.cooperscoffeeco.com/discover-the-rich-flavors-what-does-colombian-coffee-taste-like/?srsltid=AfmBOoqFCzpmkRplljGdNdaaTQyQZ2x1HSRrR-zLVM15AFfF7d8Gvrgo |
| 6 | Kona Farm Direct | Hawaii Coffee Beans  | https://www.konafarmdirect.com/post/the-ultimate-guide-to-kona-coffee-what-makes-it-the-world-s-most-sought-after-bean |
| 7 | Sweet Maria's  |  Sumatra Coffee | https://library.sweetmarias.com/coffee-producing-countries/indonesia-se-asia/sumatra-coffee-overview/ |
| 8 | Lavazz | Comparison of Arabica vs Robusta | https://www.lavazzausa.com/en/recipes-and-coffee-hacks/difference-type-arabica-robusta-coffee|
| 9 | The Extraordinary Rise: How Yunnan Coffee Became Asia’s New Coffee Champion | Yunnan Coffee profile  | https://naturebrewescape.com/the-extraordinary-rise-how-yunnan-coffee-became-asias-new-coffee-champion/|
| 10| Homelandcoffee  | Uganda coffee profile| https://homelandcoffee.co/blogs/our-blog/the-flavor-profile-of-ugandan-coffee?srsltid=AfmBOoroFIhGPOwUCy1CI0jJrK29wnAiGw6Mu4n7gBtAuiDhUDfcr7Uw |
| 11| Sweet Maria's | Ecuador coffee profile | https://library.sweetmarias.com/coffee-producing-countries/south-america/ecuador-coffee-overview/|
| 12| Sweet Maria's | Kenya Coffee profile | https://library.sweetmarias.com/coffee-producing-countries/africa/kenya-coffee-overview/|
| 13|  Suvie| yirgacheffe coffee | https://blog.suvie.com/a-beginners-guide-to-coffee-ethiopian-yirgacheffe|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
