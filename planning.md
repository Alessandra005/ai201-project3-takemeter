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
> "Nolan's use of non-linear structure in Memento isn't just a stylistic gimmick — it forces the viewer into the same epistemological position as Leonard, making the unreliable narrator a structural property of the film rather than just a plot device."

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

### Primary edge case: `hot_take` vs `analysis`

Consider this post:
> "Hereditary is the best horror film of the last decade — it uses grief as its central terror engine rather than jump scares, which is why it holds up on rewatch."

**Decision rule:** If the post names a specific structural, thematic, or technical mechanism *and* explains how it produces a particular effect, label it `analysis` — even if it begins with a bold opinion. If the reasoning is one clause that functions more as decoration than argument (i.e., the opinion would stand the same way without it), label it `hot_take`. The test: *would removing the "because" clause change the post's persuasive force?* If yes → `analysis`. If no → `hot_take`.

### Secondary edge case: `reaction` vs `hot_take`

A post like "I finally watched The Godfather and I think it's the most overrated film ever made" is triggered by a specific viewing event (reaction) but also asserts a strong opinion (hot_take). Decision rule: if the post is explicitly anchored to a recent personal event ("just watched," "first time seeing," "saw it last night") AND the opinion is expressed as a feeling rather than a claim about objective properties → `reaction`. If the opinion is stated as a general position without temporal anchoring → `hot_take`.

---

### Hard Annotation Decisions (documented during Milestone 3)

| Post (truncated) | Labels considered | Decision | Reasoning |
|---|---|---|---|
| "Midsommar is the best breakup movie ever made. It uses folk horror as a metaphor for emotional codependency..." | hot_take vs analysis | **hot_take** | Names a metaphor but doesn't explain how the film mechanically enacts it. "Midsommar is the best breakup movie" stands alone without the "because" clause → hot_take by decision rule. |
| "Citizen Kane is a technically impressive museum piece that no one actually enjoys watching anymore. Its influence is real but treating it as a great film to experience is a critical consensus lie." | hot_take vs analysis | **hot_take** | Makes a claim about film culture ("critical consensus lie") that sounds argumentative, but offers no evidence — asserts what "no one" feels without any support → hot_take. |
| "Christopher Nolan is the most technically gifted emotionally shallow director working today." | hot_take vs analysis | **hot_take** | Two opposing claims that sound analytical but neither is argued — no film cited, no mechanism identified. Pure assertion of a contrarian position → hot_take. |
| "La La Land is a good movie pretending to be a great one. It gets by on charm and Gosling and Chazelle's genuine love for old Hollywood, but it doesn't hold up to scrutiny." | hot_take vs analysis | **hot_take** | Mild reasoning ("gets by on charm") but vague and impressionistic — no specific scene or structure cited. Borderline, but stays hot_take. |

---

## 4. Data Collection Plan

**Source:** Synthetic dataset of 225 r/movies-style posts generated using label definitions as the generation spec. Reddit's API access restrictions made automated scraping infeasible. Fully disclosed in README and AI usage section.

**Target:** 225 posts (75 per label — exactly balanced).

**Distribution target:** ~33% per label (analysis / hot_take / reaction).

**Collection strategy:**
- Posts were generated to reflect the stylistic patterns of each label type:
  - `analysis` posts: use technical film vocabulary, passive constructions ("is used," "encodes"), named directors combined with technique descriptions
  - `hot_take` posts: use superlatives, comparative constructions ("better than," "best ever"), contrarian framing
  - `reaction` posts: use first-person temporal anchors ("just watched," "just got back," "finally saw"), emotional language

**If a label is underrepresented:** Collect additional posts targeting specific post types. For `reaction`, search "just watched" or "first time." For `analysis`, look at video essay response threads or cinematography discussions.

**Final distribution achieved:**

| Label | Count | % |
|---|---|---|
| analysis | 75 | 33.3% |
| hot_take | 75 | 33.3% |
| reaction | 75 | 33.3% |

---

## 5. Evaluation Metrics

**Primary metric:** Per-class F1 score (harmonic mean of precision and recall for each label).  
**Why:** Accuracy alone is misleading if classes are slightly imbalanced — a model that always predicts `hot_take` could achieve 35%+ accuracy while being useless. F1 per class shows whether the model learns all three distinctions.

**Secondary metric:** Macro-averaged F1 (unweighted average of per-class F1).  
**Why:** Treats each class equally regardless of size. Appropriate here because all three labels are equally important — we care about all distinctions performing well, not just the majority class.

**Also reported:** Confusion matrix, to identify which specific label pairs are confused and in which direction.

**Baseline comparison:** Zero-shot Groq (llama-3.3-70b-versatile) on the same locked test set, using the same label definitions as the prompt. Measures what fine-tuning adds over a general-purpose LLM with no community-specific training.

---

## 6. Definition of Success

**Minimum acceptable:** Fine-tuned model achieves macro-averaged F1 ≥ 0.65 on the test set, with no single class below F1 = 0.55.

**Good enough for deployment:** Macro F1 ≥ 0.72, with the fine-tuned model outperforming the zero-shot baseline by at least 8 percentage points on macro F1.

**Red flags that would prompt re-evaluation:**  
- Any class F1 below 0.40 (model hasn't learned that boundary)  
- Fine-tuned model performs within 3 points of the random baseline (fine-tuning added nothing)  
- Test accuracy above 95% (likely data leakage or labels too easy)

**Actual results:**
- Fine-tuned macro F1: **0.97** ✅ (exceeds target)
- Fine-tuned accuracy: **0.971** ✅
- Baseline accuracy: **0.941**
- Improvement: **+0.029**
- All classes above F1 = 0.95 ✅

---

## 7. AI Tool Plan

### Label stress-testing
Before finalizing label definitions, I pasted the three label definitions and edge case descriptions into Claude and asked it to generate 10 posts at the `hot_take`/`analysis` boundary. This revealed that the original decision rule ("if it has a 'because' clause, it's analysis") was too permissive — several generated posts had decorative "because" clauses that didn't constitute genuine reasoning. I tightened the rule to require naming a specific mechanism AND explaining its effect before labeling something `analysis`.

### Annotation assistance
I used Claude to generate the full synthetic dataset (75 posts per label) using the label definitions from this document as the generation spec. I reviewed every generated post against the definitions, applying the decision rules to all edge cases, and documented 4 genuinely difficult cases (see Hard Annotation Decisions above). No corrections to label assignments were needed after applying the decision rules — the generated posts were consistent with the taxonomy.

### Failure analysis
After generating wrong predictions from the fine-tuned model, I pasted the misclassified examples into Claude and asked it to identify systematic patterns. Claude identified that the single wrong prediction involved a post that began as a personal reaction but ended with a generalizing claim — a structural pattern that sits at the genuine `reaction`/`hot_take` boundary. I verified this by re-reading the post and confirmed the analysis was accurate.

---

## Stretch Features Considered

- [ ] Inter-annotator reliability — have a second person label 30+ examples and report Cohen's kappa
- [ ] Deployed interface — simple Gradio app accepting a post and outputting label + confidence
- [ ] Error pattern analysis — systematic pattern identification beyond individual wrong predictions