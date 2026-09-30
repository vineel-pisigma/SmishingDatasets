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
# Strong SMISHING indicators
# =========================================================

SMISHING_RULES = {

    "credential_phishing": [
        r"\bpassword\b",
        r"\bpasscode\b",
        r"\busername\b",
        r"\bcredentials?\b",
        r"\bverify your identity\b",
        r"\bverify your account\b",
        r"\bconfirm your identity\b",
        r"\bconfirm your account\b",
        r"\baccount verification\b",
    ],

    "banking": [
        r"\bbank account\b",
        r"\baccount has been (?:blocked|locked|suspended|disabled)\b",
        r"\baccount (?:blocked|locked|suspended|disabled)\b",
        r"\bdebit card\b",
        r"\bcredit card\b",
        r"\bbanking\b",
        r"\bonline banking\b",
        r"\bnet banking\b",
    ],

    "payment_fraud": [
        r"\bpayment (?:failed|pending|required|declined)\b",
        r"\bpayment is required\b",
        r"\bpay (?:now|immediately)\b",
        r"\brefund.*(?:claim|verify|confirm)\b",
        r"\btransaction.*(?:failed|blocked|suspended|unauthorized)\b",
    ],

    "otp_security": [
        r"\botp\b",
        r"\bone[- ]time password\b",
        r"\bverification code\b",
        r"\bsecurity code\b",
        r"\bsecurity pin\b",
        r"\bpin\b",
    ],

    "account_threat": [
        r"\baccount.*(?:suspended|blocked|locked|closed)\b",
        r"\baccount.*(?:will be|has been).*(?:closed|suspended|blocked)\b",
        r"\bunauthorized.*(?:login|access|transaction)\b",
        r"\bsuspicious activity\b",
        r"\bsecurity alert\b",
    ],

    "phishing_link": [
        r"\bclick (?:here|the link)\b",
        r"\bclick.*(?:link|url)\b",
        r"\bverify.*https?://",
        r"\bconfirm.*https?://",
        r"\bupdate.*https?://",
        r"\bhttp://",
        r"\bhttps://",
        r"\bwww\.",
    ],

    "delivery_scam": [
        r"\bparcel\b.*(?:payment|fee|pay|verify)",
        r"\bpackage\b.*(?:payment|fee|pay|verify)",
        r"\bdelivery\b.*(?:payment|fee|pay|verify)",
        r"\bcourier\b.*(?:payment|fee|pay|verify)",
        r"\bcustoms\b.*(?:payment|fee|pay)",
    ],

    "tax_invoice_scam": [
        r"\btax.*(?:payment|refund|verify)\b",
        r"\binvoice.*(?:payment|pay|verify)\b",
        r"\boutstanding.*(?:payment|balance|amount)\b",
    ],
}


# =========================================================
# Strong SPAM indicators
# =========================================================

SPAM_RULES = {

    "premium_rate": [
        r"\b\d+\s*p(?:pm)?\b",
        r"\b\d+\.\d+\s*p(?:pm)?\b",
        r"\bpremium rate\b",
        r"\bpremium-rate\b",
        r"\bper msg\b",
        r"\bper message\b",
        r"\bcharged.*(?:msg|message)\b",
        r"\b\d+p\s*/\s*msg\b",
    ],

    "subscription": [
        r"\bsubscribe\b",
        r"\bsubscription\b",
        r"\bunsub(?:scribe)?\b",
        r"\bunsubscribe\b",
        r"\btxt\s+stop\b",
        r"\btext\s+stop\b",
        r"\breply\s+stop\b",
        r"\bto opt out\b",
        r"\bopt out\b",
    ],

    "promotion": [
        r"\bdiscount\b",
        r"\bpromotion\b",
        r"\bpromotional\b",
        r"\bspecial offer\b",
        r"\bspecial offers\b",
        r"\bexclusive offer\b",
        r"\bdeal\b",
        r"\bsale\b",
        r"\boffer\b",
        r"\bfree ringtone\b",
        r"\bfree tones\b",
        r"\bpolyphonic tones?\b",
        r"\bmobile tones?\b",
    ],

    "competition_prize": [
        r"\bcompetition\b",
        r"\bprize\b",
        r"\bprize draw\b",
        r"\bcompetition draw\b",
        r"\bbonus caller prize\b",
        r"\byou have won\b",
        r"\byou've won\b",
        r"\byou won\b",
        r"\bcongratulations\b",
        r"\bcongrats\b",
        r"\bselected to (?:receive|win)\b",
        r"\bselected.*award\b",
        r"\bclaim code\b",
    ],

    "marketing": [
        r"\bbuy now\b",
        r"\border now\b",
        r"\bshop now\b",
        r"\bnew customers?\b",
        r"\bcustomer offer\b",
        r"\bjoin today\b",
        r"\bcall now\b",
        r"\bget yours\b",
    ],

    "entertainment_services": [
        r"\bmovie club\b",
        r"\bmobile club\b",
        r"\bchat service\b",
        r"\bdating service\b",
        r"\btones?\b",
        r"\bgames?\b.*(?:weekly|subscribe|subscription)",
    ],
}


# =========================================================
# Helpers
# =========================================================

def matched_categories(text, rules):

    matches = []

    for category, patterns in rules.items():

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            ):
                matches.append(category)
                break

    return matches


def contains_url(text):

    return bool(
        re.search(
            r"https?://|www\.",
            text,
            flags=re.IGNORECASE
        )
    )


def classify_message(message):

    text = str(message).strip()

    smishing_matches = matched_categories(
        text,
        SMISHING_RULES
    )

    spam_matches = matched_categories(
        text,
        SPAM_RULES
    )

    # -----------------------------------------------------
    # Strong evidence
    # -----------------------------------------------------

    strong_smishing_categories = {
        "credential_phishing",
        "banking",
        "payment_fraud",
        "otp_security",
        "account_threat",
        "delivery_scam",
        "tax_invoice_scam",
    }

    strong_spam_categories = {
        "premium_rate",
        "subscription",
        "promotion",
        "competition_prize",
        "entertainment_services",
    }

    strong_smishing = bool(
        set(smishing_matches)
        & strong_smishing_categories
    )

    strong_spam = bool(
        set(spam_matches)
        & strong_spam_categories
    )

    # -----------------------------------------------------
    # Priority rules
    # -----------------------------------------------------

    # 1. Clear credential/account/payment phishing
    if strong_smishing:

        # If it is primarily an actual phishing/security
        # event, classify as smishing.
        return (
            "smishing",
            "strong_smishing",
            smishing_matches,
            spam_matches
        )

    # 2. Clear commercial/premium/prize messaging
    if strong_spam:

        # Prize/competition messages in this conflict set
        # are treated as spam unless they also contain a
        # strong phishing indicator above.
        return (
            "spam",
            "strong_spam",
            smishing_matches,
            spam_matches
        )

    # 3. Link alone is NOT enough.
    # A URL can occur in ordinary spam.
    if contains_url(text):

        return (
            "review",
            "url_without_clear_intent",
            smishing_matches,
            spam_matches
        )

    # 4. Weak evidence
    if smishing_matches or spam_matches:

        return (
            "review",
            "weak_or_mixed_evidence",
            smishing_matches,
            spam_matches
        )

    # 5. No useful evidence
    return (
        "review",
        "no_clear_indicator",
        smishing_matches,
        spam_matches
    )


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 70)
    print("CONFLICT CLASSIFICATION V2")
    print("=" * 70)

    df = pd.read_csv(INPUT)

    print(f"Input conflicts: {len(df):,}")

    results = []

    for _, row in df.iterrows():

        (
            suggested_label,
            reason,
            smishing_matches,
            spam_matches
        ) = classify_message(
            row["message"]
        )

        results.append({
            "message": row["message"],
            "labels_found": row["labels_found"],
            "sources": row["sources"],
            "record_count": row["record_count"],

            "suggested_label": suggested_label,
            "reason": reason,

            "smishing_indicators":
                "|".join(smishing_matches),

            "spam_indicators":
                "|".join(spam_matches),

            # Leave blank until final human/rule review
            "final_label": "",
        })

    result = pd.DataFrame(results)

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\nSuggested labels:")

    print(
        result["suggested_label"]
        .value_counts()
    )

    print("\nReasons:")

    print(
        result["reason"]
        .value_counts()
    )

    # -----------------------------------------------------
    # Save complete analysis
    # -----------------------------------------------------

    output = (
        OUTPUT_DIR
        / "conflict_analysis_v2.csv"
    )

    result.to_csv(
        output,
        index=False
    )

    print(
        f"\nSaved:\n{output}"
    )

    # -----------------------------------------------------
    # Save review set
    # -----------------------------------------------------

    review = result[
        result["suggested_label"] == "review"
    ].copy()

    review_output = (
        OUTPUT_DIR
        / "conflict_review_v2.csv"
    )

    review.to_csv(
        review_output,
        index=False
    )

    print(
        f"Review messages: "
        f"{len(review):,}"
    )

    print(
        f"Review file:\n{review_output}"
    )

    # -----------------------------------------------------
    # Display examples
    # -----------------------------------------------------

    for label in [
        "smishing",
        "spam",
        "review"
    ]:

        subset = result[
            result["suggested_label"] == label
        ].head(5)

        print("\n" + "=" * 70)
        print(label.upper())

        for _, row in subset.iterrows():

            print("-" * 70)
            print(row["message"])

            print(
                f"Reason: {row['reason']}"
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
    print("CONFLICT CLASSIFICATION V2 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()