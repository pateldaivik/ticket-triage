from pathlib import Path

import pandas as pd


def main():

    here = Path(__file__).resolve()
    scripts_dir = here.parent
    root = scripts_dir.parent

    out_file = root / "data" / "customer_support_tickets.parquet"
    df = pd.read_parquet(out_file)

    eng_df = df[df["language"] == "en"]
    eng_df = eng_df["queue"].value_counts()

    top_8 = eng_df.head(8)
    print(top_8)


if __name__ == "__main__":
    main()
