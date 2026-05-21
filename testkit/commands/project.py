"""testkit project — 项目管理"""
import typer
import yaml
from pathlib import Path
from datetime import date

import questionary
from testkit.workspace import ensure_config
from testkit.core.repo_manager import RepoManager
from testkit.core.scaffold import create_project, DOMAIN_FRAMEWORKS
from testkit.models.project import ProjectMeta
from testkit.main import console

project = typer.Typer(help="项目管理", no_args_is_help=True)


@project.command(name="create")
def create(
    name: str = typer.Argument(help="项目名称"),
    output: str = typer.Option(None, help="输出目录（默认当前目录）"),
):
    """交互式创建新测试项目"""
    config = ensure_config()

    # Step 1: 测试域
    domains = questionary.checkbox(
        "选择测试域（空格选择，回车确认）",
        choices=[
            questionary.Choice("API Testing", value="api"),
            questionary.Choice("WEB Testing", value="web"),
            questionary.Choice("APP Testing", value="app"),
            questionary.Choice("Device Testing (物联网)", value="device"),
        ]
    ).ask()

    if not domains:
        console.print("[red]必须选择至少一个测试域[/red]")
        return

    # Step 2: 环境
    envs_str = questionary.text(
        "环境名（逗号分隔）",
        default="dev,staging"
    ).ask()
    envs = [e.strip() for e in envs_str.split(",") if e.strip()]

    # Step 3: CI
    ci = questionary.select(
        "CI 平台",
        choices=["github-actions", "gitlab-ci", "none"]
    ).ask() or "github-actions"

    # 显示概览
    console.print("\n[bold cyan]项目配置概览:[/bold cyan]")
    console.print(f"  名称: {name}")
    console.print(f"  测试域: {', '.join(domains)}")
    for d in domains:
        fw = DOMAIN_FRAMEWORKS.get(d, {})
        console.print(f"    {d}: {fw.get('framework', 'custom')}")
    console.print(f"  环境: {', '.join(envs)}")
    console.print(f"  CI: {ci}")

    confirm = questionary.confirm("确认创建？").ask()
    if not confirm:
        console.print("[yellow]已取消[/yellow]")
        return

    # 生成
    output_dir = Path(output) if output else Path.cwd() / name
    meta = ProjectMeta(
        name=name,
        domains=domains,
        created=str(date.today()),
        envs=envs,
        ci=ci,
    )
    create_project(meta, output_dir)

    # 注册到项目索引
    mgr = RepoManager(config)
    projects_dir = mgr.repo_dir("projects")
    if projects_dir.exists():
        index_file = projects_dir / f"{name}.yml"
        index_file.write_text(yaml.safe_dump(meta.model_dump(), default_flow_style=False, allow_unicode=True))
        console.print(f"[green]✓ 项目索引已注册到 {index_file}[/green]")


@project.command(name="list")
def list_projects():
    """列出所有项目"""
    config = ensure_config()
    mgr = RepoManager(config)
    projects_dir = mgr.repo_dir("projects")

    if not projects_dir.exists():
        console.print("[yellow]项目索引仓库未初始化，请先运行 testkit init[/yellow]")
        return

    projects = list(projects_dir.glob("*.yml"))
    if not projects:
        console.print("[yellow]暂无项目[/yellow]")
        return

    from rich.table import Table
    table = Table(title="项目列表")
    table.add_column("名称", style="cyan")
    table.add_column("测试域")
    table.add_column("创建日期")
    table.add_column("环境")

    for p in projects:
        meta = yaml.safe_load(p.read_text())
        table.add_row(
            meta.get("name", p.stem),
            ", ".join(meta.get("domains", [])),
            meta.get("created", ""),
            ", ".join(meta.get("envs", [])),
        )

    console.print(table)
