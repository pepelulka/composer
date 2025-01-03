import subprocess

class DockerCompose:
    @staticmethod
    def up(args, detach=False):
        cmdline = ["docker-compose"]
        for arg in args:
            cmdline += ["-f", arg]
        cmdline.append("up")
        if detach:
            cmdline.append("-d")
        print(cmdline)
        subprocess.call(cmdline)

    @staticmethod
    def down(args, force=False, volume=False):
        cmdline = ["docker-compose"]
        for arg in args:
            cmdline += ["-f", arg]
        cmdline.append("down")
        if force:
            cmdline += ["-t", "0"]
        if volume:
            cmdline.append("-v")
        print(cmdline)
        subprocess.call(cmdline)

    @staticmethod
    def build(args):
        cmdline = ["docker-compose"]
        for arg in args:
            cmdline += ["-f", arg]
        cmdline.append("build")
        print(cmdline)
        subprocess.call(cmdline)
