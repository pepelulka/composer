import argparse

from src.internal.commands import Command

ACTION_LIST = [
    'init',
    'list',
    'add',
    'up',
    'down',
    'build',
    'up-all',
    'down-all',
    'build-all'
]

def parse_args():
    parser = argparse.ArgumentParser(
        prog="composer",
        description="Tool to manage docker compose files",
        epilog=""
    )
    parser.add_argument(
        'action',
        choices=ACTION_LIST
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
        Command.init()
    elif args.action == 'list':
        Command.list()
    elif args.action == 'add':
        Command.add()
    elif args.action == 'up':
        Command.up(args.args, args.debug, args.detach)
    elif args.action == 'build':
        Command.build(args.args)
    elif args.action == 'up-all':
        Command.up_all(args.debug, args.detach)
    elif args.action == 'down-all':
        Command.down_all(args.force, args.volume)
    elif args.action == 'build-all':
        Command.build_all()

if __name__ == "__main__":
    main()
