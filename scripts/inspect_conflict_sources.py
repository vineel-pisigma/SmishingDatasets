from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "datasets" / "master" / "label_conflicts.csv"


def main():

    df = pd.read_csv(INPUT)

    print("=" * 70)
    print("CONFLICT SOURCE ANALYSIS")
    print("=" * 70)

    print(f"Conflict records: {len(df):,}")

    # -----------------------------------------------------
    # Source combinations
    # -----------------------------------------------------

    print("\nSource combinations:")

    print(
        df["sources"]
        .value_counts()
    )

    # -----------------------------------------------------
    # Record count distribution
    # -----------------------------------------------------

    print("\nNumber of source records per message:")

    print(
        df["record_count"]
        .value_counts()
        .sort_index()
    )

    # -----------------------------------------------------
    # Labels found
    # -----------------------------------------------------

    print("\nLabels found:")

    print(
        df["labels_found"]
        .value_counts()
    )

    # -----------------------------------------------------
    # Save source analysis
    # -----------------------------------------------------

    source_summary = (
        df.groupby("sources")
        .agg(
            messages=("message", "count"),
            total_records=("record_count", "sum")
        )
        .reset_index()
        .sort_values(
            "messages",
            ascending=False
        )
    )

    output = (
        ROOT
        / "datasets"
        / "master"
        / "conflict_source_summary.csv"
    )

    source_summary.to_csv(
        output,
        index=False
    )

    print(f"\nSaved: {output}")

    # -----------------------------------------------------
    # Show examples by source combination
    # -----------------------------------------------------

    for source_combo in df["sources"].unique():

        print("\n" + "=" * 70)
        print(f"SOURCE COMBINATION: {source_combo}")

        subset = df[
            df["sources"] == source_combo
        ].head(5)

        for _, row in subset.iterrows():

            print("-" * 70)
            print(row["message"])
            print(
                f"Labels: {row['labels_found']}"
            )
            print(
                f"Sources: {row['sources']}"
            )
            print(
                f"Records: {row['record_count']}"
            )


if __name__ == "__main__":
    main()