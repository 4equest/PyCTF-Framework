import argparse
import sys
import os
import glob
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import Completer, Completion, WordCompleter, NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit import HTML
from prompt_toolkit.styles import Style

# Ensure the parent directories are in the path for importing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from workspace.manager import create_workspace, save_workspace, load_workspace_unsafe, save_workspace_unsafe
from workspace.workspace import WorkSpace

current_workspace = None
parser = None

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

def load_workspace_cmd(args):
    global current_workspace
    current_workspace = get_or_load_workspace(args.name)
    print(f"Workspace '{args.name}' loaded.")

def save_workspace_cmd(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    save_workspace_unsafe(current_workspace, current_workspace.workspace_name)
    print(f"Workspace '{current_workspace.workspace_name}' saved.")

def list_modules(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    modules = current_workspace.get_module_list()
    print("Modules:", modules)

def list_recipes(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    recipes = current_workspace.get_recipe_list()
    print("Recipes:", recipes)

def module_info(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    module = current_workspace.get_module(args.module_name)
    if module is None:
        print(f"Module '{args.module_name}' not found.")
        return
    print(f"Module '{args.module_name}': {module.get_info()}")

def recipe_info(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    recipe = current_workspace.get_recipe(args.recipe_name)
    if recipe is None:
        print(f"Recipe '{args.recipe_name}' not found.")
        return
    print(f"Recipe '{args.recipe_name}': {recipe.get_info()}")

def run_module(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    module = current_workspace.get_module(args.module_name)
    if module is None:
        print(f"Module '{args.module_name}' not found.")
        return
    module.run(args.args)
    print(f"Module '{args.module_name}' executed with arguments: {args.args}")

def run_recipe(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    recipe = current_workspace.get_recipe(args.recipe_name)
    if recipe is None:
        print(f"Recipe '{args.recipe_name}' not found.")
        return
    recipe.run(args.args)
    print(f"Recipe '{args.recipe_name}' executed with arguments: {args.args}")

def run_os_command(args):
    os.system(' '.join(args.args))
    print(f"OS command executed: {' '.join(args.args)}")

# class CommandCompleter(Completer):
#     def __init__(self):
#         # self.commands = ['create', 'load', 'save', 'list-modules', 'list-recipes', 'module-info', 'recipe-info', 'run-module', 'run-recipe', 'run-cmd', 'exit']
#         self.commands = ['create', 'load', 'save', 'list-modules', 'list-recipes', 'module-info', 'recipe-info', 'run', 'module', 'recipe', 'cmd', 'exit']
#         self.files_and_dirs = self._get_files_and_dirs()

#     def _get_files_and_dirs(self):
#         current_dir = os.getcwd()
#         return [f for f in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, f)) or os.path.isfile(os.path.join(current_dir, f))]

#     def get_completions(self, document, complete_event):
#         text = document.text_before_cursor.strip().split()
#         if len(text) == 1:
#             for cmd in self.commands:
#                 if cmd.startswith(text[0]):
#                     yield Completion(cmd, start_position=-len(text[0]))
#         elif len(text) == 2 and text[0] == 'load':
#             for name in self.files_and_dirs:
#                 if name.startswith(text[1]):
#                     yield Completion(name, start_position=-len(text[1]))

class CommandCompleter(Completer):
    def __init__(self):
        # self.commands = ['create', 'load', 'save', 'list-modules', 'list-recipes', 'module-info', 'recipe-info', 'run-module', 'run-recipe', 'run-cmd', 'exit']
        self.commands = ['create', 'load', 'save', 'list', 'info', 'run', 'module', 'recipe', 'cmd', 'exit']
        self.run_subcommands = ['module', 'recipe', 'cmd']
        self.files_and_dirs = self._get_files_and_dirs()

    def _get_files_and_dirs(self):
        current_dir = os.getcwd()
        return [f for f in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, f)) or os.path.isfile(os.path.join(current_dir, f))]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip().split()
        if len(text) == 1:
            for cmd in self.commands:
                if cmd.startswith(text[0]):
                    yield Completion(cmd, start_position=-len(text[0]))
        elif len(text) == 2:
            if text[0] == 'run':
                for subcmd in self.run_subcommands:
                    if subcmd.startswith(text[1]):
                        yield Completion(subcmd, start_position=-len(text[1]))
            elif text[0] == 'load':
                for name in self.files_and_dirs:
                    if name.startswith(text[1]):
                        yield Completion(name, start_position=-len(text[1]))

def get_json_files(directory):
    return [os.path.basename(f) for f in glob.glob(os.path.join(directory, '*.json'))]

def start_interactive():
    modules = get_json_files('../modules/json')
    recipes = get_json_files('../recipes')
    workspaces = get_json_files('../workspace')

    completer = NestedCompleter.from_nested_dict({
        'create': None,
        'load': {'workspace': {workspace: None for workspace in workspaces}},
        'run': {
            'module': {module: None for module in modules},
            'recipe': {recipe: None for recipe in recipes},
            'cmd': {
                'ls': {'../workspace', '../modules', '../recipes'},
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
    

    # last_command = ""

    # def get_rprompt():
    #     return f'< Last command: {last_command}'

    while True:
        try:
            workspace_name = current_workspace.workspace_name if current_workspace else "No workspace"
            # escaped_workspace = html.escape(str(current_workspace) or "")
            command = session.prompt(f'{workspace_name}> ', bottom_toolbar=status_line, style=style)
            # command = session.prompt('> ')
            if command.strip().lower() in ['exit', 'quit']:
                break
            args = parser.parse_args(command.split())
            if hasattr(args, 'func'):
                args.func(args)
                # escaped_workspace = html.escape(str(current_workspace) or "")
            else:
                print(f"Invalid command: {command}")
                parser.print_help()
        except argparse.ArgumentError as e:
            print(f"Error: {e}")
            parser.print_help()
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    global parser
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

    parser_list_modules = subparsers.add_parser('list-modules', help='List available modules')
    parser_list_modules.set_defaults(func=list_modules)

    parser_list_recipes = subparsers.add_parser('list-recipes', help='List available recipes')
    parser_list_recipes.set_defaults(func=list_recipes)

    # parser_module_info = subparsers.add_parser('module-info', help='Get info about a specific module')
    # parser_module_info.add_argument('module_name', type=str, help='The name of the module')
    # parser_module_info.set_defaults(func=module_info)

    # parser_recipe_info = subparsers.add_parser('recipe-info', help='Get info about a specific recipe')
    # parser_recipe_info.add_argument('recipe_name', type=str, help='The name of the recipe')
    # parser_recipe_info.set_defaults(func=recipe_info)

    # parser_run_module = subparsers.add_parser('run-module', help='Run a specific module')
    # parser_run_module.add_argument('module_name', type=str, help='The name of the module')
    # parser_run_module.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the module')
    # parser_run_module.set_defaults(func=run_module)

    # parser_run_recipe = subparsers.add_parser('run-recipe', help='Run a specific recipe')
    # parser_run_recipe.add_argument('recipe_name', type=str, help='The name of the recipe')
    # parser_run_recipe.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the recipe')
    # parser_run_recipe.set_defaults(func=run_recipe)

    # parser_run_os_command = subparsers.add_parser('run-cmd', help='Run an OS command')
    # parser_run_os_command.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the command')
    # parser_run_os_command.set_defaults(func=run_os_command)

    # Info commands
    parser_info = subparsers.add_parser('info', help='Get info about a specific entity')
    info_subparsers = parser_info.add_subparsers(dest='info_type')

    parser_module_info = info_subparsers.add_parser('module', help='Get info about a specific module')
    parser_module_info.add_argument('module_name', type=str, help='The name of the module')
    parser_module_info.set_defaults(func=module_info)

    parser_recipe_info = info_subparsers.add_parser('recipe', help='Get info about a specific recipe')
    parser_recipe_info.add_argument('recipe_name', type=str, help='The name of the recipe')
    parser_recipe_info.set_defaults(func=recipe_info)

    # Run commands
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

    # List commands
    parser_list = subparsers.add_parser('list', help='List specific entities')
    list_subparsers = parser_list.add_subparsers(dest='list_type')

    parser_list_modules = list_subparsers.add_parser('module', help='List all modules')
    parser_list_modules.set_defaults(func=list_modules)

    parser_list_recipes = list_subparsers.add_parser('recipe', help='List all recipes')
    parser_list_recipes.set_defaults(func=list_recipes)

    parser_interactive = subparsers.add_parser('interactive', help='Start interactive mode')
    parser_interactive.set_defaults(func=lambda args: start_interactive())

    if len(sys.argv) == 1:
        start_interactive()
    else:
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
