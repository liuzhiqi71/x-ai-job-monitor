from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class StateStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._state = {"queries": {}}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self._state = {"queries": {}}
            return
        with self.path.open("r", encoding="utf-8") as handle:
            self._state = json.load(handle)
        self._state.setdefault("queries", {})

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self._state, handle, ensure_ascii=False, indent=2)

    def get_since_id(self, query_name: str) -> Optional[str]:
        query_state = self._state.get("queries", {}).get(query_name, {})
        return query_state.get("since_id")

    def set_since_id(self, query_name: str, since_id: Optional[str]) -> None:
        if not since_id:
            return
        self._state.setdefault("queries", {})
        self._state["queries"].setdefault(query_name, {})
        self._state["queries"][query_name]["since_id"] = since_id

    @property
    def raw_state(self) -> Dict[str, object]:
        return self._state

