from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "2021_92-156-X_DA_AD.csv"


def inspect_data():
    df = pd.read_csv(
        DATA_PATH,
        dtype={
            "DAUID2021_ADIDU2021": str,
            "DAUID2016_ADIDU2016": str,
        },
    )

    ontario = df[df["DAUID2021_ADIDU2021"].str.startswith("35")]

    relationship_counts = (
        ontario[
            [
                "DAUID2021_ADIDU2021",
                "DARELFLAG_ADINDREL",
            ]
        ]
        .drop_duplicates()
        ["DARELFLAG_ADINDREL"]
        .value_counts()
        .sort_index()
    )

    print(f"Total rows: {len(df)}")
    print(f"Ontario rows: {len(ontario)}")
    print(
        f"Unique Ontario 2021 DAs: "
        f"{ontario['DAUID2021_ADIDU2021'].nunique()}"
    )
    print(
        f"Unique Ontario 2016 DAs: "
        f"{ontario['DAUID2016_ADIDU2016'].nunique()}"
    )

    print("\nOntario relationship counts:")
    print(relationship_counts)


if __name__ == "__main__":
    inspect_data()