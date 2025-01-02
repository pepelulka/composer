"""
Функции для работы со структурой рабочей директории - ее инициализация и всё такое
"""
from pathlib import Path

from src.internal.services import Service

class WorkingDirectory:
    def __init__(self, path: Path):
        self.path = path
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        self.services_path = path.joinpath('services')
        self.debug_path = path.joinpath('debug')
        self.base_compose_path = path.joinpath('compose.yml')

        self.services_path.mkdir(exist_ok=True)
        self.debug_path.mkdir(exist_ok=True)
        self.base_compose_path.touch()

    def add_compose_files_for_service(self, service: Service):
        compose_name = service.compose_name
        self.services_path.joinpath(f'compose.{compose_name}.yml').touch()
        self.debug_path.joinpath(f'compose.debug.{compose_name}.yml').touch()
