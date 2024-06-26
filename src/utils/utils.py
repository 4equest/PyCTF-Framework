import re
import tempfile

def get_temp_folder():
    return tempfile.mkdtemp()

def replace_template(variables, template):
    pattern = re.compile(r'\{(.+?)\}')
    
    def replacer(match):
        path = match.group(1).split('.')
        value = variables
        for key in path:
            print(value)
            print(type(value))
            if isinstance(value, list):
                key = int(key)
            value = value[key]
        
        if type(value) == dict:
            return(str(value))
        return value
    return pattern.sub(replacer, template)

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