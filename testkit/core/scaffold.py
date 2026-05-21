"""项目脚手架生成器"""
from pathlib import Path
import yaml
from rich.console import Console
from testkit.models.project import ProjectMeta

console = Console()


DOMAIN_FRAMEWORKS = {
    "api": {"framework": "pytest + httpx", "tools": ["httpx", "pytest-xdist", "pytest-html"]},
    "web": {"framework": "pytest + playwright", "tools": ["playwright", "pytest-playwright", "pytest-html"]},
    "app": {"framework": "pytest + Appium", "tools": ["Appium-Python-Client", "pytest-html"]},
    "device": {"framework": "pytest + paho-mqtt", "tools": ["paho-mqtt", "pyserial", "pytest-html"]},
}

DOMAIN_DIRS = {
    "api": ["test-cases/auth", "test-cases/crud", "test-cases/scenario", "test-cases/integration",
            "scripts", "data", "knowledge", "skills"],
    "web": ["test-cases/ui", "test-cases/e2e", "test-cases/cross-browser", "test-cases/accessibility",
            "scripts", "data", "knowledge", "skills"],
    "app": ["test-cases/ui", "test-cases/gesture", "test-cases/offline", "test-cases/compatibility",
            "scripts", "data", "knowledge", "skills"],
    "device": ["test-cases/connectivity", "test-cases/protocol", "test-cases/firmware", "test-cases/hardware",
               "scripts", "data", "knowledge", "skills"],
}


def create_project(meta: ProjectMeta, output_dir: Path):
    """根据项目元数据生成脚手架"""
    console.print(f"\n[bold cyan]生成项目 {meta.name} 脚手架...[/bold cyan]\n")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 项目元数据文件
    project_yml = output_dir / "project.yml"
    project_yml.write_text(yaml.safe_dump(meta.model_dump(), default_flow_style=False, allow_unicode=True))

    # .gitignore
    (output_dir / ".gitignore").write_text(".env\n__pycache__/\n.pytest_cache/\nreports/\n*.pyc\n.DS_Store\n")

    # .env 模板
    env_content = "\n".join([f"# {e.upper()}_BASE_URL=" for e in meta.envs])
    (output_dir / ".env").write_text(f"# 环境变量\n{env_content}\n")

    # 顶层 Makefile
    makefile_lines = [".PHONY: all"]
    for domain in meta.domains:
        makefile_lines.append(f"\n{domain}:\n\tcd {domain} && make test")
    domain_targets = " ".join(meta.domains)
    makefile_lines.append(f"\nall: {domain_targets}")
    makefile_lines.append(f"\nreport:\n\tpython -m pytest --html=reports/full_report.html --self-contained-html")
    (output_dir / "Makefile").write_text("\n".join(makefile_lines) + "\n")

    # common/ 共享层
    common = output_dir / "common"
    common.mkdir(exist_ok=True)
    (common / "data_context.py").write_text('"""\ndata_context: 环境配置 + 账号池 + 数据生成器\n\n环境变量从项目根目录 .env 加载。\n各测试域通过 from common.data_context import get_env, get_account 引用。\n"""\n\nimport os\nfrom pathlib import Path\n\n\ndef get_env(name: str) -> str:\n    return os.getenv(f"{name.upper()}_BASE_URL", "")\n\n')
    for sub in ["data/static", "data/fixtures", "data/generators", "scripts"]:
        (common / sub).mkdir(parents=True, exist_ok=True)
        (common / sub / ".gitkeep").write_text("")

    # 各测试域
    for domain in meta.domains:
        domain_dir = output_dir / domain
        domain_dir.mkdir(exist_ok=True)

        # 域 Makefile
        domain_makefile = domain_dir / "Makefile"
        domain_makefile.write_text(f".PHONY: test\n\ntest:\n\tpython -m pytest test-cases/ -v --tb=short\n")

        # requirements.txt
        tools = DOMAIN_FRAMEWORKS.get(domain, {}).get("tools", [])
        (domain_dir / "requirements.txt").write_text("\n".join(tools) + "\n")

        # pytest.ini
        (domain_dir / "pytest.ini").write_text(f"[pytest]\ntestpaths = test-cases\npython_files = test_*.py\naddopts = -v --tb=short\n")

        # conftest.py
        (domain_dir / "conftest.py").write_text(f'''"""\n{domain.upper()} 测试域 fixtures\n\n从 common/ 导入共享能力，本域内定义域专用 fixture。\n"""\nimport pytest\nimport sys\nfrom pathlib import Path\n\n# 将 common 加入 path\nsys.path.insert(0, str(Path(__file__).parent.parent / "common"))\n\n\n@pytest.fixture(scope="session")\ndef base_url():\n    from data_context import get_env\n    return get_env("{domain}")\n''')

        # 子目录
        for sub in DOMAIN_DIRS.get(domain, []):
            (domain_dir / sub).mkdir(parents=True, exist_ok=True)
            (domain_dir / sub / ".gitkeep").write_text("")

    # reports/
    (output_dir / "reports").mkdir(exist_ok=True)
    (output_dir / "reports" / ".gitkeep").write_text("")

    # .agents/
    agents_dir = output_dir / ".agents"
    (agents_dir / "agents").mkdir(parents=True, exist_ok=True)
    (agents_dir / "project-skills.md").write_text(f"# {meta.name} 技能清单\n\n")
    (agents_dir / "agents" / ".gitkeep").write_text("")

    console.print(f"\n[green]✓ 项目 {meta.name} 脚手架生成完成[/green]")
    console.print(f"[green]✓ 测试域: {', '.join(meta.domains)}[/green]")
