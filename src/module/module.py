import os
import sys
import re
import subprocess
import json
import jsonschema

import utils

class Module:
    def __init__(self, module_name, shell=None) -> None:
        """
        Args:
            module_name (_type_): 起動するモジュール名(NOTファイル名)
            shell (_type_, optional): レシピからの呼び出しの場合はシェルを再利用できるかも? Defaults to None.
        """
        
        self.module_json = None
        self.module_list = self.get_module_list()
        self.module_name = module_name
        self.module_path = next((file for file, name in self.module_list if name == self.module_name))
        self.variables = {}
        
        with open(os.path.join("modules/json", self.module_path), 'r') as f:
            self.module_json = json.load(f)
        if self.module_json['prepare-module-directory']:
            self.variables["module_dir"] = utils.get_temp_folder()
        
        if shell is not None:
            self.shell = shell
        else:
            self.shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        
    def run(self, args) -> None:
        # モジュール内変数の準備
        self.variables["input"] = []
        for arg_count, arg  in enumerate(args):
            self.variables["input"].append(arg)
        
        if self.module_json['module']["type"] == "built-in":
            if self.module_json['module']["method"] == "class":
                #todo 何かしらの.pyを読み込んでインスタンスを作成しrunメソッドを実行する
                pass
                
                
            elif self.module_json['module']["method"] == "function":
                #todo 何かしらの.pyを読み込んで指定された関数を実行する
                pass
            
        elif self.module_json['module']["type"] == "external":
            execution_command = self.get_execution_command()
            
            if "environment" in self.module_json['execution'] and self.module_json['execution']["environment"]["type"] == "venv":
                venv_path = os.path.join("modules", self.module_name, "venv")
                requirements_path = os.path.join("modules", self.module_name, "requirements.txt")
                if not os.path.isdir(venv_path) and os.path.isfile(requirements_path):
                    subprocess.run(["python3", "-m", "venv", venv_path])
                elif not os.path.isfile(requirements_path):
                    raise("requirements.txt is not found")
                activate_script = os.path.join(venv_path, 'bin', 'activate')
                self.shell.stdin.write(f"source {activate_script}\n".encode())
                self.shell.stdin.flush()
            
            #todo 
            self.shell.stdin.write((execution_command + "\n").encode())
            self.shell.stdin.flush()
        
        return
        
    async def run_async(self, args) -> None:
        pass
    
    def get_result(self):
        (stdout, stderr) = self.shell.communicate()
        print(stdout, stderr)
        self.variables["output"] = []
        try:
            json_output = json.loads(stdout.decode())
            self.variables["output"] = json_output
        except json.JSONDecodeError:
            print("stdout is not in valid JSON format")
            self.variables["output"].append(stdout.decode())
            print(stdout.decode())
            
        return self.variables["output"]
    
    def replace_template(self, template):
        pattern = re.compile(r'\{(.+?)\}')
        def replacer(match):
            path = match.group(1).split('.')
            value = self.variables
            for key in path:
                print(value)
                print(type(value))
                if isinstance(value, list):
                    key = int(key)
                value = value[key]
            return str(value)
        return pattern.sub(replacer, template)
        
    def get_execution_command(self):
        execution_command = "stdbuf -i0 -o0 -e0 "
        for command in self.module_json['execution']['command']:
            command = self.replace_template(command)
            execution_command = execution_command + " " + command
        return execution_command
        
    @staticmethod
    def get_module_list() -> list:
        module_list = []
        for file in os.listdir('modules/json'):
            if file.endswith('.json'):
                if file == 'schema.json':
                    continue
                with open(os.path.join('modules/json', file), 'r') as f:
                    try:
                        module_json = json.load(f)
                        jsonschema.validate(module_json, json.load(open('modules/json/schema.json')))
                        module_list.append((file, module_json['module']["name"]))
                    except json.JSONDecodeError:
                        print(f'{file} is invalid json')
                    except jsonschema.exceptions.ValidationError as e:
                        print(f'{file} is invalid json schema')
        return module_list