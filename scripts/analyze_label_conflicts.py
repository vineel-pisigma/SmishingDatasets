from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

DUPLICATES = ROOT / "datasets" / "merged" / "exact_duplicates.csv"


def main():

    df = pd.read_csv(DUPLICATES)

    # Find messages that have more than one label
    label_counts = (
        df.groupby("message")["label"]
        .nunique()
    )

    conflicting_messages = label_counts[
        label_counts > 1
    ].index

    conflicts = df[
        df["message"].isin(conflicting_messages)
    ].copy()

    print("=" * 70)
    print("LABEL CONFLICT ANALYSIS")
    print("=" * 70)

    print(
        f"Conflicting unique messages: "
        f"{len(conflicting_messages):,}"
    )

    print(
        f"Records involved in conflicts: "
        f"{len(conflicts):,}"
    )

    print("\nConflict combinations:")

    combinations = (
        conflicts
        .groupby("message")["label"]
        .apply(lambda x: " + ".join(sorted(set(x))))
        .value_counts()
    )

    print(combinations)

    # -----------------------------------------------------
    # Save detailed report
    # -----------------------------------------------------

    output = (
        ROOT
        / "datasets"
        / "merged"
        / "label_conflicts.csv"
    )

    conflicts = conflicts.sort_values(
        ["message", "source"]
    )

    conflicts.to_csv(
        output,
        index=False
    )

    print(f"\nSaved: {output}")

    # -----------------------------------------------------
    # Display examples
    # -----------------------------------------------------

    print("\nSample conflicts:\n")

    for message, group in conflicts.groupby("message"):

        print("-" * 70)
        print("MESSAGE:")
        print(message)

        print("\nLABELS / SOURCES:")

        print(
            group[
                [
                    "label",
                    "original_label",
                    "source",
                    "source_id"
                ]
            ].to_string(index=False)
        )

        print()

        # Only show first 10 conflict groups
        if list(conflicts.groupby("message").groups).index(message) >= 9:
            break


if __name__ == "__main__":
    main()