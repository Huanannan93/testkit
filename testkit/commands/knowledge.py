"""testkit knowledge — 知识库管理"""
import typer
from testkit.workspace import ensure_config
from testkit.core.repo_manager import RepoManager
from testkit.core.scanner import Scanner
from testkit.main import console

knowledge = typer.Typer(help="知识库管理", no_args_is_help=True)


@knowledge.command(name="search")
def search(
    query: str = typer.Argument(help="搜索关键词"),
    repo: str = typer.Option("knowledge", "--repo", "-r", help="搜索的仓库名"),
):
    """搜索知识库（grep）"""
    config = ensure_config()
    mgr = RepoManager(config)
    scanner = Scanner(workspace=mgr.config.workspace)

    console.print(f"[cyan]搜索 '{query}' 在 {repo}/ 中...[/cyan]\n")
    results = scanner.search(query, repo)

    if not results:
        console.print("[yellow]未找到匹配结果[/yellow]")
        return

    for r in results[:20]:
        console.print(f"  [cyan]{r['file']}[/cyan]")
    if len(results) > 20:
        console.print(f"  ... 还有 {len(results) - 20} 个结果")
