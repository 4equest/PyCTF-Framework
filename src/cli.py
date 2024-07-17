import argparse
import sys
import os
import glob
from io import StringIO
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import Completer, Completion, WordCompleter, NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style

from workspace.manager import create_workspace, save_workspace, load_workspace_unsafe, save_workspace_unsafe
from workspace.workspace import WorkSpace

current_workspace = None

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(None, message)

    def print_help(self, file=None):
        super().print_help(file)

def set_workspace_name(name):
    global current_workspace_name
    current_workspace_name = name

def get_or_load_workspace(workspace_name):
    global current_workspace
    if current_workspace is None or current_workspace.workspace_name != workspace_name:
        current_workspace = load_workspace_unsafe(workspace_name)
    return current_workspace

def create_workspace_cmd(args):
    global current_workspace
    set_workspace_name(args.name)
    current_workspace = create_workspace(args.name)
    save_workspace_unsafe(current_workspace, args.name)
    print(f"Workspace '{args.name}' created and saved.")
    workspace = get_files('./workspace')
    return workspace

def load_workspace_cmd(args):
    global current_workspace
    current_workspace = get_or_load_workspace(args.name)
    print(f"Workspace '{args.name}' loaded.")

def save_workspace_cmd(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        current_workspace = create_workspace("No workspace")
    save_workspace_unsafe(current_workspace, current_workspace.workspace_name)
    print(f"Workspace '{current_workspace.workspace_name}' saved.")

def list_modules(args):
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    modules = current_workspace.get_module_list()
    for module in modules:
        print(module)

def list_recipes(args):
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    recipes = current_workspace.get_recipe_list()
    for recipe in recipes:
        print(recipe)

def module_info(args):
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    info = current_workspace.get_module_info(args.module_name)
    if info:
        print(info)
    else:
        print(f"Module '{args.module_name}' not found.")

def recipe_info(args):
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    info = current_workspace.get_recipe_info(args.recipe_name)
    if info:
        print(info)
    else:
        print(f"Recipe '{args.recipe_name}' not found.")

def run_module(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    if not args.module_name:
        print("Error: module_name is required.")
        return
    module_id = current_workspace.run_module(args.module_name, args.args)
    result = current_workspace.get_module_result(module_id)
    print(f"Module '{args.module_name}' executed with result: {result}")

def run_recipe(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    if not args.recipe_name:
        print("Error: recipe_name is required.")
        return
    recipe_id = current_workspace.run_recipe(args.recipe_name, args.args)
    result = current_workspace.get_recipe_result(recipe_id)
    print(f"Recipe '{args.recipe_name}' executed with result: {result}")

def run_os_command(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        current_workspace = create_workspace("No workspace")
        return
    cmd_id = current_workspace.run_cmd(args.args)
    result = current_workspace.get_cmd_result(cmd_id)
    print(f"Command executed with result: {result}")

def parse_command(command):
    if command.startswith("!"):
        cmd_args = command[1:].split()
        run_os_command(argparse.Namespace(args=cmd_args))
    else:
        print("Invalid command")

""" def get_json_files(directory):
    return [os.path.basename(f) for f in glob.glob(os.path.join(directory, '*.json'))] """

def get_files(directory):
    return [os.path.basename(f) for f in glob.glob(os.path.join(directory, '*'))]

def get_module_list():
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    list_modules(None)
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    return output.splitlines()

def get_recipe_list():
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    list_recipes(None)
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    return output.splitlines()

def start_interactive(parser):
    modules = get_module_list()
    recipes = get_recipe_list()
    workspaces = get_files('./workspace')

    completer = NestedCompleter.from_nested_dict({
        'create': None,
        'load': {workspace: None for workspace in workspaces},
        'run': {
            'module': {module: None for module in modules},
            'recipe': {recipe: None for recipe in recipes},
            'cmd': {
                'ls': None, 
            }
        },
        'list': {
            'module': None,
            'recipe': None,
        },
        'info': {
            'module': {module: None for module in modules},
            'recipe': {recipe: None for recipe in recipes},
        },
        'save': None,
        'exit': None,
        'quit': None,
    })
    
    session = PromptSession(history=InMemoryHistory(), completer=completer)

    style = Style.from_dict({
        'prompt': 'ansiblue',
        'rprompt': 'bg:#fD0DD0 #ffffff',
    })
    
    def status_line():
        return 'To exit Ctrl+C or type "exit" or "quit"'
    
    while True:
        try:
            workspace_name = current_workspace.workspace_name if current_workspace else "No workspace"
            command = session.prompt(f'{workspace_name}> ', bottom_toolbar=status_line, style=style)
            if command.strip().lower() in ['exit', 'quit']:
                break
            args = parser.parse_args(command.split())
            if hasattr(args, 'func'):
                args.func(args)
            else:
                print(f"Invalid command: {command}")
        except argparse.ArgumentError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    parser = CustomArgumentParser(description="CLI for workspace management and execution.")
    subparsers = parser.add_subparsers()

    parser_create = subparsers.add_parser('create', help='Create a new workspace')
    parser_create.add_argument('name', type=str, help='The name of the workspace to create')
    parser_create.set_defaults(func=create_workspace_cmd)

    parser_load = subparsers.add_parser('load', help='Load an existing workspace')
    parser_load.add_argument('name', type=str, help='The name of the workspace to load')
    parser_load.set_defaults(func=load_workspace_cmd)

    parser_save = subparsers.add_parser('save', help='Save the current workspace')
    parser_save.set_defaults(func=save_workspace_cmd)

    parser_info = subparsers.add_parser('info', help='Get info about a specific entity')
    info_subparsers = parser_info.add_subparsers(dest='info_type')

    parser_module_info = info_subparsers.add_parser('module', help='Get info about a specific module')
    parser_module_info.add_argument('module_name', type=str, help='The name of the module')
    parser_module_info.set_defaults(func=module_info)

    parser_recipe_info = info_subparsers.add_parser('recipe', help='Get info about a specific recipe')
    parser_recipe_info.add_argument('recipe_name', type=str, help='The name of the recipe')
    parser_recipe_info.set_defaults(func=recipe_info)

    parser_run = subparsers.add_parser('run', help='Run a specific entity')
    run_subparsers = parser_run.add_subparsers(dest='run_type')

    parser_run_module = run_subparsers.add_parser('module', help='Run a specific module')
    parser_run_module.add_argument('module_name', type=str, help='The name of the module')
    parser_run_module.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the module')
    parser_run_module.set_defaults(func=run_module)

    parser_run_recipe = run_subparsers.add_parser('recipe', help='Run a specific recipe')
    parser_run_recipe.add_argument('recipe_name', type=str, help='The name of the recipe')
    parser_run_recipe.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the recipe')
    parser_run_recipe.set_defaults(func=run_recipe)

    parser_run_os_command = run_subparsers.add_parser('cmd', help='Run an OS command')
    parser_run_os_command.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the command')
    parser_run_os_command.set_defaults(func=run_os_command)

    parser_list = subparsers.add_parser('list', help='List specific entities')
    list_subparsers = parser_list.add_subparsers(dest='list_type')

    parser_list_modules = list_subparsers.add_parser('module', help='List all modules')
    parser_list_modules.set_defaults(func=list_modules)

    parser_list_recipes = list_subparsers.add_parser('recipe', help='List all recipes')
    parser_list_recipes.set_defaults(func=list_recipes)

    if len(sys.argv) == 1:
        start_interactive(parser)
    else:
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parse_command(' '.join(sys.argv[1:]))

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "load" and len(sys.argv) == 3:
            args = argparse.Namespace(name=sys.argv[2])
            load_workspace_cmd(args=args)

if __name__ == "__main__":
    main()

