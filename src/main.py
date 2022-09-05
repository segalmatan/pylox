import argparse
import pprint

from scanner import Scanner

def report_error(line, where, message):
    print(f"ERROR [line {line}] {where}, {message}")


def run(stream):
    pprint.pprint(list(Scanner(stream).tokens()))


def main():
    parser = argparse.ArgumentParser(description="Lox programming language interpreter")
    parser.add_argument("script_path", nargs="?", help="File containing Lox code")

    args = parser.parse_args()

    if args.script_path:
        run(open(args.script_path, "rb").read())
    else:
        while True:
            line = input("> ")
            if line == "exit":
                break
            else:
                run(line)


if __name__ == "__main__":
    main()