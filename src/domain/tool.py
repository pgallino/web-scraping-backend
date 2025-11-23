from dataclasses import dataclass
from typing import Optional


@dataclass
class Tool:
    id: int
    name: str
    description: Optional[str]
    link: Optional[str]

    @classmethod
    def from_input(
        cls, name: str, description: Optional[str] = None, link: Optional[str] = None
    ) -> "Tool":
        return cls(id=0, name=name, description=description, link=link)


def build_tool(
    name: str, description: Optional[str] = None, link: Optional[str] = None
) -> Tool:
    return Tool.from_input(name, description, link)
