"""testkit init"""
from pathlib import Path
import typer
from testkit.config import Config, CONFIG_PATH
from testkit.workspace import ensure_config, clone_repo, pull_repo
from testkit.core.repo_manager import RepoManager
from rich.console import Console
console = Console()
from rich.table import Table


def init(
    workspace: str = typer.Option(None, help="工作区路径（默认 ~/.testkit/ecosystem）"),
    force: bool = typer.Option(False, "--force", "-f", help="强制重新初始化"),
):
    """初始化 test-ecosystem 工作区，拉取所有仓库"""
    config = ensure_config()

    if workspace:
        config.workspace = Path(workspace).expanduser().resolve()

    ws = config.workspace

    if ws.exists() and any(ws.iterdir()) and not force:
        console.print(f"[yellow]工作区 {ws} 已存在且非空。使用 --force 强制重新初始化。[/yellow]")
        return

    ws.mkdir(parents=True, exist_ok=True)
    console.print(f"\n[bold cyan]初始化 test-ecosystem 工作区: {ws}[/bold cyan]\n")

    # 检查依赖
    import subprocess
    for tool in ["git"]:
        result = subprocess.run(["which", tool], capture_output=True)
        if result.returncode != 0:
            console.print(f"[red]✗ {tool} 未安装[/red]")
            return
        console.print(f"  [green]✓ {tool}[/green]")

    console.print(f"  [green]✓ Python {__import__('sys').version.split()[0]}[/green]")

    # 克隆仓库
    console.print("\n[bold]拉取仓库:[/bold]")
    mgr = RepoManager(config)
    mgr.init_all()
    mgr.update_index()

    console.print(f"\n[bold green]✓ test-ecosystem 初始化完成[/bold green]")
    console.print(f"  工作区: {ws}")
    console.print(f"  运行 'testkit status' 查看状态")
