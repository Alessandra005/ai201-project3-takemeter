# TakeMeter – Planning Document
**Community:** r/movies  
**Project:** Fine-tuned discourse quality classifier

---

## 1. Community

I chose r/movies (approximately 35 million members) as my community. It's an ideal fit for a classification task because the discourse is extremely varied in quality: the same film can generate posts ranging from rigorous structural analysis to pure hype to knee-jerk emotional reactions. Unlike niche film communities (e.g., r/TrueFilm), r/movies attracts a broad range of users, which means the full spectrum of discourse quality — from careful argument to one-sentence hot takes — appears regularly in the same feed. This variation is exactly what makes the classification task interesting and non-trivial.

---

## 2. Label Taxonomy

### `analysis`
**Definition:** The post makes a structured argument about a film, director, genre, or industry trend, supported by specific evidence — plot details, cinematographic observations, historical comparisons, box office data, or references to other works. The core claim would be weakened if you removed the supporting reasoning.

**Example 1:**  
> "Nolan's use of non-linear structure in Memento isn't just a stylistic gimmick — it forces the viewer into the same epistemological position as Leonard, making the unreliable narrator a structural property of the film rather than just a plot device. Compare this to how he uses it in Dunkirk, where the three timelines converge rather than fragment."

**Example 2:**  
> "The decline of the mid-budget drama at the theatrical box office is largely a streaming-era phenomenon. Films like Manchester by the Sea (2016) and Spotlight (2015) were hits; today their equivalents go straight to Netflix because studios won't greenlight a $25M drama with no franchise potential."

---

### `hot_take`
**Definition:** A bold, confident opinion stated without supporting evidence or with only superficial justification. The claim may be defensible but the post asserts rather than argues. The framing is often provocative or contrarian.

**Example 1:**  
> "Interstellar is overrated and the third act completely ruins what could have been a masterpiece. The bookshelf scene is embarrassing."

**Example 2:**  
> "Christopher Nolan has never actually directed a good performance from any actor. Every character in his movies talks like a Wikipedia article."

---

### `reaction`
**Definition:** An immediate emotional response to a specific film, trailer, casting announcement, or industry event. Little to no argument — the post expresses a feeling in the moment. Often triggered by fresh news or a recent viewing.

**Example 1:**  
> "Just saw Dune Part 2 in IMAX and I am not okay. That sandworm scene absolutely destroyed me. Best theater experience in years."

**Example 2:**  
> "They cast him?? I don't know how to feel about this. I love the actor but I genuinely cannot picture him in this role."

---

## 3. Hard Edge Cases

**The hardest anticipated boundary: `hot_take` vs. `analysis`**

Consider this post:
> "Hereditary is the best horror film of the last decade — it uses grief as its central terror engine rather than jump scares, which is why it holds up on rewatch."

This could be `hot_take` (confident superlative claim, brief justification) or `analysis` (identifies a specific structural mechanism and explains why it matters for rewatchability).

**Decision rule:** If the post names a specific structural, thematic, or technical mechanism *and* explains how it produces a particular effect, label it `analysis` — even if it begins with a bold opinion. If the reasoning is one clause that functions more as decoration than argument (i.e., the opinion would stand the same way without it), label it `hot_take`. The test: *would removing the "because" clause change the post's persuasive force?* If yes → `analysis`. If no → `hot_take`.

**Secondary edge case: `reaction` vs. `hot_take`**

A post like "I finally watched The Godfather and I think it's the most overrated film ever made" is triggered by a specific viewing event (reaction) but also asserts a strong opinion (hot_take). Decision rule: if the post is explicitly anchored to a recent personal event ("just watched," "first time seeing," "saw it last night") and the opinion is expressed as a feeling rather than a claim about the film's objective properties, label it `reaction`. If the opinion is stated as a general position without temporal anchoring, label it `hot_take`.

---

## 4. Data Collection Plan

**Source:** r/movies via Reddit's public JSON API (no authentication required for read access).  
**Target:** 250–280 posts (buffer above 200 minimum to allow for filtering).  
**Distribution target:** ~90 examples per label (roughly balanced across `analysis`, `hot_take`, `reaction`).

**Collection strategy:**
- Pull from multiple feed types: `top` (past year), `hot`, and search queries for keywords likely to surface each label type.
- `analysis` tends to appear in longer posts and in threads about older films.
- `hot_take` tends to appear in opinion threads and "unpopular opinion" megathreads.
- `reaction` tends to appear in trailer reaction threads, "just watched" posts, and casting news threads.

**If a label is underrepresented after 200 examples:**  
Target specific post types. For `reaction`, search "just watched" or "first time" in r/movies. For `analysis`, search "video essay" responses or "cinematography" discussion threads. Do not oversample from a single thread to avoid topic bias.

---

## 5. Evaluation Metrics

**Primary metric:** Per-class F1 score (harmonic mean of precision and recall for each label).  
**Why:** Accuracy alone is misleading if classes are slightly imbalanced — a model that always predicts `hot_take` could achieve 35%+ accuracy while being useless. F1 per class shows whether the model actually learns all three distinctions.

**Secondary metric:** Macro-averaged F1 (unweighted average of per-class F1).  
**Why:** Treats each class equally regardless of size, which is appropriate here since we care about all three label types performing well — not just the majority class.

**Also reported:** Confusion matrix, to identify which specific label pairs are being confused and in which direction.

**Baseline comparison:** Zero-shot Groq (llama-3.3-70b-versatile) on the same test set, using the same label definitions from this document as the prompt. This measures what fine-tuning actually adds over a general-purpose LLM with no community-specific training.

---

## 6. Definition of Success

**Minimum acceptable:** Fine-tuned model achieves macro-averaged F1 ≥ 0.65 on the test set, with no single class below F1 = 0.55. This represents meaningful learning across all three distinctions, not just the easiest one.

**Good enough for deployment:** Macro F1 ≥ 0.72, with the fine-tuned model outperforming the zero-shot baseline by at least 8 percentage points on macro F1. At this level, a community moderation tool using the classifier would make correct decisions roughly 3 out of 4 times — useful as a signal, not a final judge.

**Red flags that would prompt re-evaluation:**  
- Any class F1 below 0.40 (model hasn't learned that boundary at all)  
- Fine-tuned model performs within 3 points of the random baseline (fine-tuning added nothing)  
- Test accuracy above 95% (likely data leakage or labels that are too easy)

---

## 7. AI Tool Plan

### Label stress-testing
Before finalizing label definitions, I will paste the three label definitions and the two edge case descriptions into Claude and ask it to generate 10 posts that sit at the `hot_take`/`analysis` boundary. If more than 3 of those posts are genuinely unclassifiable by my definitions, I will revise the decision rule before annotating.

### Annotation assistance
I will use Groq (llama-3.3-70b-versatile) to pre-label all collected examples using the definitions from this document. I will then review every pre-assigned label before accepting it, correcting any that disagree with my definitions. I will track which examples were pre-labeled in a `prelabeled` column in the CSV. All pre-labels I overrode will be logged.

### Failure analysis
After generating wrong predictions from the fine-tuned model, I will paste the full list of misclassified examples (with true and predicted labels) into Claude and ask it to identify systematic patterns — e.g., "short posts," "sarcastic phrasing," "specific film titles," "a specific label pair." I will verify every suggested pattern by re-reading the examples myself before including it in the evaluation report.

---

## 8. Hard Annotation Decisions (to be updated during Milestone 3)

*(This section will be populated with at least 3 specific difficult cases encountered during annotation, per the project spec.)*

| Post (truncated) | Labels considered | Decision | Reasoning |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

---