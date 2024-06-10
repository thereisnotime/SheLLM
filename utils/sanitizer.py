import re

def remove_code_block(input_string):
    return re.sub(r'```[a-zA-Z]*\n', '', input_string)
