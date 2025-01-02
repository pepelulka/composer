import sys

from src.internal.config import ConfigFile
from src.internal.docker import docker_compose_up
from src.internal.services import services_pretty_print, Service, resolve_dependencies_str
from src.internal.settings import WORKDIR, CURRENT_CFG
from src.internal.workdir import WorkingDirectory

# Util functions:
def abort_if_cfg_file_doesnt_exist():
    if not ConfigFile.exists(CURRENT_CFG):
        print("composer error: No config file found in the current directory")
        sys.exit(1)

# Commands handlers:
def command_init():
    _ = WorkingDirectory(WORKDIR)
    _ = ConfigFile(CURRENT_CFG)

def command_list():
    abort_if_cfg_file_doesnt_exist()
    cfg = ConfigFile(CURRENT_CFG)
    err, res = cfg.list_all_services()
    if err is not None:
        print(err)
    else:
        services_pretty_print(res)

def command_add():
    abort_if_cfg_file_doesnt_exist()
    cfg = ConfigFile(CURRENT_CFG)
    wd = WorkingDirectory(WORKDIR)
    err, res = cfg.list_all_services()
    if err is not None:
        print(err)
        return
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

def command_up(args, debug, detach):
    abort_if_cfg_file_doesnt_exist()
    cfg = ConfigFile(CURRENT_CFG)
    err, services = cfg.list_all_services()
    if err is not None:
        print(err)
        return
    services_dict = {service.short_name: service for service in services}
    services_not_found = [x for x in services if x.short_name not in services_dict.keys()]
    if services_not_found:
        print(f"Services not found in config: {', '.join(services_not_found)}")
        return
    args_without_duplicates = list(set(args))
    final_args = resolve_dependencies_str(args_without_duplicates, services)

    # Собираем теперь аргументы для docker-compose up
    base_compose_path = WORKDIR.joinpath('compose.yml')
    compose_args = [str(base_compose_path)]
    for arg in final_args:
        service_path = WORKDIR.joinpath(f'services/compose.{arg.compose_name}.yml')
        debug_path = WORKDIR.joinpath(f'debug/compose.debug.{arg.compose_name}.yml')
        compose_args.append(str(service_path))
        if debug and debug_path.exists():
            compose_args.append(str(debug_path))

    # Наконец-то долгожданный вызов
    docker_compose_up(compose_args, detach)
