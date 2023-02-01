import flet as ft


class Checks:
    def check_file_or_folder_exists(self, path: ft.Path) -> bool:
        """Check if the files exists"""
        if not path.exists():
            return False
        return True


def test_component(button: ft.FilledButton):
    failed = 0
    checks = Checks()
    template_file = ft.Path("template.docx")
    data_file = ft.Path("context.csv")
    output_dir = ft.Path("output")

    def exists_text(path: ft.Path) -> ft.Row:
        nonlocal failed
        check_mark = ft.Icon(
            "check_circle", color=ft.colors.GREEN_400, size=20)
        cross_mark = ft.Icon("cancel", color=ft.colors.RED_400, size=20)

        exists = checks.check_file_or_folder_exists(path)
        if not exists:
            failed += 1

        container = ft.Container(
            ft.Text(path.__str__()),
            bgcolor=ft.colors.ON_INVERSE_SURFACE,
            border_radius=5,
            padding=ft.padding.symmetric(horizontal=5),
        )
        mark = check_mark if exists else cross_mark
        return ft.Row([
            mark,
            container,
            ft.Text("exists", color=ft.colors.GREEN_400) if exists else ft.Text(
                "does not exist", color=ft.colors.RED_400)
        ])
    column = ft.Column()

    def updated_column() -> list:
        results = [
            exists_text(template_file),
            exists_text(data_file),
            exists_text(output_dir)
        ]
        button.text = "Dependencies" if failed == 0 else f"Dependencies ({failed})"
        return results

    column.controls = updated_column()

    def close(e):
        e.page.banner.open = False
        e.page.update()

    def refresh(e):
        nonlocal column, failed
        failed = 0
        column.controls = updated_column()
        e.page.update()

    return ft.Banner(
        content=column,
        bgcolor=ft.colors.ON_TERTIARY,
        actions=[
            ft.TextButton("Retry", on_click=refresh),
            ft.TextButton("Close", on_click=close),
        ]
    )


def main(page: ft.Page):
    page.title = "Parser v3"
    page.vertical_alignment = ft.MainAxisAlignment.START
    # change width to 200
    page.window_width = 600

    def toggle_banner(e):
        initial = bool(e.page.banner.open)
        page.banner.open = not initial  # type: ignore
        page.update()

    dependencies_btn = ft.FilledButton("Dependencies", style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10)), on_click=toggle_banner)

    page.banner = test_component(dependencies_btn)

    page.banner.open = True

    page.add(dependencies_btn)


ft.app(target=main)
