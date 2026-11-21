from pathlib import Path

import pandas as pd

SEED = 42
TEST_SIZE = 300
TOP_N_QUEUES = 8


def main():
    root = Path(__file__).resolve().parent.parent
    data_dir = root / "data"

    df = pd.read_parquet(data_dir / "customer_support_tickets.parquet")

    # English only
    df = df[df["language"] == "en"]

    # Drop empty bodies and exact-duplicate bodies so the same ticket
    # can't end up in both train and test (leakage).
    df = df.dropna(subset=["body"])
    df = df.drop_duplicates(subset=["body"])

    # Keep the N biggest queues
    top_queues = df["queue"].value_counts().head(TOP_N_QUEUES).index
    df = df[df["queue"].isin(top_queues)]

    # Fixed-seed split
    test = df.sample(n=TEST_SIZE, random_state=SEED)
    train = df.drop(test.index)

    test.to_csv(data_dir / "test.csv", index=False)
    train.to_csv(data_dir / "train.csv", index=False)

    print(f"train: {len(train)}  test: {len(test)}")
    print("\ntest queue counts:")
    print(test["queue"].value_counts())


if __name__ == "__main__":
    main()
