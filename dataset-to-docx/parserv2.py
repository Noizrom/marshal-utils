from pathlib import Path
from docxtpl import DocxTemplate
import csv

try:
    import rich
except ImportError:
    # install rich
    import subprocess

    subprocess.check_call(["python", "-m", "pip", "install", "rich"])
finally:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.text import Text
    from rich.padding import Padding
    from rich.columns import Columns
    from rich.prompt import Confirm
    from rich.status import Status


console = Console()


def clean_filename(dirty_filename: str) -> str:
    """Clean a filename by removing invalid characters"""
    return "".join(c for c in dirty_filename if c.isalnum() or c in " _-.")


def print_padded_panel(renderable: str):
    """Print a padded panel with the renderable"""
    panel = Padding(Panel(Text.from_markup(renderable)), (1, 2))
    console.print(panel)


def file_existence_checker(
    template_file: Path, data_file: Path, output_dir: Path
) -> tuple[bool, bool]:
    """Check if the files exists"""
    lines = []
    errored = False
    output_dir_exists = True

    if not template_file.exists():
        message = f"[bright_yellow]{template_file}"
        status = "[bright_red][ Missing ] "
        lines.append(Columns([Text.from_markup(status), Text.from_markup(message)]))
        errored = True
    else:
        message = f"[bright_green]{template_file}"
        status = "[bright_green][ Found   ] "
        lines.append(Columns([Text.from_markup(status), Text.from_markup(message)]))

    if not data_file.exists():
        message = f"[bright_yellow]{data_file}"
        status = "[bright_red][ Missing ] "
        lines.append(Columns([Text.from_markup(status), Text.from_markup(message)]))
        errored = True
    else:
        message = f"[bright_green]{data_file}"
        status = "[bright_green][ Found   ] "
        lines.append(Columns([Text.from_markup(status), Text.from_markup(message)]))

    if not output_dir.exists():
        message = f"[bright_yellow]{output_dir}"
        status = "[bright_yellow][ Missing ] "
        lines.append(Columns([Text.from_markup(status), Text.from_markup(message)]))
        output_dir_exists = False
    else:
        message = f"[bright_green]{output_dir}"
        status = "[bright_green][ Found   ] "
        lines.append(Columns([Text.from_markup(status), Text.from_markup(message)]))

    panel = Padding(Panel(Group(*lines), title="Dependencies Check"), (1, 2))

    console.print(panel)

    return (errored, output_dir_exists)


def main():
    template_file = Path("template.docx")
    data_file = Path("context.csv")
    output_dir = Path("output")

    breaking_error, output_exists = file_existence_checker(
        template_file, data_file, output_dir
    )
    if not output_exists:
        # create the folder and log
        output_dir.mkdir()
        console.log(f"[bright_blue]Creating output directory {output_dir}")

    if breaking_error:
        console.log("[bright_red]Please fix the errors above and try again")
        return

    # check if the output directory is empty. prompt to delete content if not
    if len(list(output_dir.iterdir())) > 0:
        if not Confirm(console=console).ask(
            "[bright_yellow]Do you want to delete the content?"
        ):
            # continue but with a warning
            print_padded_panel("[bright_yellow]Continuing with existing content")
        else:
            # delete all files in the output directory
            for file in output_dir.iterdir():
                file.unlink()

            print_padded_panel("[bright_blue]Deleted all files in output directory")

    # load the data
    with data_file.open() as dfile:
        try:
            reader = csv.reader(dfile)
            headers = next(reader)
            data: list[dict[str, str]] = [dict(zip(headers, row)) for row in reader]
        except csv.Error as e:
            console.log(f"[bright_red]Error reading {data_file}: {e}")
            return

    console.print(f"[bright_blue]👌Replacing Keywords : [green]{' ,'.join(headers)}")
    console.rule("[bright_blue]Generating Files")

    with Status("[bright_blue]Generating Files", console=console) as status:
        for row in data:
            # create the output file
            assumed_name = list(row.values())[0]
            output_file = (output_dir / assumed_name).with_suffix(".docx")

            # if file exists. add a number to the end
            if output_file.exists():
                i = 1
                while True:
                    new_output_file = output_dir / f"{assumed_name} ({i}).docx"
                    if not new_output_file.exists():
                        output_file = new_output_file
                        break
                    i += 1

            status.update(f"[bright_blue]Generating {output_file}")
            # load the template
            doc = DocxTemplate(template_file)
            doc.render(row)

            doc.save(output_file)
            console.log(f"[bright_green]Saved {output_file}")

    console.rule("[bright_blue]Done")

    input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
