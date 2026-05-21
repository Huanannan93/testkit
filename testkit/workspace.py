"""工作区管理"""
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from testkit.config import Config, DEFAULT_CONFIG, CONFIG_PATH

console = Console()


def ensure_config() -> Config:
    """确保配置文件存在，不存在则写入默认配置"""
    if CONFIG_PATH.exists():
        return Config.from_file(CONFIG_PATH)
    DEFAULT_CONFIG.to_file(CONFIG_PATH)
    console.print(f"[green]已生成默认配置: {CONFIG_PATH}[/green]")
    return DEFAULT_CONFIG


def clone_repo(name: str, url: str, target: Path):
    """克隆单个仓库"""
    if target.exists():
        console.print(f"  [yellow]⏭ {name} 已存在，跳过[/yellow]")
        return True
    console.print(f"  [cyan]⬇ 正在克隆 {name}...[/cyan]")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", url, str(target)],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        console.print(f"  [red]✗ {name} 克隆失败: {result.stderr.strip()}[/red]")
        return False
    console.print(f"  [green]✓ {name} 克隆完成[/green]")
    return True


def pull_repo(name: str, path: Path):
    """更新单个仓库"""
    if not path.exists():
        return
    result = subprocess.run(
        ["git", "-C", str(path), "pull", "--ff-only"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        if "Already up to date" not in result.stdout:
            console.print(f"  [green]✓ {name} 已更新[/green]")
    else:
        console.print(f"  [yellow]⚠ {name}: {result.stderr.strip()}[/yellow]")


def repo_status(name: str, path: Path) -> dict:
    """获取仓库状态"""
    if not path.exists():
        return {"name": name, "status": "not cloned"}
    try:
        branch = subprocess.run(
            ["git", "-C", str(path), "branch", "--show-current"],
            capture_output=True, text=True
        ).stdout.strip()
        commit = subprocess.run(
            ["git", "-C", str(path), "log", "-1", "--format=%h %s"],
            capture_output=True, text=True
        ).stdout.strip()
        return {"name": name, "status": "ok", "branch": branch, "commit": commit}
    except Exception:
        return {"name": name, "status": "error"}
