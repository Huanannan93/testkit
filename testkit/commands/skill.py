"""testkit skill — 技能管理"""
import typer
from pathlib import Path
import json

from testkit.workspace import ensure_config
from testkit.core.repo_manager import RepoManager
from testkit.core.skill_loader import load_skill, format_context
from testkit.main import console
from rich.table import Table

skill = typer.Typer(help="技能管理", no_args_is_help=True)


@skill.command(name="list")
def list_skills(
    category: str = typer.Option(None, "--category", "-c", help="按分类筛选"),
):
    """列出可用技能"""
    config = ensure_config()
    mgr = RepoManager(config)
    skills_dir = mgr.repo_dir("skills")
    idx_path = skills_dir / "index.json"

    items = []
    if idx_path.exists():
        items = json.loads(idx_path.read_text())
    if not items:
        console.print("[yellow]技能仓库为空或 index 未构建，请先运行 testkit update[/yellow]")
        return

    if category:
        items = [i for i in items if i.get("category", "") == category]

    table = Table(title="可用技能")
    table.add_column("Slug", style="cyan")
    table.add_column("名称")
    table.add_column("版本")
    table.add_column("分类")
    table.add_column("状态")

    for item in items:
        status = "[red]废弃[/red]" if item.get("deprecated") else "[green]活跃[/green]"
        table.add_row(
            item.get("slug", "?"),
            item.get("name", "?"),
            item.get("version", "?"),
            item.get("category", "?"),
            status,
        )

    console.print(table)


@skill.command(name="load")
def load(
    name: str = typer.Argument(help="技能 slug"),
    output: str = typer.Option(None, "--output", "-o", help="输出到文件"),
):
    """加载技能到 AI 上下文（解析依赖 + 拼接上下文）"""
    config = ensure_config()
    mgr = RepoManager(config)
    skills_dir = mgr.repo_dir("skills")

    try:
        result = load_skill(skills_dir, name)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        return

    console.print(f"[cyan]加载 {name}，依赖链:[/cyan]")
    for s in result["order"]:
        console.print(f"  → {s}")

    context = format_context(result)

    if output:
        Path(output).write_text(context, encoding="utf-8")
        console.print(f"[green]已输出到 {output}[/green]")
    else:
        console.print(context)


@skill.command(name="install")
def install(
    name: str = typer.Argument(help="技能 slug"),
    project_dir: str = typer.Option(None, "--project", "-p", help="项目目录"),
):
    """安装技能到项目"""
    config = ensure_config()
    mgr = RepoManager(config)
    skills_dir = mgr.repo_dir("skills")

    try:
        load_skill(skills_dir, name)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        return

    # 复制技能到项目
    target = Path(project_dir) if project_dir else Path.cwd()
    if not target.exists():
        console.print(f"[red]项目目录 {target} 不存在[/red]")
        return

    agents_dir = target / ".agents" / "skills"
    agents_dir.mkdir(parents=True, exist_ok=True)

    # 查找并复制技能文件
    for f in skills_dir.rglob("*.md"):
        content = f.read_text(encoding="utf-8")
        if f"slug: {name}" in content:
            dest = agents_dir / f"{name}.md"
            dest.write_text(content, encoding="utf-8")
            console.print(f"[green]✓ {name} 已安装到 {dest}[/green]")
            return

    console.print(f"[yellow]未找到技能文件: {name}[/yellow]")
