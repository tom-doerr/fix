#!/usr/bin/env python3

"""
This script executes a program.
If the program throws an error, the script generates suggestions 
for fixing the error.
"""

import sys
import os
import subprocess
import json
import re
import pickle
import time
import random
from AUTH import *
import openai


MAX_NUM_TOKENS = 100
SEPERATOR_STR = '==========================================================\n'
STOP_STR = '==============='

def get_output(program):
    stderr = None
    stdout = None

    # Run the program and capture its output
    with open(os.devnull, 'w') as devnull:
        try:
            # Get the stderr and the stdout of the program program.
            stdout = subprocess.check_output(program,  stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            stderr =  e.output.decode('utf-8')

    return stdout, stderr


def get_suggestions(input_prompt):
    response = openai.Completion.create(engine='davinci-codex', prompt=input_prompt, temperature=0.5, max_tokens=MAX_NUM_TOKENS, stop=STOP_STR, n=6)
    suggestions = [e['text'] for e in response['choices']]
    return suggestions

def main(argv):
    if len(argv) < 2:
        print("Usage: %s <program>" % argv[0])
        sys.exit(1)

    program = ' '.join(argv[1:])


    stdout, stderr = get_output(program)
    print("stderr:", stderr)

    # If the program didn't crash, exit
    if not stderr:
        print("No stderr, exiting")
        sys.exit(0)


    input_prompt = \
            f'{SEPERATOR_STR}' \
            f'Error:\n' \
            f'\n' \
            f'{stderr}' \
            f'\n' \
            f'{SEPERATOR_STR}' \
            f'Fix:\n' \
            f'\n' \
            f''

    suggestions = get_suggestions(input_prompt)
    suggestion_num = 0
    for suggestion in suggestions:
        if suggestion.strip() == '':
            continue

        suggestion_num += 1
        print('=================================', end='')
        print(f'  {suggestion_num}. Suggestion:')
        # Same text as above, but colored green
        print(f'\033[92m{suggestion}\033[0m')
        # print(suggestion)


if __name__ == "__main__":
    main(sys.argv)
