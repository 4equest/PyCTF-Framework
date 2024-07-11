import os
import json
import jsonschema

import module.module as md

import utils

class Recipe:
    def __init__(self, recipe_name) -> None:
        self.recipe_json = None
        self.recipe_list = self.get_recipe_list()
        self.recipe_name = recipe_name
        if self.recipe_name in self.recipe_list:
            self.recipe_path = self.recipe_list[recipe_name]
        else:
            raise KeyError(f"Error: {recipe_name} is not found.")
            
        self.variables = {}
        with open(os.path.join("recipes", self.recipe_path), 'r') as f:
            self.recipe_json = json.load(f)
        if self.recipe_json['prepare-recipe-directory']:
            self.recipe_dir = utils.get_temp_folder()
            self.variables["recipe_dir"] = self.recipe_dir

        self.modules = []
        
        
    def run(self, args: list) -> None:
        # レシピ内変数の準備
        self.variables["input"] = []
        for arg_count, arg in enumerate(args):
            self.variables["input"].append(arg)
            
        for module in self.recipe_json['modules']:
            this_module = md.Module(module["module-name"])
            #todo moduleに必要なモジュール変数を調べて取得して渡して実行
            if len(module['arguments']) > len(args):
                raise Exception(f"Error: {module['module-name']} module requires {len(module['arguments'])} arguments, but {len(args)} arguments are given.")
            
            for arg_count, arg in enumerate(module['arguments']):
                module['arguments'][arg_count] = utils.replace_template(self.variables, arg)
                
            this_module.run(module['arguments'])
            module_result = this_module.get_result()
            self.variables[module["recipe-module-name"]] = {"output": []}
            self.variables[module["recipe-module-name"]]["output"] = module_result
            #self.modules.append(this_module)
            
    def get_result(self):
        self.variables["output"] = []
        for arg_count, arg in enumerate(self.recipe_json['output']):
            self.variables["output"].append(utils.replace_template(self.variables, arg))
        return self.variables["output"]
    
    async def run_async(self, args) -> None:
        pass
    
    @staticmethod
    def get_recipe_list() -> dict:
        recipe_list = {}
        for file in os.listdir('recipes'):
            if file.endswith('.json'):
                if file == 'schema.json':
                    continue
                with open(os.path.join('recipes', file), 'r') as f:
                    try:
                        recipe_json = json.load(f)
                        jsonschema.validate(recipe_json, json.load(open('recipes/schema.json')))
                        recipe_list[recipe_json['name']] = file
                    except json.JSONDecodeError:
                        print(f'{file} is invalid json')
                    except jsonschema.exceptions.ValidationError as e:
                        print(f'{file} is invalid json schema')
        return recipe_list
    
    @staticmethod
    def get_recipe_info(recipe_name: str) -> str:
        recipe_list = Recipe.get_recipe_list()
        if not recipe_name in recipe_list:
            raise KeyError(f"{recipe_name} is not found.")
        
        with open(os.path.join("recipes", recipe_list[recipe_name]), 'r') as f:
            recipe_json = json.load(f)
        
        if not "description" in recipe_json:
            raise KeyError(f"{recipe_name} has no description.")
        
        return recipe_json["description"]