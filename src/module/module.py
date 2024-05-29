import os
import json
import jsonschema

import utils

class Module:
    def __init__(self, module_name) -> None:
        self.module_json = None
        self.module_list = self.get_module_list()
        self.module_name = module_name
        self.module_path = next((file for file, name in self.module_list if name == self.module_name))
        self.variables = None # json
        
        with open(os.path.join("modules", self.module_path), 'r') as f:
            self.module_json = json.load(f)
        if self.module_json['prepare-module-directory']:
            self.module_dir = utils.get_temp_folder(self.module_json)
            self.variables["module_dir"] = self.module_dir
        
        
        
    def run(self, args) -> None:
        # モジュール内変数の準備
        for arg, arg_count in enumerate(args):
            self.variables["input"][arg_count] = arg
            
        
        
    async def run_async(self, args) -> None:
        pass
    
    def get_result(self):
        return self.variables["output"]
        
    
    @staticmethod
    def get_module_list() -> list:
        module_list = []
        for file in os.listdir('modules'):
            if file.endswith('.json'):
                if file == 'schema.json':
                    continue
                with open(os.path.join('modules', file), 'r') as f:
                    try:
                        module_json = json.load(f)
                        jsonschema.validate(module_json, json.load(open('modules/schema.json')))
                        module_list.append((file, module_json['module-name']))
                    except json.JSONDecodeError:
                        print(f'{file} is invalid json')
                    except jsonschema.exceptions.ValidationError as e:
                        print(f'{file} is invalid json schema')
        return module_list