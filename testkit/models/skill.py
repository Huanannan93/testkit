"""技能元数据模型"""
from typing import Optional
from pydantic import BaseModel


class SkillMeta(BaseModel):
    uuid: str
    slug: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    category: str = "general"
    depends_on: list = []
    tags: list[str] = []
    author: str = ""
    visibility: str = "public"
    deprecated: bool = False
    replaced_by: Optional[str] = None
    aliases: list[str] = []
    semantic_keywords: list[str] = []
    file_path: str = ""  # 文件系统路径，Scanner 扫描后填充

    @property
    def is_active(self) -> bool:
        return not self.deprecated

    @property
    def fq_slug(self) -> str:
        """完全限定名: category/slug"""
        return f"{self.category}/{self.slug}"
