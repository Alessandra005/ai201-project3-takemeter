# TakeMeter — r/movies Discourse Quality Classifier

A fine-tuned text classifier that evaluates the quality of film discourse in r/movies, distinguishing between structured analysis, bold hot takes, and immediate emotional reactions.

---

## Community Choice

I chose r/movies (approximately 35 million members) because its discourse is unusually varied in quality. The same film can generate posts ranging from rigorous structural analysis to pure hype to knee-jerk emotional reactions — often in the same thread. Unlike niche communities such as r/TrueFilm, r/movies attracts a broad range of users, which means the full spectrum of discourse quality appears regularly. This variation makes the classification task genuinely non-trivial: the boundaries between labels are real and contested, not obvious.

---

## Label Taxonomy

### `analysis`
The post makes a structured argument about a film, director, genre, or industry trend, supported by specific evidence — plot details, cinematographic observations, historical comparisons, box office data, or references to other works. The core claim would be weakened if the supporting reasoning were removed.

**Example 1:** "Nolan structures Oppenheimer in two color modes — color for Oppenheimer's subjective sections, black and white for Strauss's hearing. The distinction is epistemological: color represents lived experience, black and white represents institutional record. The film is about which mode gets to define historical truth."

**Example 2:** "Bong Joon-ho uses vertical space throughout Parasite to encode class — the Parks live in a modernist house on a hill with maximum natural light, while the Kims' semi-basement sits below street level with a single window looking up at people's feet. Every major scene of class conflict is staged on stairs."

---

### `hot_take`
A bold, confident opinion stated without supporting evidence or with only superficial justification. The claim may be defensible but the post asserts rather than argues. The framing is often provocative or contrarian.

**Example 1:** "Interstellar's third act completely ruins what should have been a near-masterpiece. The bookshelf scene is embarrassing."

**Example 2:** "Christopher Nolan is the most technically gifted emotionally shallow director working today. Every film he makes is a masterclass in construction and a failure of feeling."

---

### `reaction`
An immediate emotional response to a specific film, trailer, casting announcement, or industry event. Little to no argument — the post expresses a feeling in the moment. Often anchored to a recent personal viewing or fresh news.

**Example 1:** "Just got back from seeing Oppenheimer in IMAX and I am genuinely shaking. The Trinity test sequence is one of the most overwhelming things I've ever experienced in a theater."

**Example 2:** "Watched Aftersun on a flight and cried for the last 20 minutes while trying not to let anyone see. Something about it hit a very specific kind of grief I didn't have a name for."

---

## Data Collection

**Source:** Synthetic dataset of 225 r/movies-style posts generated to reflect authentic discourse patterns in the community, disclosed fully per course requirements. Reddit's API access restrictions made automated scraping infeasible; the synthetic approach allowed precise control over label balance and post variety.

**Labeling process:** Each post was written to embody a specific label, then reviewed against the label definitions in `planning.md`. Every post was evaluated using the decision rules described below. The `prelabeled` column in the CSV tracks generation origin.

**Label distribution:**

| Label | Count | Percentage |
|---|---|---|
| analysis | 75 | 33.3% |
| hot_take | 75 | 33.3% |
| reaction | 75 | 33.3% |

**Train / Validation / Test split:** 157 / 34 / 34 (70% / 15% / 15%), stratified by label.

---

### Three Difficult-to-Label Examples

**1. "Midsommar is the best breakup movie ever made. It uses folk horror as a metaphor for emotional codependency and it's more accurate about that dynamic than any conventional love story."**
Labels considered: `hot_take` vs `analysis`. The post names a mechanism (folk horror as codependency metaphor) which sounds like analysis. Decision rule applied: does removing the "because" clause weaken the post's rhetorical force? "Midsommar is the best breakup movie ever made" stands completely on its own — the metaphor claim is decorative, not argumentative. → `hot_take`.

**2. "Citizen Kane is a technically impressive museum piece that no one actually enjoys watching anymore. Its influence is real but treating it as a great film to experience is a critical consensus lie."**
Labels considered: `hot_take` vs `analysis`. The post makes a claim about film culture (critical consensus is fabricated) that sounds argumentative. But no evidence is offered — it asserts what "no one" feels without any support. → `hot_take`.

**3. "La La Land is a good movie pretending to be a great one. It gets by on charm and Gosling and Chazelle's genuine love for old Hollywood, but it doesn't hold up to scrutiny."**
Labels considered: `hot_take` vs `analysis`. Gives mild reasoning ("gets by on charm") but the reasoning is vague and impressionistic — no specific scene, technique, or structural observation cited. The "scrutiny" claim is asserted not demonstrated. → `hot_take`.

---

## Fine-Tuning Approach

**Base model:** `distilbert-base-uncased` — a smaller, faster variant of BERT that retains strong performance on classification tasks and trains in under 15 minutes on a free Colab T4 GPU.

**Training setup:**
- Framework: HuggingFace `transformers` + `Trainer` API
- Epochs: 3
- Learning rate: 2e-5
- Batch size: 16 (train), 32 (eval)
- Weight decay: 0.01
- Warmup steps: 50
- Best model selected by validation accuracy

**Key hyperparameter decision:** I kept the default learning rate of 2e-5 rather than increasing it. With only 157 training examples, a higher learning rate (e.g. 5e-5) risks overshooting the loss minimum on a small dataset and producing an unstable model. The training curve confirmed this was the right choice: validation loss decreased smoothly across all 3 epochs (1.11 → 1.07 → 0.95) with no signs of divergence.

---

## Baseline Description

**Model:** `llama-3.3-70b-versatile` via Groq API (zero-shot, no fine-tuning).

**Prompt used:**
```
You are classifying posts from r/movies on Reddit.
Assign each post to exactly one of the following categories.

analysis: The post makes a structured argument about a film supported by specific evidence — plot details, cinematographic observations, historical comparisons, or references to other works. The reasoning would be weakened if removed.
Example: "Nolan structures Oppenheimer in two color modes..."

hot_take: A bold, confident opinion stated without supporting evidence or with only superficial justification. The claim is asserted rather than argued, often with provocative or contrarian framing.
Example: "Interstellar's third act completely ruins what should have been a near-masterpiece..."

reaction: An immediate emotional response to a specific film, trailer, casting announcement, or industry event. Little to no argument — the post expresses a feeling in the moment.
Example: "Just got back from seeing Oppenheimer in IMAX and I am genuinely shaking..."

Respond with ONLY the label name. Do not explain your reasoning.
Valid labels: analysis / hot_take / reaction
```

All 34 test examples were parseable (0 unparseable responses).

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy |
|---|---|
| Zero-shot baseline (Groq llama-3.3-70b) | 0.941 |
| Fine-tuned DistilBERT | **0.971** |
| Improvement | +0.029 |

### Per-Class Metrics — Fine-Tuned Model

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| analysis | 1.00 | 1.00 | 1.00 | 11 |
| hot_take | 0.92 | 1.00 | 0.96 | 12 |
| reaction | 1.00 | 0.91 | 0.95 | 11 |
| **macro avg** | **0.97** | **0.97** | **0.97** | 34 |

### Per-Class Metrics — Zero-Shot Baseline

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| analysis | 1.00 | 1.00 | 1.00 | 11 |
| hot_take | 1.00 | 0.83 | 0.91 | 12 |
| reaction | 0.85 | 1.00 | 0.92 | 11 |
| **macro avg** | **0.95** | **0.94** | **0.94** | 34 |

### Confusion Matrix — Fine-Tuned Model

|  | Predicted: analysis | Predicted: hot_take | Predicted: reaction |
|---|---|---|---|
| **True: analysis** | 11 | 0 | 0 |
| **True: hot_take** | 0 | 12 | 0 |
| **True: reaction** | 0 | 1 | 10 |

The model is nearly perfect. The single error is one `reaction` post misclassified as `hot_take`.

---

### Wrong Predictions — Analysis

**Wrong prediction #1**
> "Watched 2001 for a film class and the Stargate sequence hit different on a projector with full surround sound than it does on a laptop. Some films are genuinely made for a specific experience."
- True label: `reaction`
- Predicted: `hot_take` (confidence: 0.36)

**Why it failed:** This post is anchored to a recent personal viewing event ("for a film class") and expresses a feeling ("hit different") — the classic signature of `reaction`. However, the second sentence ("some films are genuinely made for a specific experience") reads as a general claim rather than an immediate feeling, which pulled the model toward `hot_take`. The post sits genuinely at the `reaction`/`hot_take` boundary: it begins as a reaction and ends with a mild generalizing assertion. The model's low confidence (0.36) correctly reflects the ambiguity. This is a labeling boundary problem, not a model failure — the post is legitimately borderline.

**Why only one error:** The fine-tuned model converged to near-perfect performance on the test set, which reflects both the structural clarity of the three labels and the consistent stylistic patterns in the dataset. `analysis` posts use specific technical vocabulary (cinematography terms, director names combined with technique descriptions); `reaction` posts use first-person temporal anchors ("just watched," "just got back"); `hot_take` posts use superlatives and contrarian framing. These surface patterns are learnable by DistilBERT even with 157 training examples. The baseline Groq model also performed very well (94.1%), which confirms the task has meaningful but learnable signal.

**Baseline-specific error analysis:** The zero-shot baseline made 2 errors compared to the fine-tuned model's 1. The baseline confused 2 `hot_take` posts as `reaction` — likely posts that mentioned specific films by name with emotional language, which the baseline read as personal viewing reactions. The fine-tuned model learned to weight the assertive, generalized framing of `hot_take` more strongly than the specific film reference.

---

### Sample Classifications

| Post (truncated) | Predicted Label | Confidence | Notes |
|---|---|---|---|
| "Nolan's use of practical effects in Oppenheimer — real explosions, zero CGI..." | `analysis` | 0.94 | Correctly identified: names a specific technique (practical effects) and explains its effect on the viewer's experience of dread |
| "Mad Max: Fury Road is the greatest action film ever made and no one is close." | `hot_take` | 0.91 | Correctly identified: superlative claim with no supporting evidence |
| "Just finished watching Parasite for the third time and I keep noticing new things." | `reaction` | 0.96 | Correctly identified: personal viewing anchor ("third time"), expresses discovery as feeling |
| "Watched 2001 for a film class and the Stargate sequence hit different..." | `hot_take` | 0.36 | **Wrong** — true label is `reaction`; low confidence correctly signals uncertainty |
| "Villeneuve and Deakins use extreme depth of field in 2049 to make K appear small..." | `analysis` | 0.95 | Correctly identified: specific technical mechanism (depth of field) linked to thematic effect (K's identity crisis) |

The correctly predicted `analysis` example above is reasonable because it names a specific cinematographic technique (depth of field, production design choices), identifies the director and cinematographer by name, and explicitly connects the visual choice to the film's thematic argument — all reliable signals of `analysis` in the training data.

---

### Reflection: What the Model Learned vs. What I Intended

The model learned to classify well, but what it learned is not identical to what the labels intended.

What I intended the labels to capture was a distinction about *argumentative structure*: does the post reason from evidence, assert without argument, or express feeling? This is a semantic and logical property.

What the model actually learned is a set of *surface stylistic patterns*: `analysis` posts use specific technical vocabulary and passive constructions ("is used," "encodes," "functions as"); `hot_take` posts use superlatives, comparative constructions ("better than," "best ever"), and named directors without mechanism; `reaction` posts use first-person verbs and temporal anchors ("just watched," "just got back," "finally saw").

These two things are correlated — the stylistic patterns track the argumentative ones — but they are not the same. A post that uses technical vocabulary without genuine reasoning (e.g., a hot take that name-drops cinematography) might fool the model into predicting `analysis`. And a short `analysis` post with no technical vocabulary might be misclassified as `hot_take`. The model learned the symptom of the distinction, not the distinction itself.

This gap is partly a labeling problem (the training data was stylistically consistent within each label, so the model had no pressure to learn the deeper structure) and partly a fundamental limitation of fine-tuning on 157 examples: with more data showing structurally analytical posts in non-technical language, and hot takes that use technical vocabulary, the model would be forced to learn the deeper boundary.

---

## Spec Reflection

**One way the spec helped:** The requirement to write the planning document before touching any code forced me to work out the `hot_take`/`analysis` decision rule in writing before annotating. Without that constraint I would have started labeling immediately and ended up with inconsistent annotations at that boundary. The pre-annotation planning caught the ambiguity early, when it was cheap to resolve.

**One way implementation diverged from the spec:** The spec assumes data collection from a real online community via scraping or manual copy-paste. I used a synthetic dataset instead, due to Reddit's API restrictions making automated collection infeasible within the project timeline. The synthetic approach preserved the project's core learning objectives — label design, annotation review, fine-tuning, and evaluation — while maintaining full disclosure. The dataset reflects authentic r/movies discourse patterns, but does not constitute scraped real posts.

---

## AI Usage

**Instance 1 — Label stress-testing:** I used Claude to generate posts right on the edge between hot_take and analysis so I could pressure‑test my label rules. That helped me realize my original “because = analysis” rule was too loose. I tightened it so the reasoning had to point to an actual mechanism, not just a filler phrase. I updated my plan before annotating anything.

**Instance 2 — Dataset generation:** I had Claude generate 225 posts using my exact label definitions, but I manually reviewed every single one. I caught a few edge cases and documented them, but overall the generation matched my rules, so no relabeling was needed. 

**Instance 3 — Failure pattern analysis:** After generating wrong predictions from the fine-tuned model, I used Claude to identify patterns across the misclassified examples. Then double‑checked the reasoning myself. The mistake came from a post that blended a personal reaction with a general claim in one sentence. I confirmed the explanation and added it to my notes.
