import argparse
import sys
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter

# Ensure the parent directories are in the path for importing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from workspace.manager import create_workspace, save_workspace, load_workspace_unsafe, save_workspace_unsafe
from workspace.workspace import WorkSpace

current_workspace = None

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

# def create_workspace_cmd(args):
#     global current_workspace
#     set_workspace_name(args.name)  # args.nameを使用してワークスペース名を設定
#     current_workspace = create_workspace(get_or_load_workspace())  # グローバル変数からワークスペース名を取得
#     save_workspace_unsafe(current_workspace, get_or_load_workspace())
#     print(f"Workspace '{get_or_load_workspace()}' created and saved.")

# def create_workspace_cmd(args):
#     global current_workspace
#     current_workspace = create_workspace(args.name)
#     save_workspace_unsafe(current_workspace, f"{args.name}")
#     print(f"Workspace '{args.name}' created and saved.")

def load_workspace_cmd(args):
    global current_workspace
    current_workspace = get_or_load_workspace(args.name)
    print(f"Workspace '{args.name}' loaded.")

def save_workspace_cmd(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    save_workspace_unsafe(current_workspace, f"{current_workspace.workspace_name}")
    print(f"Workspace '{current_workspace.workspace_name}' saved.")

def list_modules(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    modules = current_workspace.get_module_list()
    for module in modules:
        print(module)

def list_recipes(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    recipes = current_workspace.get_recipe_list()
    for recipe in recipes:
        print(recipe)

def module_info(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    info = current_workspace.get_module_info(args.module_name)
    if info:
        print(info)
    else:
        print(f"Module '{args.module_name}' not found.")

def recipe_info(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
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
    module_id = current_workspace.run_module(args.module_name, args.args)
    result = current_workspace.get_module_result(module_id)
    print(f"Module '{args.module_name}' executed with result: {result}")

def run_recipe(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
        return
    recipe_id = current_workspace.run_recipe(args.recipe_name, args.args)
    result = current_workspace.get_recipe_result(recipe_id)
    print(f"Recipe '{args.recipe_name}' executed with result: {result}")

def run_os_command(args):
    global current_workspace
    if current_workspace is None:
        print("No workspace loaded.")
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

def start_interactive():
    session = PromptSession(history=InMemoryHistory())
    completer = WordCompleter(['create', 'load', 'save', 'list-modules', 'list-recipes', 'module-info', 'recipe-info', 'run-module', 'run-recipe', 'exit'], ignore_case=True)
    
    print("Starting interactive mode. Type 'exit' to quit.")
    while True:
        try:
            user_input = session.prompt(">> ", completer=completer).strip()
            if user_input.lower() == 'exit':
                break

            args = user_input.split()
            if not args:
                continue

            command = args[0]
            if command == 'create':
                if len(args) != 2:
                    print("Usage: create <workspace_name>")
                else:
                    create_workspace_cmd(argparse.Namespace(name=args[1]))
            elif command == 'load':
                if len(args) != 2:
                    print("Usage: load <workspace_name>")
                else:
                    load_workspace_cmd(argparse.Namespace(name=args[1]))
            elif command == 'save':
                save_workspace_cmd(None)
            elif command == 'list-modules':
                list_modules(None)
            elif command == 'list-recipes':
                list_recipes(None)
            elif command == 'module-info':
                if len(args) != 2:
                    print("Usage: module-info <module_name>")
                else:
                    module_info(argparse.Namespace(module_name=args[1]))
            elif command == 'recipe-info':
                if len(args) != 2:
                    print("Usage: recipe-info <recipe_name>")
                else:
                    recipe_info(argparse.Namespace(recipe_name=args[1]))
            elif command == 'run-module':
                if len(args) < 2:
                    print("Usage: run-module <module_name> [args...]")
                else:
                    run_module(argparse.Namespace(module_name=args[1], args=args[2:]))
            elif command == 'run-recipe':
                if len(args) < 2:
                    print("Usage: run-recipe <recipe_name> [args...]")
                else:
                    run_recipe(argparse.Namespace(recipe_name=args[1], args=args[2:]))
            elif command.startswith('!'):
                run_os_command(argparse.Namespace(args=args[1:]))
            else:
                print(f"Unknown command: {command}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="CLI for workspace management and execution.")
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

    parser_module_info = subparsers.add_parser('module-info', help='Get info about a specific module')
    parser_module_info.add_argument('module_name', type=str, help='The name of the module')
    parser_module_info.set_defaults(func=module_info)

    parser_recipe_info = subparsers.add_parser('recipe-info', help='Get info about a specific recipe')
    parser_recipe_info.add_argument('recipe_name', type=str, help='The name of the recipe')
    parser_recipe_info.set_defaults(func=recipe_info)

    parser_run_module = subparsers.add_parser('run-module', help='Run a specific module')
    parser_run_module.add_argument('module_name', type=str, help='The name of the module')
    parser_run_module.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the module')
    parser_run_module.set_defaults(func=run_module)

    parser_run_recipe = subparsers.add_parser('run-recipe', help='Run a specific recipe')
    parser_run_recipe.add_argument('recipe_name', type=str, help='The name of the recipe')
    parser_run_recipe.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the recipe')
    parser_run_recipe.set_defaults(func=run_recipe)

    parser_run_os_command = subparsers.add_parser('run-cmd', help='Run an OS command')
    parser_run_os_command.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the command')
    parser_run_os_command.set_defaults(func=run_os_command)

    parser_interactive = subparsers.add_parser('interactive', help='Start interactive mode')
    parser_interactive.set_defaults(func=lambda args: start_interactive())

    # if len(sys.argv) == 1:
    #     start_interactive()
    # else:
    #     args = parser.parse_args()
    #     if hasattr(args, 'func'):
    #         args.func(args)
    #     else:
    #         parse_command(' '.join(sys.argv[1:]))

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "load" and len(sys.argv) == 3:
            args = argparse.Namespace(name=sys.argv[2])
            load_workspace_cmd(args=args)

    cli_completer = WordCompleter(['create', 'load', 'save', 'exit'], ignore_case=True)

    session = PromptSession(history=InMemoryHistory(), completer=cli_completer)
    while True:
        try:
            line = session.prompt('> ')
            if line.startswith("create "):
                args = line.split()
                create_workspace_cmd(args=argparse.Namespace(name=args[1]))
            elif line.startswith("load "):
                args = line.split()
                load_workspace_cmd(args=argparse.Namespace(name=args[1]))
            elif line.startswith("save"):
                save_workspace_cmd()
            elif line == "exit":
                break
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()

