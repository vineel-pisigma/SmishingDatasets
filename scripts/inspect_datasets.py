from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / "datasets" / "extracted"


def inspect_csv(path: Path, name: str):
    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)
    print(f"File: {path}")

    df = pd.read_csv(path)

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for col in df.columns:
        print(f"  - {col}")

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    print("\nMissing values:")
    print(df.isna().sum().to_string())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())


def inspect_uci(path: Path):
    print("\n" + "=" * 70)
    print("UCI SMS SPAM COLLECTION")
    print("=" * 70)

    rows = []

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line_number, line in enumerate(f, 1):
            line = line.rstrip("\n\r")

            if not line:
                continue

            parts = line.split("\t", 1)

            if len(parts) != 2:
                print(f"WARNING: malformed line {line_number}")
                continue

            label, message = parts
            rows.append((label, message))

    df = pd.DataFrame(rows, columns=["label", "message"])

    print(f"\nRows: {len(df):,}")

    print("\nLabels:")
    print(df["label"].value_counts().to_string())

    print("\nMissing values:")
    print(df.isna().sum().to_string())

    print("\nDuplicate messages:")
    print(df["message"].duplicated().sum())

    print("\nExamples:")
    print(df.head(10).to_string(index=False))


def main():
    # ---------------------------------------------------------
    # Mendeley
    # ---------------------------------------------------------

    mendeley = DATASETS / "mendeley" / "Dataset_5971.csv"

    inspect_csv(
        mendeley,
        "MENDELEY SMS PHISHING DATASET"
    )

    # ---------------------------------------------------------
    # NCSU
    # ---------------------------------------------------------

    ncsu_messages = (
        DATASETS
        / "ncsu"
        / "sms-phishing-main"
        / "phishing_messages.csv"
    )

    ncsu_campaigns = (
        DATASETS
        / "ncsu"
        / "sms-phishing-main"
        / "phishing_campaigns.csv"
    )

    inspect_csv(
        ncsu_messages,
        "NCSU PHISHING MESSAGES"
    )

    inspect_csv(
        ncsu_campaigns,
        "NCSU PHISHING CAMPAIGNS"
    )

    # ---------------------------------------------------------
    # UCI
    # ---------------------------------------------------------

    uci = (
        DATASETS
        / "uci"
        / "SMSSpamCollection"
    )

    inspect_uci(uci)


if __name__ == "__main__":
    main()