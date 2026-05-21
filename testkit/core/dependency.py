"""依赖图构建、拓扑排序、环检测 (Kahn 算法)"""
from collections import defaultdict, deque
from testkit.models.dep_ref import DepRef


class DependencyError(Exception):
    pass


def topological_sort(nodes: list[tuple[str, list[DepRef]]]) -> list[str]:
    """
    Kahn 算法：一次完成环检测 + 拓扑排序
    输入: [(node_id, [DepRef, ...]), ...]
    输出: 拓扑有序的 node_id 列表
    抛出: DependencyError 若存在环
    """
    # 构建邻接表和入度
    adj = defaultdict(list)
    indegree = defaultdict(int)
    all_nodes = set()

    for nid, deps in nodes:
        all_nodes.add(nid)
        indegree.setdefault(nid, 0)
        for dep in deps:
            if not dep.optional:  # 可选依赖不影响拓扑
                adj[nid].append(dep.target_slug)
                indegree[dep.target_slug] = indegree.get(dep.target_slug, 0) + 1

    # 零入度节点入队
    queue = deque([nid for nid in all_nodes if indegree.get(nid, 0) == 0])
    result = []

    while queue:
        nid = queue.popleft()
        result.append(nid)
        for neighbor in adj.get(nid, []):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(all_nodes):
        # 存在环，找出环中节点
        remaining = all_nodes - set(result)
        raise DependencyError(f"检测到循环依赖，涉及: {', '.join(sorted(remaining))}")

    return result


def resolve_load_order(skills: dict[str, list[DepRef]]) -> list[str]:
    """解析技能加载顺序"""
    nodes = [(slug, deps) for slug, deps in skills.items()]
    return topological_sort(nodes)
