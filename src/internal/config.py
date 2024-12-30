"""
Функции для работы с конфиг файлом - его чтением, изменением, созданием и удалением
"""
import os.path

import yaml
from pathlib import Path
from typing import List

from internal.services import Service, topological_sort

"""
Структура конфиг файла:

services:
  serv1:
    compose_name: service1
  serv2:
    compose_name: service2
    depends_on:
      - serv1
"""
class ConfigFile:
    def __init__(self, path: Path):
        self.path = path
        # Создаём файл (со всеми родительскими директориями), если не существует
        if not os.path.exists(path):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            with open(path, 'w') as f:
                f.write('services:\n')

    def parse(self) -> (str | None, List[Service] | None):
        services = []
        with open(self.path, 'r') as f:
            try:
                data = yaml.safe_load(f)
                if data is None:
                    return "Error while parsing config file: file is empty", None
                if 'services' not in data.keys():
                    return "Error while parsing config file: no services section in config file", None
                if data['services'] is None:
                    return None, []
                for service_name, service_info in data['services'].items():
                    services.append(Service(
                        short_name=service_name,
                        compose_name=service_info['compose_name'],
                        depends_on=([] if 'depends_on' not in service_info else service_info['depends_on'])
                    ))
            except KeyError as e:
                return f"Key error while parsing config file: {e}", None
            except Exception as e:
                return f"Error while parsing config file...", None
        return None, services

    # returns (err, result) in golang-like style
    # result is topologically sorted
    @staticmethod
    def validate(services: List[Service]) -> (str | None, List[Service] | None):
        services_list = [s.short_name for s in services]
        # 1. Проверяем, что сервисы зависят только от существующих сервисов
        for service in services:
            undefined_services = list(filter(lambda x : x not in services_list, service.depends_on))
            if undefined_services:
                return f"Config file has undefined services in dependencies, for example: {undefined_services[0]}", None
        # 2. Проверяем что нет циклических зависимостей, делаем топологическую сортировку
        err, result = topological_sort(services)
        if err is not None:
            return f"Config file validation error: {err}"
        return None, result

    def parse_and_validate(self) -> (str | None, List[Service] | None):
        err, res = self.parse()
        if err is not None:
            return err, None
        err, res = self.validate(res)
        if err is not None:
            return err, None
        return None, res

    def list_all_services(self) -> (str | None, List[Service] | None):
        return self.parse_and_validate()

    def dump_into_file(self, services: List[Service]):
        if not services:
            data = {'services': None}
        else:
            data = {'services': {} }
            for service in services:
                data['services'][service.short_name] = {
                    'compose_name': service.compose_name
                }
                if service.depends_on:
                    data['services'][service.short_name]['depends_on'] = service.depends_on
        with open(self.path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)


    # Return None if success
    def try_add(self, service: Service) -> str | None:
        err, res = self.parse_and_validate()
        if err is not None:
            return err
        res.append(service)
        err, _ = self.validate(res)
        if err is not None:
            return err
        try:
            self.dump_into_file(res)
        except Exception as e:
            return f'{e}'
        return None


    @classmethod
    def exists(cls, path: Path):
        return os.path.exists(path)
