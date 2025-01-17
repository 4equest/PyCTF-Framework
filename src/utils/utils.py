import re
import json
import tempfile

def get_temp_folder():
    return tempfile.mkdtemp()

def find_max_arg_num(input_string):
    pattern = r'\{input\.(\d+)\}'
    matches = re.findall(pattern, input_string)
    numbers = map(int, matches)
    return max(numbers, default=None)

def replace_template(variables, template):
    pattern = re.compile(r'\{(.+?)\}')
    
    def replacer(match):
        path = match.group(1).split('.')
        value = variables
        for key in path:
            if isinstance(value, list):
                key = int(key)
                
            value = value[key]
        
        if type(value) == dict or type(value) == list:
            value = json.dumps(value)
        return value
    
    return pattern.sub(replacer, template)

def replace_template_nostr(variables: dict, template: str):
    if not (template.startswith("{") and template.endswith("}")):
        return None
        
    keys = template.strip("{}").split(".")
    obj = variables.copy()
    for key in keys:
        try:
            if isinstance(obj, list):  # json_objがリストの場合
                key = int(key) 
            obj = obj[key]
        except (KeyError, IndexError, TypeError):
            return None  # キーが存在しない場合はNoneを返す

    return obj

def filter_object(obj, allowed_types=(str, int, float, bool, list, dict, type(None))):
    """
    任意のオブジェクトからjsonに変換可能なオブジェクトのみを取り出す
    """
    if isinstance(obj, dict):
        # 辞書の場合、キーと値をループして新しい辞書を作成
        return {k: filter_object(v, allowed_types) for k, v in obj.items() if isinstance(v, allowed_types)}
    elif isinstance(obj, list):
        # リストの場合、要素をループして新しいリストを作成
        return [filter_object(x, allowed_types) for x in obj if isinstance(x, allowed_types)]
    elif isinstance(obj, allowed_types):
        # 許可された型の場合、そのまま返す
        return obj
    else:
        # それ以外の型の場合、Noneを返す
        return None