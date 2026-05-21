"""配置驱动的仓库管理器"""
import subprocess
from pathlib import Path
from testkit.config import Config, DEFAULT_CONFIG


class RepoManager:
    def __init__(self, config: Config):
        self.config = config

    def repo_dir(self, name: str) -> Path:
        return self.config.workspace / name

    def init_all(self):
        """初始化所有仓库（clone）"""
        from testkit.workspace import clone_repo
        self.config.workspace.mkdir(parents=True, exist_ok=True)
        results = {}
        for name, repo in self.config.repos.items():
            target = self.repo_dir(name)
            results[name] = clone_repo(name, repo.url, target)
        return results

    def update_all(self):
        """更新所有仓库（pull）"""
        from testkit.workspace import pull_repo
        for name in self.config.repos:
            pull_repo(name, self.repo_dir(name))

    def get_repo_path(self, repo_type: str) -> Path:
        """根据类型获取仓库路径"""
        for name, repo in self.config.repos.items():
            if repo.type == repo_type:
                return self.repo_dir(name)
        raise ValueError(f"未找到类型为 {repo_type} 的仓库")

    def update_index(self):
        """重建所有仓库的 index.json"""
        from testkit.core.scanner import Scanner
        scanner = Scanner()
        for name in self.config.repos:
            repo_path = self.repo_dir(name)
            if repo_path.exists():
                index_path = repo_path / "index.json"
                scanner.scan_and_save_index(repo_path, index_path)
