import sys

from src.internal.config import ConfigFile
from src.internal.docker import DockerCompose
from src.internal.services import services_pretty_print, Service, resolve_dependencies_str
from src.internal.settings import WORKDIR, CURRENT_CFG
from src.internal.workdir import WorkingDirectory

from typing import List
from collections.abc import Callable


# =========================
# Util functions:

def abort_if_cfg_file_doesnt_exist():
    if not ConfigFile.exists(CURRENT_CFG):
        print("composer error: No config file found in the current directory")
        sys.exit(1)

def existed_workdir_init() -> (ConfigFile, List[Service], WorkingDirectory):
    cfg = ConfigFile(CURRENT_CFG)
    wd = WorkingDirectory(WORKDIR)
    err, res = cfg.list_all_services()
    if err is not None:
        print(err)
        sys.exit(1)
    return cfg, res, wd

# Проверяет все ли сервисы определены, удаляет дубликаты и разрешает зависимости
def filter_args(args, services, abort_if_undefined=True, remove_duplicated=True, resolve_deps=True):
    services_dict = {service.short_name: service for service in services}
    services_not_found = [x for x in services if x.short_name not in services_dict.keys()]
    if services_not_found and abort_if_undefined:
        print(f"Services not found in config: {', '.join(services_not_found)}")
        sys.exit(1)

    if remove_duplicated:
        args_copy = list(set(args))
    else:
        args_copy = args.copy()

    if resolve_deps:
        args_copy = resolve_dependencies_str(args_copy, services)

    return args_copy

def args_to_docker_compose_args(args, debug=False):
    base_compose_path = WORKDIR.joinpath('compose.yml')
    compose_args = [str(base_compose_path)]
    for arg in args:
        service_path = WORKDIR.joinpath(f'services/compose.{arg.compose_name}.yml')
        debug_path = WORKDIR.joinpath(f'debug/compose.debug.{arg.compose_name}.yml')
        compose_args.append(str(service_path))
        if debug and debug_path.exists():
            compose_args.append(str(debug_path))
    return compose_args

# =========================
# Command handler functions:

def command_for_all(command_func: Callable[..., None]):
    def wrapper(*args, **kwargs):
        abort_if_cfg_file_doesnt_exist()
        cfg, services, _ = existed_workdir_init()
        command_func([service.short_name for service in services], *args, **kwargs)

    return wrapper

class Command:
    @staticmethod
    def init():
        _ = WorkingDirectory(WORKDIR)
        _ = ConfigFile(CURRENT_CFG)

    @staticmethod
    def list():
        abort_if_cfg_file_doesnt_exist()
        cfg = ConfigFile(CURRENT_CFG)
        err, res = cfg.list_all_services()
        if err is not None:
            print(err)
        else:
            services_pretty_print(res)

    @staticmethod
    def add():
        abort_if_cfg_file_doesnt_exist()
        cfg, res, wd = existed_workdir_init()
        print("Let's create new service. List of existing services:")
        services_pretty_print(res)
        new_service = Service(
            short_name="",
            compose_name="",
            depends_on=[]
        )

        while True:
            print("Enter short name for service:")
            new_service.short_name = input().strip()
            print("Enter compose name for service:")
            new_service.compose_name = input().strip()
            print("Enter list of services your new service depends on (in following format: 'serv1,serv2,serv3') [Optional] :")
            new_service.depends_on = list(map(
                lambda x : x.strip(), # Split by ',' symbol and then strip
                input().split(',')
            ))
            new_service.depends_on = list(filter(lambda x : x != '', new_service.depends_on))

            print("Your service here:")
            services_pretty_print([new_service])

            ans = ''
            while ans not in ['n', 'y', 'c']:
                print("Are you sure you want to add this service? [y(Yes)/n(No)/c(Cancel)] ", end='')
                ans = input()

            if ans == 'c':
                print("Aborting...")
                return
            if ans == 'n':
                continue
            if ans == 'y':
                break

        err = cfg.try_add(new_service)
        if err is None:
            wd.add_compose_files_for_service(new_service)
            print('Success!')
        else:
            print(f'Error: {err}')

    @staticmethod
    def up(args, debug, detach):
        abort_if_cfg_file_doesnt_exist()
        cfg, services, _ = existed_workdir_init()

        final_args = filter_args(args, services)

        compose_args = args_to_docker_compose_args(final_args, debug=debug)

        # Наконец-то долгожданный вызов
        DockerCompose.up(compose_args, detach)

    @staticmethod
    def up_all(debug, detach):
        return command_for_all(Command.up)(debug, detach)

    @staticmethod
    def down(args, force, volume):
        abort_if_cfg_file_doesnt_exist()
        cfg, services, _ = existed_workdir_init()

        final_args = filter_args(args, services)

        compose_args = args_to_docker_compose_args(final_args, debug=False)

        # Наконец-то долгожданный вызов
        DockerCompose.down(compose_args, force, volume)

    @staticmethod
    def down_all(force, volume):
        return command_for_all(Command.down)(force, volume)

    @staticmethod
    def build(args):
        abort_if_cfg_file_doesnt_exist()
        cfg, services, _ = existed_workdir_init()

        final_args = filter_args(args, services)

        compose_args = args_to_docker_compose_args(final_args, debug=False)

        DockerCompose.build(compose_args)

    @staticmethod
    def build_all():
        return command_for_all(Command.build)()
