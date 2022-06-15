from glob import glob
from pathlib import Path

import typer
import rich
from rich.progress import track

from koda.core import compress_file

cli = typer.Typer()


@cli.command("compress")
def compress(
    file: Path = typer.Argument(default=...),
    out_file: Path = typer.Argument(
        default=None, help="<original stem>.artpack by default"
    ),
):
    if "*" in str(file) and out_file:
        raise typer.Abort("Can't combine out_file with a glob.")
    for file in glob(str(file)):
        file = Path(file)
        rich.print("--- Compressing", file, "---")
        out_file, model = compress_file(
            file,
            out_path=out_file,
            iter_wrapper=lambda iter_: track(iter_, total=file.stat().st_size),
        )
        rich.print(f"Compressed data written to", out_file)
        rich.print(f"Entropy: ", model.entropy)
        rich.print(f"Compression ratio: ", file.stat().st_size / out_file.stat().st_size * 100, "%\n")


if __name__ == "__main__":
    cli()
