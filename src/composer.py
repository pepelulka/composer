import argparse

from internal.commands import (
    command_up,
    command_add,
    command_list,
    command_init
)

def parse_args():
    parser = argparse.ArgumentParser(
        prog="composer",
        description="Tool to manage docker compose files",
        epilog=""
    )
    parser.add_argument(
        'action',
        choices=[
            'init',
            'list',
            'add',
            'up',
            'up-all',

        ]
    )
    parser.add_argument("args", nargs="*")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-D", "--detach", action="store_true")
    parser.add_argument("-f", "--force", action="store_true")
    parser.add_argument("-v", "--volume", action="store_true")

    return parser.parse_args()

def main():
    args = parse_args()
    if args.action == 'init':
        command_init()
    elif args.action == 'list':
        command_list()
    elif args.action == 'add':
        command_add()
    elif args.action == 'up':
        command_up(args.args, args.debug, args.detach)

if __name__ == "__main__":
    main()
