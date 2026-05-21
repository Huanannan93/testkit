"""统一依赖引用模型"""
from typing import Optional
from pydantic import BaseModel


class DepRef(BaseModel):
    ref_type: str       # "skill" | "knowledge" | "script" | "template"
    target_uuid: Optional[str] = None
    target_slug: str
    version_hint: str = ""
    optional: bool = False  # True=软依赖（缺失告警），False=硬依赖（缺失报错）


def parse_ref(raw: dict | str) -> DepRef:
    """解析依赖引用，兼容字符串和字典两种格式"""
    if isinstance(raw, str):
        # 简单格式: "skill:api-basics@>=1.0"
        ref_type, rest = raw.split(":", 1)
        if "@" in rest:
            slug, ver = rest.split("@", 1)
            return DepRef(ref_type=ref_type, target_slug=slug, version_hint=f"@{ver}")
        return DepRef(ref_type=ref_type, target_slug=rest)
    return DepRef(**raw)
