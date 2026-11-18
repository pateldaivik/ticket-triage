from pathlib import Path

from datasets import load_dataset


def main():

    data = load_dataset("Tobi-Bueck/customer-support-tickets")
    split = data["train"]

    here = Path(__file__).resolve()
    scripts_dir = here.parent
    root = scripts_dir.parent

    out_file = root / "data" / "customer_support_tickets.parquet"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    split.to_parquet(out_file)
    print(len(split))


if __name__ == "__main__":
    main()
