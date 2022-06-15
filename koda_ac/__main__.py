from glob import glob
from pathlib import Path

import typer
import rich
from matplotlib import pyplot as plt
from rich.progress import track

from koda_ac.core import compress_file, decompress_file

cli = typer.Typer()


@cli.command()
def compress(
    file: Path = typer.Argument(default=...),
    out_file: Path = typer.Argument(
        default=None, help="<original stem>.artpack by default"
    ),
):
    if "*" in str(file) and out_file:
        rich.print("Can't combine out_file with a glob.")
        return

    with open(".report.md", "w") as report:
        report.write("| Nazwa pliku | Entropia | Zyskano miejsca |\n")
        report.write("| ----------- | -------- | ----------------- |\n")

        for file in glob(str(file)):
            file = Path(file)
            rich.print("--- Compressing", file, "---")
            out_path, model = compress_file(
                file,
                out_path=out_file,
                iter_wrapper=lambda iter_: track(iter_, total=file.stat().st_size),
            )
            space_saved = round(
                -out_path.stat().st_size / file.stat().st_size * 100 + 100, 2
            )
            report.write(f"| {file} | {model.entropy} | {space_saved}% |\n")
            rich.print(f"Compressed data written to", out_path)
            rich.print(f"Entropy:", model.entropy)
            rich.print(f"Space saved:", space_saved, "%")
            fig = plt.figure()
            plt.title(file.name)
            plt.bar(model.count.keys(), model.count.values())
            plot_file = file.with_suffix(".hist.png")
            plt.savefig(str(plot_file))
            plt.close(fig)
            rich.print("Input histogram saved as", plot_file)
            rich.print()
    rich.print("Report saved to .report.md")


@cli.command()
def decompress(
    file: Path = typer.Argument(default=...),
    out_file: Path = typer.Argument(
        default=None, help="<original stem>(artunpacked).<original_ext> by default"
    ),
):
    if "*" in str(file) and out_file:
        rich.print("Can't combine out_file with a glob.")
        return
    if file.suffix != ".artpack":
        rich.print("Only *.artpack files can be decompressed.")
        return
    for file in glob(str(file)):
        file = Path(file)
        decompress_file(
            file,
            out_path=out_file,
            iter_wrapper=lambda iter_, total: track(iter_, total=total, description=f"Decoding {file}..."),
        )


if __name__ == "__main__":
    cli()
