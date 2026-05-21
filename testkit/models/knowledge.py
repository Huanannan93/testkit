"""知识元数据模型"""
from typing import Optional
from pydantic import BaseModel


class KnowledgeMeta(BaseModel):
    uuid: str
    slug: str
    title: str
    category: str = ""
    tags: list[str] = []
    related_skills: list = []
    version: str = "1.0.0"
    visibility: str = "public"
    file_path: str = ""

    @property
    def fq_slug(self) -> str:
        return f"{self.category}/{self.slug}"
