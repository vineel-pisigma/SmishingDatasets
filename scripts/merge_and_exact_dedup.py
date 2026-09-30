from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

PROCESSED = ROOT / "datasets" / "processed"
OUTPUT = ROOT / "datasets" / "merged"

OUTPUT.mkdir(parents=True, exist_ok=True)


FILES = [
    PROCESSED / "mendeley_clean.csv",
    PROCESSED / "ncsu_clean.csv",
    PROCESSED / "uci_clean.csv",
]


def main():

    print("=" * 70)
    print("MERGING DATASETS")
    print("=" * 70)

    frames = []

    for path in FILES:
        df = pd.read_csv(path)

        print(f"{path.name}: {len(df):,}")

        frames.append(df)

    df = pd.concat(frames, ignore_index=True)

    print(f"\nMerged records: {len(df):,}")

    # -----------------------------------------------------
    # Basic cleanup
    # -----------------------------------------------------

    df["message"] = (
        df["message"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Remove completely empty messages
    before_empty = len(df)

    df = df[df["message"] != ""].copy()

    print(
        f"Empty messages removed: "
        f"{before_empty - len(df):,}"
    )

    # -----------------------------------------------------
    # Exact duplicate detection
    # -----------------------------------------------------

    df["message_exact"] = df["message"]

    duplicate_mask = df.duplicated(
        subset=["message_exact"],
        keep=False
    )

    duplicate_rows = df[duplicate_mask].copy()

    print(
        f"\nRecords belonging to exact-duplicate groups: "
        f"{len(duplicate_rows):,}"
    )

    print(
        f"Unique messages before exact deduplication: "
        f"{df['message_exact'].nunique():,}"
    )

    # -----------------------------------------------------
    # Check label conflicts
    # -----------------------------------------------------

    label_counts = (
        duplicate_rows
        .groupby("message_exact")["label"]
        .nunique()
    )

    conflicting_messages = label_counts[
        label_counts > 1
    ]

    print(
        f"Exact duplicate messages with conflicting labels: "
        f"{len(conflicting_messages):,}"
    )

    # -----------------------------------------------------
    # Save duplicate report
    # -----------------------------------------------------

    duplicate_report = (
        duplicate_rows
        .sort_values("message_exact")
    )

    duplicate_report.to_csv(
        OUTPUT / "exact_duplicates.csv",
        index=False
    )

    # -----------------------------------------------------
    # Keep first occurrence
    # -----------------------------------------------------

    deduped = df.drop_duplicates(
        subset=["message_exact"],
        keep="first"
    ).copy()

    # Remove helper column
    deduped = deduped.drop(
        columns=["message_exact"]
    )

    print(
        f"\nRecords after exact deduplication: "
        f"{len(deduped):,}"
    )

    print(
        f"Exact duplicates removed: "
        f"{len(df) - len(deduped):,}"
    )

    # -----------------------------------------------------
    # Label distribution
    # -----------------------------------------------------

    print("\nFinal label distribution:")
    print(deduped["label"].value_counts())

    # -----------------------------------------------------
    # Source distribution
    # -----------------------------------------------------

    print("\nFinal source distribution:")
    print(deduped["source"].value_counts())

    # -----------------------------------------------------
    # Save merged dataset
    # -----------------------------------------------------

    output = OUTPUT / "merged_exact_dedup.csv"

    deduped.to_csv(
        output,
        index=False
    )

    print(f"\nSaved: {output}")

    print("=" * 70)
    print("EXACT DEDUPLICATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()