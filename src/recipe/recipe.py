import os
import json
import jsonschema

import module.module as md

import utils

class Recipe:
    def __init__(self, recipe_name, states) -> None:
        self.recipe_json = None
        self.recipe_list = self.get_recipe_list()
        self.recipe_name = recipe_name
        if self.recipe_name in self.recipe_list:
            self.recipe_path = self.recipe_list[recipe_name]
        else:
            raise KeyError(f"Error: {recipe_name} is not found.")
            
        self.states = states
        self.variables = {}
        with open(os.path.join("recipes", self.recipe_path), 'r') as f:
            self.recipe_json = json.load(f)
        if self.recipe_json['prepare-recipe-directory']:
            self.recipe_dir = utils.get_temp_folder()
            self.variables["recipe_dir"] = self.recipe_dir

        self.modules = []
        
        
    def run(self, args: list) -> None:
        
        # レシピ内変数の準備
        max_arg_num = utils.find_max_arg_num(json.dumps(self.recipe_json))
        if max_arg_num is not None and max_arg_num > len(args):
            raise Exception(f"Error: {module['name']} module/recipe requires {max_arg_num} arguments, but {len(args)} arguments are given.")

        self.variables["input"] = []
        
        for arg_count, arg in enumerate(args):
            template_arg = utils.replace_template_nostr(self.states, arg)
            if not template_arg is None:
                arg = template_arg
            self.variables["input"].append(arg)
            
        self.variables["inrecipe-names"] = []
        for module in self.recipe_json['execution-chain']:
            for arg_count, arg in enumerate(module['arguments']):
                module['arguments'][arg_count] = utils.replace_template(self.variables, arg)
                    
            if module["type"] == "module":
                this_execution = md.Module(module["name"], self.states)
            elif module["type"] == "recipe":
                this_execution = Recipe(module["name"], self.states)
                
            this_execution.run(module['arguments'])
            self.variables[module["inrecipe-name"]] = {"output": []}
            self.variables[module["inrecipe-name"]]["output"] = this_execution.get_result()
            self.variables["inrecipe-names"].append(module["inrecipe-name"])

            
    def get_result(self):
        self.variables["output"] = []
        for arg_count, arg in enumerate(self.recipe_json['output']):
            self.variables["output"].append(utils.replace_template_nostr(self.variables, arg))
            
        return self.variables["output"]
    
    def get_variables(self):
        return self.variables
    
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