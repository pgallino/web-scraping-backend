from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ScrapeRequest:
    url: str
    selectors: Dict[str, str]
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[float] = 10.0


@dataclass
class ScrapeResult:
    url: str
    data: Dict[str, List[str]]
    meta: Optional[Dict[str, Any]] = None


__all__ = ["ScrapeRequest", "ScrapeResult"]
