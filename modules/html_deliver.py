from modules.paths import Path

from typing import Any


PAGES_PATH = Path("./web/")
COMPONENTS_PATH = Path("./web/static/components/")


def _hydrate(content: str, data: dict) -> str:
    for key, value in data.items():
        content = content.replace("{{" + key + "}}", str(value))
    return content


class Component:
    def __init__(self, pathname: str, codename: str = None) -> None:
        if not codename:
            codename = pathname
        
        self.codename = f"[!{codename.upper()}]"
        self.path = COMPONENTS_PATH + pathname + ".html"            
        self.content = self.path.read()
        
    def hydrate(self, data: dict[str, Any]) -> str:
        content = self.path.read()
        self.content = _hydrate(content, data)
        return self

    def get(self) -> str:
        return self.content


class PageContent:
    def __init__(self, name: str):
        self.filename = name + ".html"
        self.path = PAGES_PATH + self.filename
        self.content = self.path.read()
    
    def hydrate(self, components: list[Component] = None, data_fields: dict[str, Any] = None) -> str:
        """ Add all components and data_fields. Returns ready HTML. """
        if components is None:
            components = []
        if data_fields is None:
            data_fields = {}
        
        for component in components:
            self.content = self.content.replace(component.codename, component.get())
            
        if data_fields:
            self.content = _hydrate(self.content, data_fields)
            
        return self.content
        
    def get(self) -> str:
        return self.content
