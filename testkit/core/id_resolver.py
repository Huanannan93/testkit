"""UUID/slug ↔ 路径解析器，兼容旧引用"""
from pathlib import Path


class IDResolver:
    def __init__(self, index: dict[str, dict] = None):
        self._uuid_map: dict[str, str] = {}  # uuid → file_path
        self._slug_map: dict[str, str] = {}  # slug → file_path
        self._load_index(index or {})

    def _load_index(self, index: dict[str, dict]):
        for file_path, meta in index.items():
            if meta.get("uuid"):
                self._uuid_map[meta["uuid"]] = file_path
            if meta.get("slug"):
                self._slug_map[meta["slug"]] = file_path

    def resolve(self, ref: str, ref_type: str = "slug") -> str:
        """解析引用，返回文件路径"""
        if ref_type == "uuid":
            return self._uuid_map.get(ref, "")
        return self._slug_map.get(ref, ref)  # slug 未命中则回退为原始路径
