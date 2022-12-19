#!/usr/bin/env python3

"""
This script executes a program.
If the program throws an error, the script generates suggestions
for fixing the error.
"""

import sys
import os
import subprocess

from llmhub.client import Client as LLMClient

LLM = LLMClient("https://www.llmhub.com/2/functions/35/share")

NUMBER_OF_SUGGESTIONS = 9
NUM_ERROR_CHARS = 4000


def get_output(program):
    stderr = None
    stdout = None

    # Run the program and capture its output
    with open(os.devnull, "w") as devnull:
        try:
            # Get the stderr and the stdout of the program program.
            stdout = subprocess.check_output(
                program, stderr=subprocess.STDOUT, shell=True
            ).decode("utf-8")
        except subprocess.CalledProcessError as e:
            stderr = e.output.decode("utf-8")

    return stdout, stderr


def main(argv):
    if len(argv) < 2:
        print("Usage: %s <program>" % argv[0])
        sys.exit(1)

    program = " ".join(argv[1:])

    stdout, stderr = get_output(program)
    print("stderr:", stderr)

    # If the program didn't crash, exit
    if not stderr:
        print("No stderr, exiting")
        sys.exit(0)

    suggestions = [LLM.run({
        "error": stderr[-NUM_ERROR_CHARS:]
    })["output"] for i in range(NUMBER_OF_SUGGESTIONS)]

    # f'Step by step instructions on how to fix the issue:\n' \

    suggestion_num = 0
    for suggestion in suggestions:
        if suggestion.strip() == "":
            continue

        suggestion_num += 1
        block_char = "─"
        print(f"{block_char * 40}", end="")

        print(f"  {suggestion_num}. Suggestion:")
        print(f"\033[92m{suggestion.strip()}\033[0m")
        print()


if __name__ == "__main__":
    main(sys.argv)
