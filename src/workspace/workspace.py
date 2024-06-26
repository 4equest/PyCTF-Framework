import utils
from module import Module
from recipe import Recipe
import uuid

class WorkSpace:
    def __init__(self,
                module_state = [], # モジュール ID(連番とか) 実行状態 モジュールは実行後に破棄してoutputだけ保持しておくべき
                recipe_state = [], # レシピ ID(連番とか) 実行状態 レシピは実行後に破棄してoutputだけ保持しておくべき
                cmd_state = [],
                workspace_name = "default_workspace",
                workspace_id = "workspace-" + str(uuid.uuid4()),
                #workspace_path = "./default_workspace.json",
                ) -> None:
        self.module_state = module_state
        self.recipe_state = recipe_state
        self.cmd_state = cmd_state
        self.workspace_name = workspace_name
        self.workspace_id = workspace_id
        #self.workspace_path = workspace_path
        
    def create_workspace(self) -> None:
        # 新規作成の場合 loadと被る部分は__init__にいれるべき
        pass
    
    def load_workspace(self) -> None:
        pass
    
    def save_workspace(self) -> None:
        # 実行中のモジュール、レシピがある場合は保存無理
        pass
    
    def run_module(self, module_name: str, args: list) -> str:
        module = Module(module_name)
        module.run(args)
        module_id = self.get_next_module_id()
        self.module_state.append({
            module_id:{
                "module" : module,
                "running": False, # syncなのでFalse
                "output" : []
            }})
        
        return module_id
        
    
    async def run_module_async(self, module_name, args) -> int:
        pass
    
    def get_module_result(self, id: str) -> object:
        if id not in self.module_state:
            raise KeyError("module_id: {} not found".format(id))
        self.module_state[id]["output"] = self.module_state[id]["module"].get_result()
        return self.module_state[id]["output"]
    
    def get_module_state_list(self) -> object:
        return self.module_state
    
    def get_module_list(self) -> list:
        return Module.get_module_list()
    
    def get_module_info(modulename: str) -> object:
        # todo descriptionなどを返せたらいいな
        pass
            
    def run_recipe(self, recipe_name: str, args: list) -> str:
        recipe = Recipe(recipe_name)
        recipe.run(args)
        recipe_id = self.get_next_recipe_id()
        self.recipe_state.append({
            recipe_id:{
                "recipe" : recipe,
                "running": False,
                "output" : []
            }})
        
        return recipe_id
    
    async def run_recipe_async(self, recipe_name, args) -> int:
        pass
    
    def get_recipe_result(self, id) -> object:
        if id not in self.recipe_state:
            raise KeyError("recipe_id: {} not found".format(id))
        self.recipe_state[id]["output"] = self.recipe_state[id]["recipe"].get_result()
        return self.recipe_state[id]["output"]
    
    def get_recipe_state_list(self) -> object:
        return self.recipe_state
    
    def get_recipe_list(self) -> list:
        return Recipe.get_recipe_list()

    def get_recipe_info(recipe_name: str) -> object:
        # todo descriptionなどを返せたらいいな
        pass
    
    def run_cmd(self, args: list) -> str:
        pass
    
    def run_cmd_async(self, args: list) -> str:
        pass
    
    def get_cmd_result(self, id: str) -> object:
        pass

    def get_next_module_id(self) -> str:
        return "module-" + str(uuid.uuid4())
    
    def get_next_recipe_id(self) -> str:
        return "recipe-" + str(uuid.uuid4())
    
    def get_next_cmd_id(self) -> str:
        return "cmd-" + str(uuid.uuid4())