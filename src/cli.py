import argparse
import sys
import os
import glob
import datetime
import traceback
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import Completer, Completion, WordCompleter, NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.prompt import IntPrompt
from rich.panel import Panel

from workspace.manager import create_workspace, save_workspace, load_workspace_unsafe, save_workspace_unsafe
from workspace.workspace import WorkSpace

current_workspace = None

class HelpRequested(Exception):
    pass

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(None, message)

    def print_help(self, file=None):
        help_text = self.format_help()
        help_text = help_text.replace("show this help message and exit", "show this help message")
        if file is None:
            file = sys.stdout
        file.write(help_text)
        raise HelpRequested()

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
    Console().print(f"[green]Workspace '{args.name}' created and saved.[/green]")
    workspace = get_files('./workspace')
    return workspace

def load_workspace_cmd(args):
    global current_workspace
    current_workspace = get_or_load_workspace(args.name)
    Console().print(f"[green]Workspace '{args.name}' loaded.[/green]")

def save_workspace_cmd(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        current_workspace = create_workspace("No workspace")
    save_workspace_unsafe(current_workspace, current_workspace.workspace_name)
    Console().print(f"[green]Workspace '{current_workspace.workspace_name}' saved.[/green]")

"""
testing now

# workspace.py

def get_recipe_info(self, recipe_name):
    try:
        return Recipe.get_recipe_info(recipe_name)
    except KeyError:
        return "No description available."

def get_module_info(self, module_name):
    try:
        return Module.get_module_info(module_name)
    except KeyError:
        return "No description available."
"""

def list_recipes(args):
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    recipes = current_workspace.get_recipe_list()
    if recipes is None:
        recipes = []

    table = Table(title="Listing Recipes")
    table.add_column("Index", justify="right", style="cyan", no_wrap=True)
    table.add_column("Recipe Name", style="magenta")
    table.add_column("Description", style="green")

    for i, recipe in enumerate(recipes):
        info_str = current_workspace.get_recipe_info(recipe)
        description = info_str.strip() if info_str else 'No description available'
        table.add_row(str(i + 1), recipe, description)

    Console().print(table)
    return recipes

def list_modules(args):
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    modules = current_workspace.get_module_list()
    if modules is None:
        modules = []

    table = Table(title="Listing Modules")
    table.add_column("Module Name", justify="left")
    table.add_column("Description", style="green")

    for module in modules:
        info_str = current_workspace.get_module_info(module)
        description = info_str.strip() if info_str else 'No description available'
        table.add_row(module, description)

    Console().print(table)
    return modules

def module_info(args):
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    info = current_workspace.get_module_info(args.module_name)
    if info:
        Console().print(info)
    else:
        Console().print(f"[red]Module '{args.module_name}' not found.[/red]")

def recipe_info(args):
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    info = current_workspace.get_recipe_info(args.recipe_name)
    if info:
        Console().print(info)
    else:
        Console().print(f"[red]Recipe '{args.recipe_name}' not found.[/red]")

def run_module(args):
    global current_workspace
    if current_workspace is None:
        Console().print("[red]No workspace loaded.[/red]")
        return
    if not args.module_name:
        Console().print("[red]Error: module_name is required.[/red]")
        return
    module_id = current_workspace.run_module(args.module_name, args.args)
    result = current_workspace.get_module_result(module_id)
    Console().print(f"[green]Module '{args.module_name}' executed with result: {result}[/green]")

def run_recipe(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    if not args.recipe_name:
        print("Error: recipe_name is required.")
        return
    print(f"Running recipe: {args.recipe_name} with args: {args.args}")
    recipe_id = current_workspace.run_recipe(args.recipe_name, args.args)
    result = current_workspace.get_recipe_result(recipe_id)
    print(f"Recipe '{args.recipe_name}' executed with result: {result}")

def run_os_command(args):
    Console().print("[red]Warning: This feature is under development.[/red]")
    global current_workspace
    if current_workspace is None:
        Console().print("[red]No workspace loaded.[/red]")
        current_workspace = create_workspace("No workspace")
        return
    cmd_id = current_workspace.run_cmd(args.args)
    result = current_workspace.get_cmd_result(cmd_id)
    Console().print(f"[green]Command executed with result: {result}[/green]")

def parse_command(command):
    if command.startswith("!"):
        cmd_args = command[1:].split()
        run_os_command(argparse.Namespace(args=cmd_args))
    else:
        Console().print("[red]Invalid command[/red]")

def get_files(directory):
    return [os.path.basename(f) for f in glob.glob(os.path.join(directory, '*'))]

def get_module_list():
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    modules = current_workspace.get_module_list()
    if modules is None:
        modules = []
    return modules

def get_recipe_list():
    global current_workspace
    if current_workspace is None:
        current_workspace = create_workspace("No workspace")
    recipes = current_workspace.get_recipe_list()
    return recipes

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
    
    session = PromptSession(history=InMemoryHistory(),auto_suggest=AutoSuggestFromHistory(), completer=completer)
    now = datetime.datetime.now()

    style = Style.from_dict({
        'prompt': 'ansiblue',
        'rprompt': 'bg:#7D7D7D #ffffff',
        'completion-menu.completion': 'bg:#008888 #ffffff',
        'completion-menu.completion.current': 'bg:#00aaaa #000000',
        'scrollbar.background': 'bg:#88aaaa',
        'scrollbar.button': 'bg:#222222',
    })
    
    def status_line():
        return 'To exit Ctrl+C or type "exit" or "quit"'
    
    while True:
        try:
            workspace_name = current_workspace.workspace_name if current_workspace else "No workspace"
            command = session.prompt(f'{workspace_name}> ',rprompt= "%s:%s:%s" % (now.hour, now.minute, now.second), bottom_toolbar=status_line, style=style, mouse_support=True)
            if command.strip().lower() in ['exit', 'quit']:
                break
            args = parser.parse_args(command.split())
            if hasattr(args, 'func'):
                args.func(args)
            else:
                print(f"Invalid command: {command}")
        except HelpRequested:
            continue
        except argparse.ArgumentError as e:
            # print(f"Error: {e}")
            traceback.print_exc()

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

