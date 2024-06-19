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
        return str(value)
    return pattern.sub(replacer, template)