"""testkit status"""
import json
import typer
from testkit.workspace import ensure_config, repo_status
from testkit.core.repo_manager import RepoManager
from testkit.main import console
from rich.table import Table


def status():
    """查看生态状态"""
    config = ensure_config()
    mgr = RepoManager(config)

    table = Table(title="test-ecosystem 状态")
    table.add_column("仓库", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("分支", style="yellow")
    table.add_column("最新 Commit")

    for name in config.repos:
        st = repo_status(name, mgr.repo_dir(name))
        if st["status"] == "ok":
            table.add_row(name, "✓", st.get("branch", "-"), st.get("commit", "-")[:50])
        elif st["status"] == "not cloned":
            table.add_row(name, "[red]未克隆[/red]", "-", "-")
        else:
            table.add_row(name, "[red]异常[/red]", "-", "-")

    console.print(table)

    # 检查 index.json 统计
    console.print("\n[bold]内容统计:[/bold]")
    for name in ["skills", "agents", "scripts", "knowledge", "templates"]:
        idx_path = mgr.repo_dir(name) / "index.json"
        if idx_path.exists():
            items = json.loads(idx_path.read_text())
            console.print(f"  [cyan]{name}[/cyan]: {len(items)} 项")
        else:
            console.print(f"  [cyan]{name}[/cyan]: [yellow]index 未构建[/yellow]")
