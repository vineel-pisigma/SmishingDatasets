from pathlib import Path
import csv
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

EXTRACTED = ROOT / "datasets" / "extracted"
PROCESSED = ROOT / "datasets" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Mendeley
# ---------------------------------------------------------

def process_mendeley():
    path = EXTRACTED / "mendeley" / "Dataset_5971.csv"

    df = pd.read_csv(path)

    df = df.rename(columns={
        "TEXT": "message",
        "LABEL": "original_label"
    })

    result = pd.DataFrame({
        "message": df["message"].astype(str).str.strip(),
        "original_label": df["original_label"].astype(str).str.strip().str.lower(),
        "source": "mendeley",
        "source_id": range(len(df))
    })

    result["label"] = result["original_label"].map({
        "ham": "benign",
        "spam": "spam",
        "smishing": "smishing"
    })

    result = result[
        ["message", "label", "original_label", "source", "source_id"]
    ]

    output = PROCESSED / "mendeley_clean.csv"
    result.to_csv(output, index=False)

    print(f"\nMendeley: {len(result):,} records")
    print(result["label"].value_counts(dropna=False))
    print(f"Saved: {output}")


# ---------------------------------------------------------
# UCI
# ---------------------------------------------------------

def process_uci():
    path = EXTRACTED / "uci" / "SMSSpamCollection"

    rows = []

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line_number, line in enumerate(f, 1):

            line = line.rstrip("\r\n")

            if not line:
                continue

            parts = line.split("\t", 1)

            if len(parts) != 2:
                print(f"Skipping malformed UCI line: {line_number}")
                continue

            label, message = parts

            label = label.strip().lower()
            message = message.strip()

            if not message:
                continue

            rows.append({
                "message": message,
                "label": "benign" if label == "ham" else "spam",
                "original_label": label,
                "source": "uci",
                "source_id": line_number
            })

    result = pd.DataFrame(rows)

    output = PROCESSED / "uci_clean.csv"
    result.to_csv(output, index=False)

    print(f"\nUCI: {len(result):,} records")
    print(result["label"].value_counts(dropna=False))
    print(f"Saved: {output}")


# ---------------------------------------------------------
# NCSU
# ---------------------------------------------------------

def process_ncsu():
    path = (
        EXTRACTED
        / "ncsu"
        / "sms-phishing-main"
        / "phishing_messages.csv"
    )

    rows = []

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.reader(f)

        # Skip header
        next(reader)

        for row_number, row in enumerate(reader, 1):

            if len(row) != 7:
                print(
                    f"Skipping malformed NCSU row "
                    f"{row_number}: {len(row)} fields"
                )
                continue

            # Actual NCSU structure:
            #
            # row[0] = row/index
            # row[1] = messageID
            # row[2] = destination number
            # row[3] = message
            # row[4] = sender
            # row[5] = time
            # row[6] = error in time

            row_index = row[0].strip()
            message_id = row[1].strip()
            destination_number = row[2].strip()
            message = row[3].strip()
            sender = row[4].strip()
            time = row[5].strip()
            error_in_time = row[6].strip()

            if not message:
                continue

            rows.append({
                "message": message,
                "label": "smishing",
                "original_label": "phishing",
                "source": "ncsu",
                "source_id": message_id
            })

    result = pd.DataFrame(rows)

    output = PROCESSED / "ncsu_clean.csv"
    result.to_csv(output, index=False)

    print(f"\nNCSU: {len(result):,} records")
    print(result["label"].value_counts(dropna=False))
    print(f"Saved: {output}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("STANDARDIZING DATASETS")
    print("=" * 70)

    process_mendeley()
    process_uci()
    process_ncsu()

    print("\n" + "=" * 70)
    print("STANDARDIZATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()