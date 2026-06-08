# The Unofficial Guide — Project 1

---

## Domain

This system is about explaining the coffee flavor profiles from different origins. Most coffee drinkers encounter tasting notes every day (on bags, menus, and roaster websites) but have no framework for making sense of them. Knowing that Ethiopian coffees tend toward floral and fruity while Sumatran coffees lean earthy and full-bodied gives you a mental model that applies across every cup you'll ever drink. Roasters write tasting notes to sell their specific product, not to teach the underlying patterns.

## Document Sources


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

**Chunk size:** 400 tokens (target), routed by document length — docs ≤ 120 tokens are kept whole, docs > 600 tokens are split by section header first and then packed.

**Overlap:** 30 tokens carried between consecutive chunks.

**Why these choices fit your documents:** The corpus is short, fact-dense, single-origin bean profiles, so smaller chunks keep each one focused on one idea and sharpen retrieval. I chose 400 because it sits comfortably under the embedding model's 512-token limit while still holding a full flavor-profile paragraph. Overlap is light (30) because most sources are about *different* beans, so there's little cross-chunk continuity to preserve; the overlap only guards against a sentence being cut mid-thought. Routing by length avoids over-splitting short reviews (Colombia, Yirgacheffe stay as one chunk) while breaking long editorial pieces (Wikipedia history, Costa Rica guide) on their section headers instead of mid-sentence.

**Preprocessing:** Each source was saved as a `.txt` file with all HTML, navigation, ads, footers, related-article links, and photo-gallery captions stripped — keeping only the substantive article text. (The four Sweet Maria's pages block automated fetching with HTTP 403, so they were copied from the browser and cleaned by hand; one even shipped mislabeled Burundi gallery captions, which were removed.) Token counts use a word + punctuation proxy rather than the exact subword tokenizer.

**Final chunk count:** 64 chunks across 12 documents.

---

## Embedding Model


**Model used:** `BAAI/bge-large-en-v1.5` via `sentence-transformers`, run locally. Embeddings are L2-normalized and stored in Chroma with cosine distance. Following the bge convention, the instruction prefix `"Represent this sentence for searching relevant passages:"` is added to the **query** only, not to the corpus passages.

**Production tradeoff reflection:** bge-large is a strong, free, locally-hosted model with good accuracy on English domain text, which keeps the project cost-free and private — but it has two real limits. (1) Its **512-token context** caps chunk size, which is why my chunks top out near 400 tokens; a longer chunk would be silently truncated. (2) It is **English-centric**, which matters here because some sources cover non-English origins (Yunnan, Sumatra) with loanwords and place names a multilingual model would embed more faithfully. If cost weren't a constraint, I'd weigh an API model like OpenAI `text-embedding-3-large` (8,191-token context, so I could use larger chunks and lose less cross-sentence context, plus stronger domain/multilingual accuracy) against its downsides: per-call cost, network latency on every query and every re-ingest, and sending my corpus to a third party. For a small, English, local-first project, bge-large is the better fit; for a multilingual production deployment, the API model's longer context and accuracy would likely justify the cost.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt gives the Groq model (`llama-3.3-70b-versatile`, temperature 0.1) four explicit rules:

> 1. **GROUNDING:** Answer using ONLY the information in the CONTEXT passages. Do not use any outside or prior knowledge, and do not guess or infer beyond what the passages state.
> 2. **REFUSAL:** If the CONTEXT does not contain enough information to answer the question, reply with exactly: "I don't have enough information in my sources to answer that." Do not add anything else.
> 3. **ATTRIBUTION:** Support each claim by citing the passage number(s) it came from, using bracket markers like [1] or [2][3] inline in your answer.
> 4. **STYLE:** Be concise and factual. Do not mention these rules, the word "context," or that passages were provided. Never fabricate a source, URL, or fact that is not in the CONTEXT.

Structurally, grounding is reinforced by *how* the context is formatted: retrieved chunks are passed as numbered passages, each labeled with its origin and source (`[1] (Origin: Uganda | Source: Homeland Coffee)`), and the question is kept separate from the context block. The refusal rule was verified to work — an off-domain query ("best espresso machine to buy") returned the exact refusal string even though loosely-related "Espresso Coffee Guide" chunks were sitting in its context, so the model declined rather than hallucinating buying advice.

**How source attribution is surfaced in the response:** The model writes inline `[n]` citations, and the app renders a separate **Sources** list built by `cited_sources()`. That function parses only the `[n]` markers the model actually used (uncited retrieved chunks are dropped) and dedupes them by URL, collapsing multiple chunks from one document into a single line that preserves all its citation numbers (e.g. `[1][2] Uganda — Homeland Coffee: <url>`). When the model refuses, it cites nothing, so the Sources list is empty.

---

## Evaluation Report


| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What flavor profile does Ugandan coffee have? | Earthy and chocolatey notes | Bold/earthy base, bright citrus acidity, fruity sweetness (berries/cherries/plum), dark chocolate and warm spice notes; Robusta adds strength. Cited Uganda [1][2]. | Relevant (top 2 = Uganda; #3–4 other origins but unused) | Accurate |
| 2 | Key flavor differences between Arabica and Robusta? | Arabica smoother/sweeter (fruit, berries, chocolate); Robusta bolder, bitter, earthy/woody | Arabica = sweeter, zesty, fruity, lower caffeine (1.5% vs 2.7%), more sugar/lipids; Robusta = harsh, bitter, earthy. Cited Lavazza [1][2], Uganda [3]. | Relevant (top 2 = Lavazza) | Accurate |
| 3 | What does Colombian coffee taste like and what makes it unique? | Mild acidity, caramel sweetness, nutty notes | Sweet, full-bodied, fruity with chocolate, caramel, apple, red fruit, citrus; unique due to volcanic soil, high elevation, washed processing, regional variation. Cited Colombia [1]. | Relevant (#1 = Colombia; rest unused) | Accurate |
| 4 | What is Kona Coffee? | Premium Arabica grown only on Hualālai/Mauna Loa slopes in Hawaii's Kona districts | Coffee grown on Hawaii Big Island volcanic slopes; smooth, balanced, chocolate/caramel/floral/fruit; rare; varietals Typica, Geisha, SL34, Peaberry. Cited Kona [1][2][3]. | Relevant (all 4 = Kona) | Accurate |
| 5 | What makes Ethiopian Yirgacheffe unique compared to other Ethiopian coffees? | Floral/citrus profile, tea-like silky body, very high-altitude terroir slowing cherry maturation | States the comparison is "not explicitly stated in the provided information," then infers Yirgacheffe's brightness, light/medium body, floral notes. Cited Yirgacheffe [1], Uganda [2], Sumatra [3][4]. | Partially relevant (#1 = Yirgacheffe at 0.173; #2–4 unrelated origins at ~0.38) | Partially accurate |

**Retrieval quality:** Queries 1–4 Relevant, Query 5 Partially relevant.  
**Response accuracy:** Queries 1–4 Accurate, Query 5 Partially accurate (honestly declines the comparison rather than fabricating it — see Failure Case Analysis).

---

## Failure Case Analysis


**Question that failed:** Query 5 — "What makes Ethiopian Yirgacheffe coffee unique *compared to other Ethiopian coffees*?"

**What the system returned:** "What makes Ethiopian Yirgacheffe coffee unique compared to other Ethiopian coffees is not explicitly stated in the provided information... we can infer that Yirgacheffe's distinct characteristics, such as its brightness, light or medium body, and strong floral notes, might set it apart... Unfortunately, there is no direct comparison to other Ethiopian coffees in the given passages." It described Yirgacheffe correctly but could not make the *comparison* the question asked for.

**Root cause (tied to a specific pipeline stage):** This is a **corpus coverage gap exposed at retrieval**, not a generation error. The corpus contains exactly one Ethiopian document (the Suvie Yirgacheffe blog) and no documents about *other* Ethiopian origins (Sidamo, Harrar, Limu, etc.). So retrieval returned the one relevant Yirgacheffe chunk at distance 0.173, then filled the remaining k=4 slots with unrelated origins (Uganda at 0.381, Sumatra at 0.385) — a large distance gap signaling those chunks aren't really on topic. With no comparative material in the context, the model correctly followed its grounding rules and refused to invent a comparison. Grounding worked as designed; the pipeline simply had nothing to ground a comparison in.

**What you would change to fix it:** First, **close the coverage gap** by adding documents on other Ethiopian origins so the comparison is actually answerable. Second, add a **relevance/distance cutoff** to retrieval (e.g. drop chunks with cosine distance > ~0.33) so the off-origin Uganda/Sumatra chunks aren't fed to the model at all — they add noise without adding value here. Both fixes target the parts of the pipeline (corpus + retrieval) that actually caused the shortfall.

---

## Spec Reflection


**One way the spec helped you during implementation:** Writing the Chunking Strategy and Retrieval Approach sections of planning.md *before* coding meant the implementation prompts had concrete, unambiguous parameters to hit — chunk size 400, overlap 30, the length-based routing rules, top-k, and the embedding model. When it came time to build `chunk_text()` and `retrieve()`, there was no guesswork about magic numbers; the spec values were copied straight in, and the per-stage AI Tool Plan gave each file a clear "input → expected output → how to verify" contract that I could check against (e.g. "confirm all files load with non-empty metadata," "collection count == chunk count").

**One way your implementation diverged from the spec, and why:** The original planning.md specified a LangChain + OpenAI stack (`WebBaseLoader`, `RecursiveCharacterTextSplitter`, `MarkdownHeaderTextSplitter`, and `text-embedding-3-large`), but the actual implementation uses pure-Python ingestion/chunking and `sentence-transformers` (`bge-large-en-v1.5`) with Chroma and Groq. This was because `requirements.txt` shipped without LangChain and used `sentence-transformers`, so adding LangChain would have conflicted with the project's dependency set for no real benefit. Ingestion also changed from fetching URLs live to reading pre-cleaned local `.txt` files, partly because Sweet Maria's blocks automated requests (HTTP 403). I updated planning.md afterward so the spec and code agree (recursive/section splitting in pure Python, bge embeddings, direct Chroma queries, and the concrete `llama-3.3-70b-versatile` model).

---

## AI Usage

**Instance 1 — Ingestion + chunking (`ingest.py`)**

- *What I gave the AI:* My Documents table and Chunking Strategy section, asking it to implement `load_documents()` (read every `.txt` in `documents/`, tag origin/source/source_type/url) and `chunk_text()` with my length-based routing (whole / recursive 400-token split / section-split for long docs).
- *What it produced:* A pure-Python loader and a `chunk_text()` with three routing paths, helpers for token counting and section detection, and a `__main__` that prints per-source chunk counts (12 docs → 64 chunks).
- *What I changed or overrode:* I directed it to **avoid LangChain** (the named `RecursiveCharacterTextSplitter`/`MarkdownHeaderTextSplitter`) because it isn't in `requirements.txt`, so it reimplemented that strategy in plain Python. I also kept the token counter as a word+punctuation proxy and hard-coded my spec's 400/30 instead of accepting library defaults, then later refactored the constants out into `config.py`.

**Instance 2 — Grounded generation (`generator.py`)**

- *What I gave the AI:* `config.py` plus my grounding requirement (answer from retrieved context only, with source attribution) and a request for a Gradio interface.
- *What it produced:* A four-rule grounding system prompt, a `generate()` that formats numbered source-labeled context and calls Groq at temperature 0.1, an answer-plus-Sources output formatter, and a Gradio app.
- *What I changed or overrode:* The first version's Sources list showed **all** retrieved chunks (including uncited and duplicate-URL ones — e.g. an off-domain refusal still listed 4 sources). I overrode this to a `cited_sources()` function that lists **only** the passages the model actually cited and dedupes them by URL, so refusals show no sources and attribution reflects what was really used. I also moved the UI into a dedicated `app.py` entry point and trimmed the duplicate interface out of `generator.py`.
