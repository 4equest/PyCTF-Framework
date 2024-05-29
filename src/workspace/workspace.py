from module import Module
from recipe import Recipe

class WorkSpace:
    def __init__(self) -> None:
        self.module_state = [] # モジュール ID(連番とか) 実行状態
        self.recipe_state = [] # レシピ ID(連番とか) 実行状態
        
    def create_workspace(self) -> None:
        # 新規作成の場合 loadと被る部分は__init__にいれるべき
        pass
    
    def load_workspace(self) -> None:
        pass
    
    def save_workspace(self) -> None:
        pass
    
    def run_module(self, module_name, args) -> int:
        module = Module(module_name)
        module.run(args)
        module_id = self.get_next_module_id()
        self.module_state.append({
            "module":module,
            "id": module_id,
            "running":False
            })
        
        return module_id
        
    
    async def run_module_async(self, module_name, args) -> int:
        pass
    
    def get_module_result(self, id) -> None:
        pass
    
    def run_recipe(self, recipe_name, args) -> int:
        recipe = Recipe(recipe_name)
        recipe.run(args)
        recipe_id = self.get_next_recipe_id()
        self.recipe_state.append({
            "recipe":recipe,
            "id": recipe_id,
            "running":False
            })
        
        return recipe_id
    
    async def run_recipe_async(self, recipe_name, args) -> int:
        pass
    
    def get_recipe_result(self, id) -> None:
        pass
    
    def get_next_module_id(self) -> int:
        pass
    
    def get_next_recipe_id(self) -> int:
        pass

    def run_cmd(self) -> None:
        """OSコマンドの実行
        """
        pass
    
