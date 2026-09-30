from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

MASTER = (
    ROOT
    / "datasets"
    / "master"
    / "master_exact_groups.csv"
)

REVIEW = (
    ROOT
    / "datasets"
    / "master"
    / "conflict_review_completed.xlsx"
)

OUTPUT = (
    ROOT
    / "datasets"
    / "master"
    / "master_final.csv"
)


def main():

    print("=" * 70)
    print("APPLYING CONFLICT RESOLUTION")
    print("=" * 70)

    master = pd.read_csv(MASTER)

    review = pd.read_excel(
        REVIEW,
        sheet_name="Conflict Review"
    )

    print(f"Master records: {len(master):,}")
    print(f"Reviewed conflicts: {len(review):,}")

    # -----------------------------------------------------
    # Validate review file
    # -----------------------------------------------------

    required_columns = {
        "message",
        "final_label",
        "review_status"
    }

    missing = required_columns - set(review.columns)

    if missing:
        raise ValueError(
            f"Missing columns in review file: {missing}"
        )

    # Only approved reviewed records
    approved = review[
        review["review_status"].astype(str).str.lower()
        == "approved"
    ].copy()

    print(f"Approved conflict labels: {len(approved):,}")

    if len(approved) != 285:
        raise ValueError(
            f"Expected 285 approved conflicts, "
            f"found {len(approved)}"
        )

    # Check labels
    valid_labels = {
        "benign",
        "spam",
        "smishing"
    }

    invalid = set(
        approved["final_label"]
        .dropna()
        .astype(str)
        .str.lower()
    ) - valid_labels

    if invalid:
        raise ValueError(
            f"Invalid final labels: {invalid}"
        )

    approved["final_label"] = (
        approved["final_label"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # -----------------------------------------------------
    # Make sure every reviewed message exists in master
    # -----------------------------------------------------

    master_messages = set(
        master["message"].astype(str)
    )

    review_messages = set(
        approved["message"].astype(str)
    )

    missing_messages = review_messages - master_messages

    if missing_messages:
        raise ValueError(
            f"{len(missing_messages)} reviewed messages "
            f"are missing from master dataset"
        )

    # -----------------------------------------------------
    # Apply final labels
    # -----------------------------------------------------

    label_map = dict(
        zip(
            approved["message"].astype(str),
            approved["final_label"]
        )
    )

    conflict_mask = (
        master["label_status"] == "conflict"
    )

    print(
        f"Conflict records in master: "
        f"{conflict_mask.sum():,}"
    )

    # Apply reviewed labels
    master.loc[conflict_mask, "label"] = (
        master.loc[conflict_mask, "message"]
        .astype(str)
        .map(label_map)
    )

    # Mark them as resolved
    master.loc[conflict_mask, "label_status"] = (
        "resolved_conflict"
    )

    # -----------------------------------------------------
    # Verify no unresolved conflicts remain
    # -----------------------------------------------------

    unresolved = master[
        master["label_status"] == "conflict"
    ]

    if len(unresolved) != 0:
        raise ValueError(
            f"{len(unresolved)} conflicts remain unresolved"
        )

    # -----------------------------------------------------
    # Final statistics
    # -----------------------------------------------------

    print("\nFinal label distribution:")

    print(
        master["label"]
        .value_counts()
    )

    print(
        f"\nFinal records: "
        f"{len(master):,}"
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    master.to_csv(
        OUTPUT,
        index=False
    )

    print(
        f"\nSaved:\n{OUTPUT}"
    )

    print("\n" + "=" * 70)
    print("CONFLICT RESOLUTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()