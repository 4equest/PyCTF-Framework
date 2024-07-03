import argparse
import sys
import os
import readline

# Ensure the parent directories are in the path for importing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from workspace.manager import create_workspace, save_workspace, load_workspace_unsafe
from workspace.workspace import WorkSpace

current_workspace = None

def get_or_load_workspace(workspace_name):
    global current_workspace
    if current_workspace is None or current_workspace.workspace_name != workspace_name:
        current_workspace = load_workspace_unsafe(f"{workspace_name}")
    return current_workspace

def create_workspace_cmd(args):
    workspace = create_workspace(args.name)
    save_workspace(workspace, f"{args.name}")
    print(f"Workspace '{args.name}' created and saved.")
    return workspace

def load_workspace_cmd(args):
    workspace = get_or_load_workspace(args.name)
    print(f"Workspace '{args.name}' loaded.")
    return workspace

def save_workspace_cmd(args):
    global current_workspace
    if current_workspace is None or current_workspace.workspace_name != args.name:
        current_workspace = load_workspace_unsafe(f"{args.name}")
    save_workspace(current_workspace, f"{args.name}")
    print(f"Workspace '{current_workspace.workspace_name}' saved.")

def list_modules(args):
    workspace = get_or_load_workspace(args.name)
    modules = workspace.get_module_list()
    for module in modules:
        print(module)

def list_recipes(args):
    workspace = get_or_load_workspace(args.name)
    recipes = workspace.get_recipe_list()
    for recipe in recipes:
        print(recipe)

def module_info(args):
    workspace = get_or_load_workspace(args.name)
    info = workspace.get_module_info(args.module_name)
    if info:
        print(info)
    else:
        print(f"Module '{args.module_name}' not found.")

def recipe_info(args):
    workspace = get_or_load_workspace(args.name)
    info = workspace.get_recipe_info(args.recipe_name)
    if info:
        print(info)
    else:
        print(f"Recipe '{args.recipe_name}' not found.")

def run_module(args):
    workspace = get_or_load_workspace(args.workspace)
    module_id = workspace.run_module(args.module_name, args.args)
    result = workspace.get_module_result(module_id)
    print(f"Module '{args.module_name}' executed with result: {result}")

def run_recipe(args):
    workspace = get_or_load_workspace(args.workspace)
    recipe_id = workspace.run_recipe(args.recipe_name, args.args)
    result = workspace.get_recipe_result(recipe_id)
    print(f"Recipe '{args.recipe_name}' executed with result: {result}")

def run_os_command(args):
    workspace = get_or_load_workspace(args.workspace)
    cmd_id = workspace.run_cmd(args.args)
    result = workspace.get_cmd_result(cmd_id)
    print(f"Command executed with result: {result}")

def parse_command(command):
    if command.startswith("!"):
        cmd_args = command[1:].split()
        run_os_command(argparse.Namespace(workspace=cmd_args[0], args=cmd_args[1:]))
    else:
        print("Invalid command")

def start_interactive():
    readline.parse_and_bind('tab: complete')
    print("Starting interactive mode. Type 'exit' to quit.")
    while True:
        try:
            user_input = input(">> ").strip()
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
                if len(args) != 2:
                    print("Usage: save <workspace_name>")
                else:
                    save_workspace_cmd(argparse.Namespace(name=args[1]))
            elif command == 'list-modules':
                if len(args) != 2:
                    print("Usage: list-modules <workspace_name>")
                else:
                    list_modules(argparse.Namespace(name=args[1]))
            elif command == 'list-recipes':
                if len(args) != 2:
                    print("Usage: list-recipes <workspace_name>")
                else:
                    list_recipes(argparse.Namespace(name=args[1]))
            elif command == 'module-info':
                if len(args) != 3:
                    print("Usage: module-info <workspace_name> <module_name>")
                else:
                    module_info(argparse.Namespace(name=args[1], module_name=args[2]))
            elif command == 'recipe-info':
                if len(args) != 3:
                    print("Usage: recipe-info <workspace_name> <recipe_name>")
                else:
                    recipe_info(argparse.Namespace(name=args[1], recipe_name=args[2]))
            elif command == 'run-module':
                if len(args) < 3:
                    print("Usage: run-module <workspace_name> <module_name> [args...]")
                else:
                    run_module(argparse.Namespace(workspace=args[1], module_name=args[2], args=args[3:]))
            elif command == 'run-recipe':
                if len(args) < 3:
                    print("Usage: run-recipe <workspace_name> <recipe_name> [args...]")
                else:
                    run_recipe(argparse.Namespace(workspace=args[1], recipe_name=args[2], args=args[3:]))
            elif command.startswith('!'):
                run_os_command(argparse.Namespace(workspace=args[1], args=args[1:]))
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
    parser_save.add_argument('name', type=str, help='The name of the workspace to save')
    parser_save.set_defaults(func=save_workspace_cmd)

    parser_list_modules = subparsers.add_parser('list-modules', help='List available modules')
    parser_list_modules.add_argument('name', type=str, help='The name of the workspace')
    parser_list_modules.set_defaults(func=list_modules)

    parser_list_recipes = subparsers.add_parser('list-recipes', help='List available recipes')
    parser_list_recipes.add_argument('name', type=str, help='The name of the workspace')
    parser_list_recipes.set_defaults(func=list_recipes)

    parser_module_info = subparsers.add_parser('module-info', help='Get info about a specific module')
    parser_module_info.add_argument('name', type=str, help='The name of the workspace')
    parser_module_info.add_argument('module_name', type=str, help='The name of the module')
    parser_module_info.set_defaults(func=module_info)

    parser_recipe_info = subparsers.add_parser('recipe-info', help='Get info about a specific recipe')
    parser_recipe_info.add_argument('name', type=str, help='The name of the workspace')
    parser_recipe_info.add_argument('recipe_name', type=str, help='The name of the recipe')
    parser_recipe_info.set_defaults(func=recipe_info)

    parser_run_module = subparsers.add_parser('run-module', help='Run a specific module')
    parser_run_module.add_argument('workspace', type=str, help='The name of the workspace')
    parser_run_module.add_argument('module_name', type=str, help='The name of the module')
    parser_run_module.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the module')
    parser_run_module.set_defaults(func=run_module)

    parser_run_recipe = subparsers.add_parser('run-recipe', help='Run a specific recipe')
    parser_run_recipe.add_argument('workspace', type=str, help='The name of the workspace')
    parser_run_recipe.add_argument('recipe_name', type=str, help='The name of the recipe')
    parser_run_recipe.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the recipe')
    parser_run_recipe.set_defaults(func=run_recipe)

    parser_run_os_command = subparsers.add_parser('run-cmd', help='Run an OS command')
    parser_run_os_command.add_argument('workspace', type=str, help='The name of the workspace')
    parser_run_os_command.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the command')
    parser_run_os_command.set_defaults(func=run_os_command)

    parser_interactive = subparsers.add_parser('interactive', help='Start interactive mode')
    parser_interactive.set_defaults(func=lambda args: start_interactive())

    if len(sys.argv) == 1:
        start_interactive()
    else:
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parse_command(' '.join(sys.argv[1:]))

if __name__ == "__main__":
    main

"""
import argparse
import sys
import os
import readline

# ensure the parent directories are in the path for importing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from workspace.manager import create_workspace, save_workspace, load_workspace_unsafe, save_workspace_unsafe
from workspace.workspace import workspace

current_workspace = none

def get_or_load_workspace(workspace_name):
    global current_workspace
    if current_workspace is none or current_workspace.workspace_name != workspace_name:
        current_workspace = load_workspace_unsafe(f"{workspace_name}")
    return current_workspace

def create_workspace_cmd(args):
    workspace = create_workspace(args.name)
    save_workspace(workspace, f"{args.name}")
    print(f"workspace '{args.name}' created and saved.")
    return workspace

def load_workspace_cmd(args):
    workspace = get_or_load_workspace(args.name)
    print(f"workspace '{args.name}' loaded.")
    return workspace

def save_workspace_cmd(args):
    global current_workspace
    if current_workspace is none or current_workspace.workspace_name != args.name:
        current_workspace = load_workspace_unsafe(f"{args.name}")
    save_workspace(current_workspace, f"{args.name}")
    print(f"workspace '{current_workspace.workspace_name}' saved.")

def list_modules(args):
    workspace = get_or_load_workspace(args.name)
    modules = workspace.get_module_list()
    for module in modules:
        print(module)

def list_recipes(args):
    workspace = get_or_load_workspace(args.name)
    recipes = workspace.get_recipe_list()
    for recipe in recipes:
        print(recipe)

def module_info(args):
    workspace = get_or_load_workspace(args.name)
    info = workspace.get_module_info(args.module_name)
    if info:
        print(info)
    else:
        print(f"module '{args.module_name}' not found.")

def recipe_info(args):
    workspace = get_or_load_workspace(args.name)
    info = workspace.get_recipe_info(args.recipe_name)
    if info:
        print(info)
    else:
        print(f"recipe '{args.recipe_name}' not found.")

def run_module(args):
    workspace = get_or_load_workspace(args.workspace)
    module_id = workspace.run_module(args.module_name, args.args)
    result = workspace.get_module_result(module_id)
    print(f"module '{args.module_name}' executed with result: {result}")

def run_recipe(args):
    workspace = get_or_load_workspace(args.workspace)
    recipe_id = workspace.run_recipe(args.recipe_name, args.args)
    result = workspace.get_recipe_result(recipe_id)
    print(f"recipe '{args.recipe_name}' executed with result: {result}")

def run_os_command(args):
    workspace = get_or_load_workspace(args.workspace)
    cmd_id = workspace.run_cmd(args.args)
    result = workspace.get_cmd_result(cmd_id)
    print(f"command executed with result: {result}")

def parse_command(command):
    if command.startswith("!"):
        cmd_args = command[1:].split()
        run_os_command(argparse.namespace(workspace=cmd_args[0], args=cmd_args[1:]))
    else:
        print("invalid command")

def start_interactive():
    print("starting interactive mode. type 'exit' to quit.")
    while true:
        try:
            user_input = readline.get_line_buffer(">> ").strip()
            if user_input.lower() == 'exit':
                break

            args = user_input.split()
            if not args:
                continue
            user_input = input(">> ").strip()
            if user_input.lower() == 'exit':
                break

            args = user_input.split()
            if not args:
                continue

            command = args[0]
            if command == 'create':
                if len(args) != 2:
                    print("usage: create <workspace_name>")
                else:
                    create_workspace_cmd(argparse.namespace(name=args[1]))
            elif command == 'load':
                if len(args) != 2:
                    print("usage: load <workspace_name>")
                else:
                    load_workspace_cmd(argparse.namespace(name=args[1]))
            elif command == 'save':
                if len(args) != 2:
                    print("usage: save <workspace_name>")
                else:
                    save_workspace_cmd(argparse.namespace(name=args[1]))
            elif command == 'list-modules':
                if len(args) != 2:
                    print("usage: list-modules <workspace_name>")
                else:
                    list_modules(argparse.namespace(name=args[1]))
            elif command == 'list-recipes':
                if len(args) != 2:
                    print("usage: list-recipes <workspace_name>")
                else:
                    list_recipes(argparse.namespace(name=args[1]))
            elif command == 'module-info':
                if len(args) != 3:
                    print("usage: module-info <workspace_name> <module_name>")
                else:
                    module_info(argparse.namespace(name=args[1], module_name=args[2]))
            elif command == 'recipe-info':
                if len(args) != 3:
                    print("usage: recipe-info <workspace_name> <recipe_name>")
                else:
                    recipe_info(argparse.namespace(name=args[1], recipe_name=args[2]))
            elif command == 'run-module':
                if len(args) < 3:
                    print("usage: run-module <workspace_name> <module_name> [args...]")
                else:
                    run_module(argparse.namespace(workspace=args[1], module_name=args[2], args=args[3:]))
            elif command == 'run-recipe':
                if len(args) < 3:
                    print("usage: run-recipe <workspace_name> <recipe_name> [args...]")
                else:
                    run_recipe(argparse.namespace(workspace=args[1], recipe_name=args[2], args=args[3:]))
            elif command.startswith('!'):
                run_os_command(argparse.namespace(workspace=args[1], args=args[1:]))
            else:
                print(f"unknown command: {command}")
        except exception as e:
            print(f"error: {e}")

def main():
    parser = argparse.argumentparser(description="cli for workspace management and execution.")
    subparsers = parser.add_subparsers()

    parser_create = subparsers.add_parser('create', help='create a new workspace')
    parser_create.add_argument('name', type=str, help='the name of the workspace to create')
    parser_create.set_defaults(func=create_workspace_cmd)

    parser_load = subparsers.add_parser('load', help='load an existing workspace')
    parser_load.add_argument('name', type=str, help='the name of the workspace to load')
    parser_load.set_defaults(func=load_workspace_cmd)

    parser_save = subparsers.add_parser('save', help='save the current workspace')
    parser_save.add_argument('name', type=str, help='the name of the workspace to save')
    parser_save.set_defaults(func=save_workspace_cmd)

    parser_list_modules = subparsers.add_parser('list-modules', help='list available modules')
    parser_list_modules.add_argument('name', type=str, help='the name of the workspace')
    parser_list_modules.set_defaults(func=list_modules)

    parser_list_recipes = subparsers.add_parser('list-recipes', help='list available recipes')
    parser_list_recipes.add_argument('name', type=str, help='the name of the workspace')
    parser_list_recipes.set_defaults(func=list_recipes)

    parser_module_info = subparsers.add_parser('module-info', help='get info about a specific module')
    parser_module_info.add_argument('name', type=str, help='the name of the workspace')
    parser_module_info.add_argument('module_name', type=str, help='the name of the module')
    parser_module_info.set_defaults(func=module_info)

    parser_recipe_info = subparsers.add_parser('recipe-info', help='get info about a specific recipe')
    parser_recipe_info.add_argument('name', type=str, help='the name of the workspace')
    parser_recipe_info.add_argument('recipe_name', type=str, help='the name of the recipe')
    parser_recipe_info.set_defaults(func=recipe_info)

    parser_run_module = subparsers.add_parser('run-module', help='run a specific module')
    parser_run_module.add_argument('workspace', type=str, help='the name of the workspace')
    parser_run_module.add_argument('module_name', type=str, help='the name of the module')
    parser_run_module.add_argument('args', nargs=argparse.remainder, help='arguments for the module')
    parser_run_module.set_defaults(func=run_module)

    parser_run_recipe = subparsers.add_parser('run-recipe', help='run a specific recipe')
    parser_run_recipe.add_argument('workspace', type=str, help='the name of the workspace')
    parser_run_recipe.add_argument('recipe_name', type=str, help='the name of the recipe')
    parser_run_recipe.add_argument('args', nargs=argparse.remainder, help='arguments for the recipe')
    parser_run_recipe.set_defaults(func=run_recipe)

    parser_run_os_command = subparsers.add_parser('run-cmd', help='run an os command')
    parser_run_os_command.add_argument('workspace', type=str, help='the name of the workspace')
    parser_run_os_command.add_argument('args', nargs=argparse.remainder, help='arguments for the command')
    parser_run_os_command.set_defaults(func=run_os_command)

    parser_interactive = subparsers.add_parser('interactive', help='start interactive mode')
    parser_interactive.set_defaults(func=lambda args: start_interactive())

    if len(sys.argv) == 1:
        start_interactive()
    else:
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parse_command(' '.join(sys.argv[1:]))


if __name__ == "__main__":
    main()

# now
import argparse
import sys
import os
import readline

# Add src directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from workspace.manager import create_workspace, load_workspace_unsafe, save_workspace
from workspace.workspace import WorkSpace

def create_workspace_cmd(args):
    workspace = create_workspace(args.name)
    save_workspace(workspace, f"{args.name}")
    print(f"Workspace '{args.name}' created and saved.")

def load_workspace_cmd(args):
    workspace = load_workspace_unsafe(f"{args.name}")
    print(f"Workspace '{args.name}' loaded.")
    return workspace

def save_workspace_cmd(args):
    workspace = load_workspace_unsafe(f"{args.name}")
    save_workspace(workspace, f"{args.name}")
    print(f"Workspace '{workspace.workspace_name}' saved.")

def list_modules(args):
    workspace = load_workspace_unsafe(f"{args.name}")
    modules = workspace.get_module_list()
    for module in modules:
        print(module)

def list_recipes(args):
    workspace = load_workspace_unsafe(f"{args.name}")
    recipes = workspace.get_recipe_list()
    for recipe in recipes:
        print(recipe)

def module_info(args):
    workspace = load_workspace_unsafe(f"{args.name}")
    info = workspace.get_module_info(args.module_name)
    if info:
        print(info)
    else:
        print(f"Module '{args.module_name}' not found.")

def recipe_info(args):
    workspace = load_workspace_unsafe(f"{args.name}")
    info = workspace.get_recipe_info(args.recipe_name)
    if info:
        print(info)
    else:
        print(f"Recipe '{args.recipe_name}' not found.")

def run_module(args):
    workspace = load_workspace_unsafe(f"{args.workspace}")
    module_id = workspace.run_module(args.module_name, args.args)
    result = workspace.get_module_result(module_id)
    print(f"Module '{args.module_name}' executed with result: {result}")

def run_recipe(args):
    workspace = load_workspace_unsafe(f"{args.workspace}")
    recipe_id = workspace.run_recipe(args.recipe_name, args.args)
    result = workspace.get_recipe_result(recipe_id)
    print(f"Recipe '{args.recipe_name}' executed with result: {result}")

def run_os_command(args):
    workspace = load_workspace_unsafe(f"{args.workspace}")
    cmd_id = workspace.run_cmd(args.args)
    result = workspace.get_cmd_result(cmd_id)
    print(f"Command executed with result: {result}")

def parse_command(command):
    if command.startswith("!"):
        cmd_args = command[1:].split()
        run_os_command(argparse.Namespace(workspace=cmd_args[0], args=cmd_args[1:]))
    else:
        print("Invalid command")

def start_interactive():
    print("Starting interactive mode. Type 'exit' to quit.")
    while True:
        try:
            # user_input = readline.
            code.interact()
            user_input = input(">> ").strip()
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
                if len(args) != 2:
                    print("Usage: save <workspace_name>")
                else:
                    save_workspace_cmd(argparse.Namespace(name=args[1]))
            elif command == 'list-modules':
                if len(args) != 2:
                    print("Usage: list-modules <workspace_name>")
                else:
                    list_modules(argparse.Namespace(name=args[1]))
            elif command == 'list-recipes':
                if len(args) != 2:
                    print("Usage: list-recipes <workspace_name>")
                else:
                    list_recipes(argparse.Namespace(name=args[1]))
            elif command == 'module-info':
                if len(args) != 3:
                    print("Usage: module-info <workspace_name> <module_name>")
                else:
                    module_info(argparse.Namespace(name=args[1], module_name=args[2]))
            elif command == 'recipe-info':
                if len(args) != 3:
                    print("Usage: recipe-info <workspace_name> <recipe_name>")
                else:
                    recipe_info(argparse.Namespace(name=args[1], recipe_name=args[2]))
            elif command == 'run-module':
                if len(args) < 3:
                    print("Usage: run-module <workspace_name> <module_name> [args...]")
                else:
                    run_module(argparse.Namespace(workspace=args[1], module_name=args[2], args=args[3:]))
            elif command == 'run-recipe':
                if len(args) < 3:
                    print("Usage: run-recipe <workspace_name> <recipe_name> [args...]")
                else:
                    run_recipe(argparse.Namespace(workspace=args[1], recipe_name=args[2], args=args[3:]))
            elif command.startswith('!'):
                run_os_command(argparse.Namespace(workspace=args[1], args=args[1:]))
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
    parser_save.add_argument('name', type=str, help='The name of the workspace to save')
    parser_save.set_defaults(func=save_workspace_cmd)

    parser_list_modules = subparsers.add_parser('list-modules', help='List available modules')
    parser_list_modules.add_argument('name', type=str, help='The name of the workspace')
    parser_list_modules.set_defaults(func=list_modules)

    parser_list_recipes = subparsers.add_parser('list-recipes', help='List available recipes')
    parser_list_recipes.add_argument('name', type=str, help='The name of the workspace')
    parser_list_recipes.set_defaults(func=list_recipes)

    parser_module_info = subparsers.add_parser('module-info', help='Get info about a specific module')
    parser_module_info.add_argument('name', type=str, help='The name of the workspace')
    parser_module_info.add_argument('module_name', type=str, help='The name of the module')
    parser_module_info.set_defaults(func=module_info)

    parser_recipe_info = subparsers.add_parser('recipe-info', help='Get info about a specific recipe')
    parser_recipe_info.add_argument('name', type=str, help='The name of the workspace')
    parser_recipe_info.add_argument('recipe_name', type=str, help='The name of the recipe')
    parser_recipe_info.set_defaults(func=recipe_info)

    parser_run_module = subparsers.add_parser('run-module', help='Run a specific module')
    parser_run_module.add_argument('workspace', type=str, help='The name of the workspace')
    parser_run_module.add_argument('module_name', type=str, help='The name of the module')
    parser_run_module.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the module')
    parser_run_module.set_defaults(func=run_module)

    parser_run_recipe = subparsers.add_parser('run-recipe', help='Run a specific recipe')
    parser_run_recipe.add_argument('workspace', type=str, help='The name of the workspace')
    parser_run_recipe.add_argument('recipe_name', type=str, help='The name of the recipe')
    parser_run_recipe.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the recipe')
    parser_run_recipe.set_defaults(func=run_recipe)

    parser_run_os_command = subparsers.add_parser('run-cmd', help='Run an OS command')
    parser_run_os_command.add_argument('workspace', type=str, help='The name of the workspace')
    parser_run_os_command.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the command')
    parser_run_os_command.set_defaults(func=run_os_command)

    parser_interactive = subparsers.add_parser('interactive', help='Start interactive mode')
    parser_interactive.set_defaults(func=lambda args: start_interactive())

    if len(sys.argv) == 1:
        start_interactive()
    else:
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parse_command(' '.join(sys.argv[1:]))

if __name__ == "__main__":
    main()

"""
