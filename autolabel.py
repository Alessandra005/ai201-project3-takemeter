"""
autolabel.py — Pre-label r/movies posts using Groq (llama-3.3-70b-versatile)
for TakeMeter. You review and correct every label before training.

Usage:
    pip install groq
    export GROQ_API_KEY="your_key_here"   # or set it in the script below
    python autolabel.py

Input:  reddit_raw.csv   (from scrape_reddit.py)
Output: dataset_prelabeled.csv  — has label + prelabeled columns
        You then review this file, correct labels, and save as dataset.csv
"""

import csv
import os
import time
import json

try:
    from groq import Groq
except ImportError:
    print("Install groq first:  pip install groq")
    raise

# ── Config ────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")  # Set via env var
INPUT_FILE   = "reddit_raw.csv"
OUTPUT_FILE  = "dataset_prelabeled.csv"
MODEL        = "llama-3.3-70b-versatile"
MAX_ROWS     = 280  # Collect a buffer above 200 minimum

SYSTEM_PROMPT = """You are a precise text classifier for an r/movies discourse quality study.

You will classify each Reddit post into EXACTLY ONE of these three labels:

analysis — The post makes a structured argument about a film, director, genre, or industry trend, supported by specific evidence: plot details, cinematographic observations, historical comparisons, box office data, or references to other works. The core claim would be weakened if you removed the supporting reasoning.

hot_take — A bold, confident opinion stated without supporting evidence or with only superficial justification. The claim may be defensible but the post asserts rather than argues. The framing is often provocative or contrarian. Short opinions, superlative claims ("best/worst ever"), and contrarian positions without argument belong here.

reaction — An immediate emotional response to a specific film, trailer, casting announcement, or industry event. Little to no argument — the post expresses a feeling in the moment. Posts anchored to a recent personal event ("just watched," "first time seeing," "saw it last night") or to fresh news belong here.

DECISION RULES FOR EDGE CASES:
- If a post names a specific structural/technical mechanism AND explains the effect it produces → analysis (even if it starts with a bold opinion)
- If the "reasoning" is one clause that decorates an opinion without genuinely supporting it → hot_take
- If the post is explicitly anchored to a recent personal viewing or news event AND expresses feeling rather than claim → reaction

OUTPUT FORMAT: Respond with ONLY the label name, nothing else. One of: analysis, hot_take, reaction"""

USER_TEMPLATE = "Classify this r/movies post:\n\n{text}"

# ── Main ──────────────────────────────────────────────────────────────────────

def classify(client, text):
    """Call Groq and return the label string, or None on failure."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_TEMPLATE.format(text=text[:800])},
            ],
            temperature=0,
            max_tokens=10,
        )
        raw = response.choices[0].message.content.strip().lower()
        # Clean up any stray punctuation
        label = raw.strip(".,!?:\"'")
        if label in ("analysis", "hot_take", "reaction"):
            return label
        # Try to recover partial matches
        for valid in ("analysis", "hot_take", "reaction"):
            if valid in label:
                return valid
        return None
    except Exception as e:
        print(f"    API error: {e}")
        return None


def main():
    if not GROQ_API_KEY:
        raise ValueError(
            "Set your Groq API key:\n"
            "  export GROQ_API_KEY='your_key_here'\n"
            "or paste it directly into the GROQ_API_KEY variable at the top of this file."
        )

    client = Groq(api_key=GROQ_API_KEY)

    # Load raw posts
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Cap to MAX_ROWS
    rows = rows[:MAX_ROWS]
    print(f"Loaded {len(rows)} posts from {INPUT_FILE}")

    results = []
    failed = 0
    label_counts = {"analysis": 0, "hot_take": 0, "reaction": 0, "failed": 0}

    for i, row in enumerate(rows):
        text = row.get("text", "").strip()
        if not text:
            continue

        label = classify(client, text)

        if label is None:
            failed += 1
            label_counts["failed"] += 1
            label = "REVIEW"  # Flag for manual review
        else:
            label_counts[label] += 1

        results.append({
            "text": text,
            "label": label,         # Pre-assigned label — YOU MUST REVIEW THIS
            "prelabeled": "yes",    # Tracks that this was pre-labeled by AI
            "original_title": row.get("title", ""),
            "source_url": row.get("url", ""),
            "notes": "",            # Fill in during your review for edge cases
        })

        # Progress
        if (i + 1) % 25 == 0:
            print(f"  [{i+1}/{len(rows)}] — {label_counts}")

        time.sleep(0.3)  # Avoid rate limits

    # Save
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["text", "label", "prelabeled", "original_title", "source_url", "notes"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\n{'='*50}")
    print(f"Done. {len(results)} posts saved to {OUTPUT_FILE}")
    print(f"Label distribution: {label_counts}")
    if failed > 0:
        print(f"⚠️  {failed} posts got 'REVIEW' label — check those manually")

    # Distribution check
    total = len(results)
    for label, count in label_counts.items():
        if label == "failed":
            continue
        pct = count / total * 100
        if pct > 70:
            print(f"\n⚠️  WARNING: '{label}' is {pct:.0f}% of dataset — collect more of the others!")
        elif pct < 15:
            print(f"\n⚠️  WARNING: '{label}' is only {pct:.0f}% of dataset — needs more examples!")

    print(f"""
{'='*50}
NEXT STEPS:
1. Open {OUTPUT_FILE} in a spreadsheet (Excel / Google Sheets)
2. Read EVERY row and correct any wrong 'label' values
3. For edge cases, fill in the 'notes' column with your reasoning
4. When done, save as  dataset.csv  (the notebook expects this filename)
5. Aim for no label above 70% of total — re-collect if needed
6. Keep the 'prelabeled' column — you'll disclose this in your README
""")


if __name__ == "__main__":
    main()
