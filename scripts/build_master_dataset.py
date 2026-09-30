from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

PROCESSED = ROOT / "datasets" / "processed"
OUTPUT = ROOT / "datasets" / "master"

OUTPUT.mkdir(parents=True, exist_ok=True)


FILES = [
    PROCESSED / "mendeley_clean.csv",
    PROCESSED / "ncsu_clean.csv",
    PROCESSED / "uci_clean.csv",
]


def main():

    print("=" * 70)
    print("BUILDING MASTER DATASET")
    print("=" * 70)

    # -----------------------------------------------------
    # Load standardized datasets
    # -----------------------------------------------------

    frames = []

    for path in FILES:
        df = pd.read_csv(path)

        print(f"{path.name}: {len(df):,}")

        frames.append(df)

    df = pd.concat(frames, ignore_index=True)

    print(f"\nRaw standardized records: {len(df):,}")

    # -----------------------------------------------------
    # Basic cleanup
    # -----------------------------------------------------

    df["message"] = (
        df["message"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df = df[df["message"] != ""].copy()

    # -----------------------------------------------------
    # Group exact messages
    # -----------------------------------------------------

    grouped = (
        df.groupby("message", sort=False)
    )

    records = []

    for message, group in grouped:

        labels = sorted(
            group["label"]
            .dropna()
            .unique()
            .tolist()
        )

        sources = sorted(
            group["source"]
            .dropna()
            .unique()
            .tolist()
        )

        # -------------------------------------------------
        # Determine label status
        # -------------------------------------------------

        if len(labels) == 1:
            resolved_label = labels[0]
            label_status = "consistent"
        else:
            resolved_label = "conflict"
            label_status = "conflict"

        # -------------------------------------------------
        # Preserve all source information
        # -------------------------------------------------

        records.append({
            "message": message,

            "label": resolved_label,

            "label_status": label_status,

            "labels_found": "|".join(labels),

            "sources": "|".join(sources),

            "source_count": len(sources),

            "record_count": len(group),

            "source_ids": "|".join(
                group["source_id"]
                .astype(str)
                .tolist()
            ),
        })

    master = pd.DataFrame(records)

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    print(
        f"\nUnique messages: "
        f"{len(master):,}"
    )

    print("\nLabel status:")

    print(
        master["label_status"]
        .value_counts()
    )

    print("\nResolved label distribution:")

    print(
        master[
            master["label_status"] == "consistent"
        ]["label"]
        .value_counts()
    )

    conflicts = master[
        master["label_status"] == "conflict"
    ]

    print(
        f"\nConflicting unique messages: "
        f"{len(conflicts):,}"
    )

    print("\nConflict combinations:")

    print(
        conflicts["labels_found"]
        .value_counts()
    )

    # -----------------------------------------------------
    # Save master dataset
    # -----------------------------------------------------

    master_path = (
        OUTPUT / "master_exact_groups.csv"
    )

    master.to_csv(
        master_path,
        index=False
    )

    # -----------------------------------------------------
    # Save conflict-only dataset
    # -----------------------------------------------------

    conflict_path = (
        OUTPUT / "label_conflicts.csv"
    )

    conflicts.to_csv(
        conflict_path,
        index=False
    )

    print(
        f"\nMaster dataset saved:"
        f"\n{master_path}"
    )

    print(
        f"\nConflict dataset saved:"
        f"\n{conflict_path}"
    )

    print("\n" + "=" * 70)
    print("MASTER DATASET CREATED")
    print("=" * 70)


if __name__ == "__main__":
    main()