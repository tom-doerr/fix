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
import openai
import configparser


MAX_NUM_TOKENS = 100
FREQUENCY_PENALTY = 2
NUMBER_OF_SUGGESTIONS = 9
SEPERATOR_STR = '==========================================================\n'
STOP_STR = '==============='

CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')


def create_template_ini_file():
    """
    If the ini file does not exist create it and add the organization_id and
    secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        with open(API_KEYS_LOCATION, 'w') as f:
            f.write('[openai]\n')
            f.write('organization_id=\n')
            f.write('secret_key=\n')

        print('OpenAI API config file created at {}'.format(API_KEYS_LOCATION))
        print('Please edit it and add your organization ID and secret key')
        print('If you do not yet have an organization ID and secret key, you\n'
               'need to register for OpenAI Codex: \n'
                'https://openai.com/blog/openai-codex/')
        sys.exit(1)


def initialize_openai_api():
    """
    Initialize the OpenAI API
    """
    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")



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
    response = openai.Completion.create(engine='davinci-codex', prompt=input_prompt, temperature=0.5, max_tokens=MAX_NUM_TOKENS, stop=STOP_STR, n=NUMBER_OF_SUGGESTIONS, frequency_penalty=FREQUENCY_PENALTY)
    suggestions = [e['text'] for e in response['choices']]
    return suggestions

def main(argv):
    initialize_openai_api()
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
            f'Fix for the above error:\n' \
            f''

            # f'Step by step instructions on how to fix the issue:\n' \

    suggestions = get_suggestions(input_prompt)
    suggestion_num = 0
    for suggestion in suggestions:
        if suggestion.strip() == '':
            continue

        suggestion_num += 1
        block_char = '─'
        print(f'{block_char * 40}', end='')

        print(f'  {suggestion_num}. Suggestion:')
        print(f'\033[92m{suggestion.strip()}\033[0m')
        print()


if __name__ == "__main__":
    main(sys.argv)
