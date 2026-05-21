"""技能加载器：解析依赖 + 拼接上下文"""
from pathlib import Path
from rich.console import Console
from testkit.core.scanner import scan_dir, parse_frontmatter
from testkit.core.dependency import resolve_load_order
from testkit.models.dep_ref import DepRef, parse_ref

console = Console()


def load_skill(repo_path: Path, skill_slug: str) -> dict:
    """加载单个技能，解析其依赖"""
    items = scan_dir(repo_path, ".md")
    skill_map = {}
    target = None

    for item in items:
        slug = item.get("slug", "")
        if slug:
            skill_map[slug] = item
        if slug == skill_slug:
            target = item

    if not target:
        raise ValueError(f"技能 {skill_slug} 不存在")

    # 解析依赖图
    deps_graph = {}
    _add_with_deps(target, skill_map, deps_graph, set())

    # 拓扑排序
    order = resolve_load_order(deps_graph)
    return {"order": order, "skills": [skill_map[s] for s in order]}


def _add_with_deps(skill: dict, skill_map: dict, graph: dict, visited: set):
    """递归添加技能及其依赖到图中"""
    slug = skill.get("slug", "")
    if slug in visited:
        return
    visited.add(slug)

    deps_raw = skill.get("depends_on", [])
    deps = [parse_ref(d) for d in deps_raw]
    graph[slug] = deps

    for dep in deps:
        if dep.target_slug in skill_map and dep.target_slug not in visited:
            _add_with_deps(skill_map[dep.target_slug], skill_map, graph, visited)


def format_context(load_result: dict) -> str:
    """将加载结果格式化为 AI 可读上下文"""
    parts = []
    for slug in load_result["order"]:
        skill = next(s for s in load_result["skills"] if s.get("slug") == slug)
        parts.append(f"---\n## Skill: {skill.get('name', slug)} ({slug} v{skill.get('version', '?')})\n")
        parts.append(skill.get("_body", ""))
    return "\n".join(parts)
