from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

INPUT = (
    ROOT
    / "datasets"
    / "master"
    / "conflict_analysis_v2.csv"
)

OUTPUT = (
    ROOT
    / "datasets"
    / "master"
    / "conflict_review.xlsx"
)


def main():

    df = pd.read_csv(INPUT)

    # Put the important columns first
    columns = [
        "message",
        "suggested_label",
        "reason",
        "smishing_indicators",
        "spam_indicators",
        "labels_found",
        "sources",
        "record_count",
        "final_label",
    ]

    df = df[columns].copy()

    # Add a human-review status
    df["review_status"] = "pending"

    # Keep final_label empty initially
    df["final_label"] = ""

    # Make an Excel file
    with pd.ExcelWriter(
        OUTPUT,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Conflict Review",
            index=False
        )

        # Helpful summary
        summary = (
            df["suggested_label"]
            .value_counts()
            .rename_axis("suggestion")
            .reset_index(name="count")
        )

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

    print("=" * 70)
    print("CONFLICT REVIEW FILE CREATED")
    print("=" * 70)

    print(f"Total conflicts: {len(df):,}")

    print(
        f"Saved:\n{OUTPUT}"
    )


if __name__ == "__main__":
    main()