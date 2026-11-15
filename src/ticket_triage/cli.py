import typer

app = typer.Typer()


@app.command()
def classify(n: int = 50):
    """Classify n tickets (wired up once llm.py exists)."""
    typer.echo(f"Would classify {n} tickets")
