from pathlib import Path
import pandas as pd
import re
from langdetect import detect, LangDetectException

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "datasets" / "master" / "master_final.csv"
OUTPUT = ROOT / "datasets" / "master" / "data_quality_audit.csv"


def normalize_basic(text):
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_language(text):
    try:
        return detect(str(text))
    except LangDetectException:
        return "unknown"
    except Exception:
        return "unknown"


df = pd.read_csv(INPUT)

print("=" * 70)
print("DATA QUALITY AUDIT")
print("=" * 70)

print(f"Total records: {len(df):,}")
print()

# ---------------------------------------------------------
# Basic checks
# ---------------------------------------------------------

df["message_length"] = df["message"].astype(str).str.len()
df["word_count"] = df["message"].astype(str).str.split().str.len()

df["has_replacement_char"] = df["message"].astype(str).str.contains(
    "\ufffd",
    regex=False
)

df["has_url"] = df["message"].astype(str).str.contains(
    r"(https?://|www\.|bit\.ly|tinyurl|t\.co/)",
    case=False,
    regex=True
)

df["has_phone_number"] = df["message"].astype(str).str.contains(
    r"\+?\d[\d\s().-]{7,}\d",
    regex=True
)

df["normalized_message"] = (
    df["message"]
    .astype(str)
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# ---------------------------------------------------------
# Language detection
# ---------------------------------------------------------

print("Detecting languages...")
df["language"] = df["message"].apply(detect_language)

# ---------------------------------------------------------
# Print summary
# ---------------------------------------------------------

print("\nLABEL DISTRIBUTION")
print(df["label"].value_counts())

print("\nMESSAGE LENGTH")
print(df["message_length"].describe())

print("\nWORD COUNT")
print(df["word_count"].describe())

print("\nREPLACEMENT CHARACTER")
print(df["has_replacement_char"].value_counts())

print("\nURL")
print(df["has_url"].value_counts())

print("\nPHONE NUMBER")
print(df["has_phone_number"].value_counts())

print("\nLANGUAGE DISTRIBUTION")
print(df["language"].value_counts().head(20))

# ---------------------------------------------------------
# Very short messages
# ---------------------------------------------------------

short = df[df["message_length"] < 5]

print("\nVERY SHORT MESSAGES (<5 characters)")
print(f"Count: {len(short):,}")

if len(short):
    print(
        short[
            ["message", "label", "sources"]
        ].head(30).to_string(index=False)
    )

# ---------------------------------------------------------
# Replacement characters
# ---------------------------------------------------------

bad_encoding = df[df["has_replacement_char"]]

print("\nMESSAGES WITH REPLACEMENT CHARACTER ( )")
print(f"Count: {len(bad_encoding):,}")

if len(bad_encoding):
    print(
        bad_encoding[
            ["message", "label", "sources"]
        ].head(30).to_string(index=False)
    )

# ---------------------------------------------------------
# Non-English candidates
# ---------------------------------------------------------

non_english = df[
    ~df["language"].isin(["en", "unknown"])
]

print("\nNON-ENGLISH CANDIDATES")
print(f"Count: {len(non_english):,}")

if len(non_english):
    print(
        non_english[
            ["message", "label", "language", "sources"]
        ].head(50).to_string(index=False)
    )

# ---------------------------------------------------------
# Normalized duplicates
# ---------------------------------------------------------

normalized_counts = df["normalized_message"].value_counts()

normalized_duplicates = normalized_counts[
    normalized_counts > 1
]

print("\nNORMALIZED DUPLICATE GROUPS")
print(f"Groups: {len(normalized_duplicates):,}")
print(
    f"Records involved: "
    f"{normalized_duplicates.sum():,}"
)

# ---------------------------------------------------------
# Suspiciously long messages
# ---------------------------------------------------------

long_messages = df[df["message_length"] > 1000]

print("\nVERY LONG MESSAGES (>1000 characters)")
print(f"Count: {len(long_messages):,}")

if len(long_messages):
    print(
        long_messages[
            ["message", "label", "message_length", "sources"]
        ].head(20).to_string(index=False)
    )

# ---------------------------------------------------------
# Save audit dataset
# ---------------------------------------------------------

audit_columns = [
    "message",
    "label",
    "label_status",
    "sources",
    "source_count",
    "record_count",
    "message_length",
    "word_count",
    "has_replacement_char",
    "has_url",
    "has_phone_number",
    "language",
    "normalized_message",
]

df[audit_columns].to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8"
)

print()
print("=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
print(f"Saved: {OUTPUT}")