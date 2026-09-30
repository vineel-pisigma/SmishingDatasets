from pathlib import Path
import re
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

INPUT = (
    ROOT
    / "datasets"
    / "master"
    / "label_conflicts.csv"
)

OUTPUT_DIR = ROOT / "datasets" / "master"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# Indicator patterns
# =========================================================

SMISHING_PATTERNS = {
    "credential/account": [
        r"\baccount\b",
        r"\blogin\b",
        r"\blog[- ]?in\b",
        r"\bpassword\b",
        r"\busername\b",
        r"\bverify\b",
        r"\bverification\b",
        r"\bidentity\b",
        r"\bsecurity alert\b",
        r"\baccount.*(?:blocked|locked|suspended|disabled)\b",
    ],

    "bank/payment": [
        r"\bbank\b",
        r"\bpayment\b",
        r"\btransaction\b",
        r"\bcard\b",
        r"\bcredit card\b",
        r"\bdebit card\b",
        r"\bwallet\b",
        r"\binvoice\b",
        r"\btax\b",
        r"\brefund\b",
        r"\bpay\b",
        r"\bpayment.*(?:required|failed|pending)\b",
    ],

    "otp/security": [
        r"\botp\b",
        r"\bone[- ]?time password\b",
        r"\bsecurity code\b",
        r"\bverification code\b",
        r"\bpasscode\b",
        r"\bpin\b",
    ],

    "delivery/service impersonation": [
        r"\bdelivery\b",
        r"\bparcel\b",
        r"\bpackage\b",
        r"\bcourier\b",
        r"\bshipment\b",
        r"\bcustoms\b",
        r"\bpost\b",
    ],

    "urgency": [
        r"\burgent\b",
        r"\bimmediately\b",
        r"\basap\b",
        r"\baction required\b",
        r"\bwithin \d+\b",
        r"\bexpires?\b",
        r"\bfinal notice\b",
    ],

    "links": [
        r"https?://",
        r"\bwww\.",
        r"\.com\b",
        r"\.net\b",
        r"\.org\b",
    ],

    "click/action": [
        r"\bclick\b",
        r"\btap\b",
        r"\bvisit\b",
        r"\bopen\b",
        r"\bconfirm\b",
        r"\bupdate\b",
        r"\bactivate\b",
    ],
}


SPAM_PATTERNS = {
    "promotion": [
        r"\boffer\b",
        r"\bdiscount\b",
        r"\bsale\b",
        r"\bpromo(?:tion)?\b",
        r"\bdeal\b",
        r"\bspecial offer\b",
        r"\bfree\b",
    ],

    "subscription": [
        r"\bsubscribe\b",
        r"\bunsubscribe\b",
        r"\bsubscription\b",
        r"\btxt\s*stop\b",
        r"\btext\s*stop\b",
        r"\bstop\s+to\b",
    ],

    "marketing": [
        r"\bbuy\b",
        r"\border now\b",
        r"\bshop\b",
        r"\bshopping\b",
        r"\bnew customer\b",
        r"\bcustomer offer\b",
    ],

    "premium_rate": [
        r"\bpremium\b",
        r"\b150p\b",
        r"\b150ppm\b",
        r"\bper\s*msg\b",
        r"\bper\s*message\b",
        r"\bcharged\b",
        r"\brate\b",
    ],

    "competition/prize": [
        r"\bcompetition\b",
        r"\bcongratulations\b",
        r"\bcongrats\b",
        r"\byou have won\b",
        r"\byou've won\b",
        r"\bwon\b",
        r"\bprize\b",
        r"\bcash prize\b",
    ],
}


# =========================================================
# Scoring
# =========================================================

def find_matches(text, patterns):
    matches = []

    for category, regexes in patterns.items():

        category_matches = []

        for pattern in regexes:
            if re.search(pattern, text, flags=re.IGNORECASE):
                category_matches.append(pattern)

        if category_matches:
            matches.append(category)

    return matches


def analyze_message(message):

    text = str(message).lower()

    smishing_matches = find_matches(
        text,
        SMISHING_PATTERNS
    )

    spam_matches = find_matches(
        text,
        SPAM_PATTERNS
    )

    # -----------------------------------------------------
    # Score categories
    # -----------------------------------------------------

    smishing_score = 0
    spam_score = 0

    # Strong indicators
    strong_smishing = {
        "credential/account",
        "bank/payment",
        "otp/security",
    }

    strong_spam = {
        "subscription",
        "marketing",
        "premium_rate",
    }

    for category in smishing_matches:

        if category in strong_smishing:
            smishing_score += 3
        elif category in {"links", "click/action"}:
            smishing_score += 2
        else:
            smishing_score += 1

    for category in spam_matches:

        if category in strong_spam:
            spam_score += 3
        elif category in {"promotion", "marketing"}:
            spam_score += 2
        else:
            spam_score += 1

    # -----------------------------------------------------
    # Determine suggestion
    # -----------------------------------------------------

    if smishing_score >= spam_score + 3:
        suggestion = "likely_smishing"

    elif spam_score >= smishing_score + 3:
        suggestion = "likely_spam"

    else:
        suggestion = "ambiguous"

    return (
        smishing_score,
        spam_score,
        suggestion,
        smishing_matches,
        spam_matches,
    )


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 70)
    print("SMISHING vs SPAM CONFLICT ANALYSIS")
    print("=" * 70)

    df = pd.read_csv(INPUT)

    print(f"Conflict records: {len(df):,}")

    results = []

    for _, row in df.iterrows():

        (
            smishing_score,
            spam_score,
            suggestion,
            smishing_matches,
            spam_matches,
        ) = analyze_message(row["message"])

        results.append({
            "message": row["message"],
            "labels_found": row["labels_found"],
            "sources": row["sources"],
            "record_count": row["record_count"],

            "smishing_score": smishing_score,
            "spam_score": spam_score,

            "suggestion": suggestion,

            "smishing_indicators":
                "|".join(smishing_matches),

            "spam_indicators":
                "|".join(spam_matches),
        })

    result = pd.DataFrame(results)

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\nSuggested categories:")

    print(
        result["suggestion"]
        .value_counts()
    )

    print("\nScore comparison:")

    print(
        result[
            [
                "smishing_score",
                "spam_score"
            ]
        ]
        .value_counts()
        .sort_index()
    )

    # -----------------------------------------------------
    # Save full analysis
    # -----------------------------------------------------

    output = (
        OUTPUT_DIR
        / "conflict_analysis.csv"
    )

    result.to_csv(
        output,
        index=False
    )

    print(
        f"\nSaved:\n{output}"
    )

    # -----------------------------------------------------
    # Save ambiguous messages separately
    # -----------------------------------------------------

    ambiguous = result[
        result["suggestion"] == "ambiguous"
    ].copy()

    ambiguous_output = (
        OUTPUT_DIR
        / "conflict_ambiguous.csv"
    )

    ambiguous.to_csv(
        ambiguous_output,
        index=False
    )

    print(
        f"Ambiguous messages saved:\n"
        f"{ambiguous_output}"
    )

    # -----------------------------------------------------
    # Show examples
    # -----------------------------------------------------

    print("\nExamples:\n")

    for suggestion in [
        "likely_smishing",
        "likely_spam",
        "ambiguous",
    ]:

        subset = result[
            result["suggestion"] == suggestion
        ].head(3)

        print("=" * 70)
        print(suggestion.upper())

        for _, row in subset.iterrows():

            print("-" * 70)
            print(row["message"])
            print(
                f"Smishing score: "
                f"{row['smishing_score']}"
            )
            print(
                f"Spam score: "
                f"{row['spam_score']}"
            )
            print(
                f"Smishing indicators: "
                f"{row['smishing_indicators']}"
            )
            print(
                f"Spam indicators: "
                f"{row['spam_indicators']}"
            )

    print("\n" + "=" * 70)
    print("CONFLICT ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()