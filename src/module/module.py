
import os
import sys
import re
import subprocess
import json
import jsonschema

import utils

class Module:
    def __init__(self, module_name) -> None:
        """
        Args:
            module_name (_type_): 起動するモジュール名(NOTファイル名)
        """
        
        self.module_json = None
        self.module_list = self.get_module_list()
        self.module_name = module_name
        if self.module_name in self.module_list:
            self.module_path = self.module_list[module_name]
        else:
            raise Exception(f"Error: {module_name} is not found.")
        
        self.variables = {}
        
        with open(os.path.join("modules/json", self.module_path), 'r') as f:
            self.module_json = json.load(f)
        if self.module_json['prepare-module-directory']:
            self.variables["module_dir"] = utils.get_temp_folder()
            
        self.variables["cwd"] = os.getcwd()
        
    def run(self, args: list) -> None:
        # モジュール内変数の準備
        self.variables["input"] = []
        for arg_count, arg  in enumerate(args):
            self.variables["input"].append(arg)
        
        if self.module_json["type"] == "built-in":
            if self.module_json["method"] == "class":
                #todo 何かしらの.pyを読み込んでインスタンスを作成しrunメソッドを実行する
                pass
                
                
            elif self.module_json["method"] == "function":
                #todo 何かしらの.pyを読み込んで指定された関数を実行する
                pass
            
        elif self.module_json["type"] == "external":
            execution_command = self.get_execution_command()
            
            if "environment" in self.module_json['execution'] and self.module_json['execution']["environment"]["type"] == "venv":
                venv_path = os.path.join("modules", self.module_name, "venv")
                requirements_path = os.path.join("modules", self.module_name, "requirements.txt")
                if not os.path.isdir(venv_path) and os.path.isfile(requirements_path):
                    subprocess.run(["python3", "-m", "venv", venv_path])
                elif not os.path.isfile(requirements_path):
                    raise("requirements.txt is not found")
                activate_script = os.path.join(venv_path, 'bin', 'activate')
                subprocess.run(f"source {activate_script} && pip install -r {requirements_path} > /dev/null 2>&1", shell=True, executable="/bin/bash")
                execution_command = f"source {activate_script} && {execution_command}"
            self.shell = subprocess.run(execution_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, executable="/bin/bash")

        return
        
    async def run_async(self, args) -> None:
        pass
    
    def get_result(self):
        stdout, stderr = self.shell.stdout, self.shell.stderr
        # print(stdout, stderr)
        self.variables["output"] = []
        try:
            json_output = json.loads(stdout.decode())
            self.variables["output"] = json_output
        except json.JSONDecodeError:
            # print("stdout is not in valid JSON format")
            self.variables["output"].append(stdout.decode())
            # print(stdout.decode())
            
        return self.variables["output"]
    
        
    def get_execution_command(self):
        execution_command = "stdbuf -i0 -o0 -e0 "
        for command in self.module_json['execution']['command']:
            command = utils.replace_template(self.variables, command)
            execution_command = execution_command + " " + command
        return execution_command
        
    @staticmethod
    def get_module_list() -> list:
        module_list = {}
        for file in os.listdir('modules/json'):
            if file.endswith('.json'):
                if file == 'schema.json':
                    continue
                with open(os.path.join('modules/json', file), 'r') as f:
                    try:
                        module_json = json.load(f)
                        jsonschema.validate(module_json, json.load(open('modules/json/schema.json')))
                        module_list[module_json["name"]] = file
                    except json.JSONDecodeError:
                        print(f'{file} is invalid json')
                    except jsonschema.exceptions.ValidationError as e:
                        print(f'{file} is invalid json schema')
        return module_list
