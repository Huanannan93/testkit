"""testkit update"""
import typer
from testkit.workspace import ensure_config
from testkit.core.repo_manager import RepoManager
from rich.console import Console
console = Console()


def update(
    no_pull: bool = typer.Option(False, "--no-pull", help="跳过 git pull"),
):
    """更新所有仓库"""
    config = ensure_config()
    mgr = RepoManager(config)

    console.print("\n[bold cyan]更新 test-ecosystem...[/bold cyan]\n")

    if not no_pull:
        console.print("[bold]拉取更新:[/bold]")
        mgr.update_all()

    console.print("\n[bold]重建索引:[/bold]")
    mgr.update_index()

    console.print(f"\n[bold green]✓ 更新完成[/bold green]")
