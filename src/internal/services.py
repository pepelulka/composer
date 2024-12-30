"""
Функции для работы с внутренним представлением "сервиса"
"""
from dataclasses import dataclass
from typing import List
from enum import Enum
import prettytable

@dataclass
class Service:
    short_name: str
    compose_name: str
    depends_on: List[str]

def services_pretty_print(services: List[Service]):
    table = prettytable.PrettyTable()
    table.field_names = [
        "Short name",
        "Compose name",
        "Dependencies",
    ]
    for service in services:
        table.add_row(
            [service.short_name, service.compose_name, ", ".join(service.depends_on)]
        )
    print(table)


# Class for topological sort
class _NodeState(Enum):
    WHITE = 0
    GRAY = 1
    BLACK = 2

def _dfs(current: str, services_dict, result_stack, visited) -> bool:
    visited[current] = _NodeState.GRAY
    for dep in services_dict[current].depends_on:
        if visited[dep] == _NodeState.BLACK:
            continue
        if visited[dep] == _NodeState.GRAY:
            return False
        if not _dfs(dep, services_dict, result_stack, visited):
            return False
    visited[current] = _NodeState.BLACK
    result_stack.append(services_dict[current])
    return True

# Returns (err, result) in golang-style
def topological_sort(services: List[Service]) -> (str | None, List[Service] | None):
    services_dict = {service.short_name: service for service in services}
    visited = {service: _NodeState.WHITE for service in services_dict.keys()}
    result_stack = []
    for node in services_dict.keys():
        if visited[node] == _NodeState.WHITE:
            dfs_result = _dfs(node, services_dict, result_stack, visited)
            if not dfs_result:
                return "Negative cycle found", None
    return None, result_stack

# Resolving dependencies
def resolve_dependencies_str(my_services_str: List[str], all_services: List[Service]) -> List[Service]:
    all_services_dict = {service.short_name: service for service in all_services}
    my_services = [all_services_dict[name] for name in my_services_str]
    visited = {service.short_name: _NodeState.WHITE for service in all_services}
    result_stack = []
    for service in my_services:
        node = service.short_name
        if visited[node] == _NodeState.WHITE:
            _dfs(node, all_services_dict, result_stack, visited)
    return result_stack
