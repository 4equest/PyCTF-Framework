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
        self.recipe_path = next((file for file, name in self.recipe_list if name == self.recipe_name))

        with open(os.path.join("recipes", self.recipe_path), 'r') as f:
            self.recipe_json = json.load(f)
        if self.recipe_json['prepare-recipe-directory']:
            self.recipe_dir = utils.get_temp_folder(self.recipe_json)
            self.variables["recipe_dir"] = self.module_dir

        self.variables = None # json
        self.modules = []
        
        
    def run(self, args) -> None:
        # レシピ内変数の準備
        for arg, arg_count in enumerate(args):
            self.variables["input"][arg_count] = arg
            
        for module in self.recipe_json['modules']:
            self.modules.append(md.Module(module["module-name"]))
            #todo moduleに必要なモジュール変数を調べて取得して渡して実行
            
    async def run_async(self, args) -> None:
        pass
    
    @staticmethod
    def get_recipe_list() -> list:
        recipe_list = []
        for file in os.listdir('recipes'):
            if file.endswith('.json'):
                if file == 'schema.json':
                    continue
                with open(os.path.join('recipes', file), 'r') as f:
                    try:
                        recipe_json = json.load(f)
                        jsonschema.validate(recipe_json, json.load(open('recipes/schema.json')))
                        recipe_list.append((file, recipe_json['recipe-name']))
                    except json.JSONDecodeError:
                        print(f'{file} is invalid json')
                    except jsonschema.exceptions.ValidationError as e:
                        print(f'{file} is invalid json schema')
        return recipe_list