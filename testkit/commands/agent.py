"""testkit agent — Agent 模板管理"""
import typer
import json

from testkit.workspace import ensure_config
from testkit.core.repo_manager import RepoManager
from testkit.main import console
from rich.table import Table

agent = typer.Typer(help="Agent 管理", no_args_is_help=True)


@agent.command(name="list")
def list_agents(
    category: str = typer.Option(None, "--category", "-c", help="按分类筛选"),
):
    """列出可用 Agent 模板"""
    config = ensure_config()
    mgr = RepoManager(config)
    agents_dir = mgr.repo_dir("agents")
    idx_path = agents_dir / "index.json"

    items = []
    if idx_path.exists():
        items = json.loads(idx_path.read_text())
    if not items:
        console.print("[yellow]Agent 仓库为空或 index 未构建[/yellow]")
        return

    table = Table(title="可用 Agent 模板")
    table.add_column("名称")
    table.add_column("描述")
    table.add_column("版本")

    for item in items:
        table.add_row(
            item.get("name", "?"),
            item.get("description", "")[:60],
            item.get("version", "?"),
        )

    console.print(table)
