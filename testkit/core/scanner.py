"""统一扫描器：扫描 skills/knowledge/agents 文件，提取 frontmatter 元数据，维护 index.json"""
import json
import re
from pathlib import Path
import yaml
from rich.console import Console

console = Console()


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 YAML frontmatter，返回 (元数据, 正文)"""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    meta = yaml.safe_load(parts[1]) or {}
    return meta, parts[2]


def scan_dir(directory: Path, suffix: str = ".md") -> list[dict]:
    """扫描目录下所有指定后缀文件，返回元数据列表"""
    results = []
    if not directory.exists():
        return results
    for f in sorted(directory.rglob(f"*{suffix}")):
        if f.name.startswith("."):
            continue
        try:
            content = f.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(content)
            if meta:
                meta["file_path"] = str(f.relative_to(directory))
                meta["_body"] = body
                results.append(meta)
        except Exception as e:
            console.print(f"  [yellow]⚠ 解析 {f} 失败: {e}[/yellow]")
    return results


def scan_all(repo_path: Path) -> dict[str, list[dict]]:
    """扫描整个仓库，按分类返回"""
    result = {
        "skills": scan_dir(repo_path, ".md"),
        "knowledge": scan_dir(repo_path, ".md"),
        "agents": scan_dir(repo_path, ".md"),
        "templates": scan_dir(repo_path, ".md"),
    }
    # 过滤掉无 frontmatter 的普通文件
    return result


class Scanner:
    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path.home() / ".testkit" / "ecosystem"
        self._cache: dict[str, list[dict]] = {}

    def scan_repo(self, repo_name: str) -> list[dict]:
        """扫描指定仓库"""
        repo_path = self.workspace / repo_name
        if not repo_path.exists():
            return []
        return scan_dir(repo_path, ".md")

    def scan_all_repos(self) -> dict[str, list[dict]]:
        """扫描所有仓库"""
        results = {}
        for d in self.workspace.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                items = scan_dir(d, ".md")
                if items:
                    results[d.name] = items
        self._cache = results
        return results

    def scan_and_save_index(self, repo_path: Path, index_path: Path):
        """扫描仓库并保存 index.json"""
        items = scan_dir(repo_path, ".md")
        # 去 body，只保留元数据
        clean = [{k: v for k, v in item.items() if k != "_body"} for item in items]
        index_path.write_text(json.dumps(clean, ensure_ascii=False, indent=2))

    def search(self, query: str, repo_name: str = None) -> list[dict]:
        """grep 搜索"""
        import subprocess
        search_dir = self.workspace / repo_name if repo_name else self.workspace
        if not search_dir.exists():
            return []
        try:
            result = subprocess.run(
                ["grep", "-rli", query, str(search_dir)],
                capture_output=True, text=True, timeout=10
            )
            return [{"file": line} for line in result.stdout.strip().split("\n") if line]
        except subprocess.TimeoutExpired:
            return []
