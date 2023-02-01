import flet as ft


class Checks:
    def check_file_or_folder_exists(self, path: ft.Path) -> bool:
        """Check if the files exists"""
        if not path.exists():
            return False
        return True


def test_component():
    checks = Checks()
    template_file = ft.Path("template.docx")
    data_file = ft.Path("context.csv")
    output_dir = ft.Path("output")

    template_file_exists = checks.check_file_or_folder_exists(template_file)
    data_file_exists = checks.check_file_or_folder_exists(data_file)
    output_dir_exists = checks.check_file_or_folder_exists(output_dir)

    if not output_dir_exists:
        # create the folder and log
        output_dir.mkdir()

    check_mark = ft.Icon("check_circle", color=ft.colors.GREEN_400, size=25)
    cross_mark = ft.Icon("cancel", color=ft.colors.RED_400, size=25)

    def exists_text(path: str, exists: bool) -> ft.Row:
        container = ft.Container(
            ft.Text(path),
            bgcolor=ft.colors.ON_INVERSE_SURFACE,
            border_radius=5,
            padding=ft.padding.symmetric(horizontal=5),
        )
        return ft.Row([
            container,
            ft.Text("exists", color=ft.colors.GREEN_400) if exists else ft.Text(
                "does not exist", color=ft.colors.RED_400)
        ])

    create_button = ft.OutlinedButton("Create", height=40)

    return ft.Column([
        ft.ListTile(
            dense=True,
            title=exists_text("template.docx", template_file_exists),
            leading=check_mark if template_file_exists else cross_mark,
            trailing=create_button if not template_file_exists else None
        ),
        ft.ListTile(
            dense=True,
            title=exists_text("context.csv", data_file_exists),
            leading=check_mark if data_file_exists else cross_mark,
            trailing=create_button if not data_file_exists else None

        ),
        ft.ListTile(
            dense=True,
            title=exists_text("output", output_dir_exists),
            leading=check_mark if output_dir_exists else cross_mark,
            trailing=create_button if not output_dir_exists else None

        )
    ])


def main(page: ft.Page):
    page.title = "Parser v3"
    page.vertical_alignment = ft.MainAxisAlignment.START
    # change width to 200
    page.window_width = 600

    test_container = ft.Container(test_component())
    page.add(test_container)


ft.app(target=main)
