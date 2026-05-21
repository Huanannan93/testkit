"""项目索引模型"""
from typing import Optional
from pydantic import BaseModel


class ProjectMeta(BaseModel):
    name: str
    domains: list[str] = ["api"]
    repo: str = ""
    created: str = ""
    pinned_skills: dict[str, list[str]] = {}  # domain -> [slug@version]
    knowledge_version: str = ""
    envs: list[str] = []
    ci: str = "github-actions"
