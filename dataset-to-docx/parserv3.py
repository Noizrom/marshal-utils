from typing import Any, Generator
import flet as ft
import csv
import uuid


from docxtpl import DocxTemplate

template_file = ft.Path("template.docx")
data_file = ft.Path("context.csv")
output_dir = ft.Path("output")


class DependenciesCheck:
    def __init__(self):
        self.failed = 0
        self.path_exists: dict[ft.Path, bool] = dict()
        self.run_check()

    def run_check(self):
        self.failed = 0
        for path in [template_file, data_file, output_dir]:
            exists = True
            if not path.exists():
                self.failed += 1
                exists = False
            self.path_exists[path] = exists


def banner(button: ft.OutlinedButton, checks: DependenciesCheck):
    def generate_rows():
        for path, exists in checks.path_exists.items():
            check_mark = ft.Icon(
                "check_circle", color=ft.colors.GREEN_400, size=20)
            cross_mark = ft.Icon("cancel", color=ft.colors.RED_400, size=20)

            container = ft.Container(
                ft.Text(path.__str__()),
                bgcolor=ft.colors.ON_INVERSE_SURFACE,
                border_radius=5,
                padding=ft.padding.symmetric(horizontal=5),
            )
            mark = check_mark if exists else cross_mark

            yield ft.Row([
                mark,
                container,
                ft.Text("exists", color=ft.colors.GREEN_400) if exists else ft.Text(
                    "does not exist", color=ft.colors.RED_400)
            ])

    column = ft.Column()

    def updated_column() -> list:
        results = generate_rows()
        button.text = "Dependencies" if checks.failed == 0 else f"Dependencies ({checks.failed})"
        return list(results)

    column.controls = updated_column()

    def close(e):
        e.page.banner.open = False
        e.page.update()

    def refresh(e):
        nonlocal column
        column.controls = updated_column()
        checks.run_check()
        e.page.update()

    return ft.Banner(
        content=column,
        bgcolor=ft.colors.ON_TERTIARY,
        actions=[
            ft.TextButton("Retry", on_click=refresh),
            ft.TextButton("Close", on_click=close),
        ]
    )


class Action:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        self.doc = DocxTemplate(template_file)
        self.output = output_dir / f"{self.data['NAME']}.docx"

    def run(self) -> None:
        self.doc.render(self.data)
        self.doc.save(self.output)

    @property
    def exists(self) -> bool:
        return self.output.exists()


def content(data: dict[str, Any], checkbox_ref: ft.Ref[ft.Checkbox]):

    text = ft.Text("PENDING", color=ft.colors.AMBER)
    status = ft.Container(text,
                          border=ft.border.all(1, ft.colors.AMBER),
                          border_radius=5,
                          padding=4)

    action = Action(data)

    if action.exists:
        text.value = "DONE"
        text.color = ft.colors.GREEN_400
        status.border = ft.border.all(1, ft.colors.GREEN_400)

    def play(e):
        action.run()
        if action.exists:
            text.value = "DONE"
            text.color = ft.colors.GREEN_400
            status.border = ft.border.all(1, ft.colors.GREEN_400)
            e.page.update()

    return ft.Row([
        ft.Row([
            ft.Checkbox(ref=checkbox_ref, fill_color=ft.colors.ON_BACKGROUND,
                        check_color=ft.colors.BACKGROUND),
            ft.Text(data['NAME'], style=ft.TextThemeStyle.LABEL_LARGE),
        ]),
        status,
    ],
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,)


class ItemsManager:
    def __init__(self):
        # get all the data
        self.references: dict[uuid.UUID, ft.Ref[ft.Checkbox]] = dict()
        self.containers: list[ft.Container] = list()

        with data_file.open() as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = [row for row in reader]
            self.data = [{header[i]: row[i]
                          for i in range(len(header))} for row in rows]

        for datum in self.data:
            row_id = uuid.uuid4()
            container = ft.Container()

            checkbox_ref = ft.Ref[ft.Checkbox]()
            text_row = content(datum, checkbox_ref)

            container.content = ft.Card(
                content=ft.Container(text_row, padding=10,
                                     border_radius=ft.border_radius.all(5),
                                     bgcolor=ft.colors.ON_SECONDARY),
                elevation=3)

            self.containers.append(container)
            self.references[row_id] = checkbox_ref

    def check_all(self, e):
        for container in self.references.values():
            container.current.value = True
        e.page.update()

    def unchecked_all(self, e):
        for container in self.references.values():
            container.current.value = False
        e.page.update()

    def run_selected(self, e):
        for container in self.references.items():
            ...
            # print("ID: ", container[0])
            # print("REF: ", container[1].current.value)


def main(page: ft.Page):
    page.title = "Parser v3"
    page.vertical_alignment = ft.MainAxisAlignment.START
    # change width to 200
    page.window_width = 600

    items = ItemsManager()
    checks = DependenciesCheck()

    def toggle_banner(e):
        initial = bool(e.page.banner.open)
        page.banner.open = not initial  # type: ignore
        page.update()

    dependencies_btn = ft.OutlinedButton("Dependencies", style=ft.ButtonStyle(
        elevation=10,
        shape=ft.RoundedRectangleBorder(radius=5)), on_click=toggle_banner, height=28,
        icon="info")

    delete_all_btn = ft.OutlinedButton("Delete All", style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=5)), on_click=toggle_banner, height=28)

    rerun_all_btn = ft.OutlinedButton("Rerun All", style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=5)), on_click=toggle_banner, height=28)

    run_selected_btn = ft.OutlinedButton("Run Selected", style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=5)),
        on_click=items.run_selected, height=28)

    check_all_btn = ft.OutlinedButton("Check All", style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=5)),
        on_click=items.check_all, height=28)

    unchecked_all_btn = ft.OutlinedButton("Uncheck All", style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=5)),
        on_click=items.unchecked_all, height=28)

    page.banner = banner(dependencies_btn, checks=checks)
    page.banner.open = True if checks.failed > 0 else False

    page.add(ft.Row([dependencies_btn, delete_all_btn,
             rerun_all_btn, run_selected_btn, check_all_btn, unchecked_all_btn]))

    lv = ft.ListView(expand=1, spacing=2, padding=8, auto_scroll=False)
    lv.controls = items.containers

    page.add(lv)


ft.app(target=main)
