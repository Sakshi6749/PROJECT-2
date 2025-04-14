import os, json, io, re

def execute(question: str, parameter, file_bytes = None):
    if file_bytes:
        json_file = io.BytesIO(file_bytes)
        json_str = json_file.read()
        data = json.loads(json_str)
    else:
        data = extract_and_sort_json(question)

    return sort_json_array(data, parameter["json_column_name"][0], parameter["json_column_name"][1])


def sort_json_array(data, sort_by, tie_breaker):
    try:
        # Sort by sort_by, then by tie_breaker
        sorted_data = sorted(data, key=lambda x: (x[sort_by], x[tie_breaker]))
        return json.dumps(sorted_data, separators=(',', ':'))
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Invalid input: {str(e)}")

def extract_and_sort_json(input_string):
    """
    Extracts a JSON array from a given string and sorts it by age.
    :param input_string: str, input containing JSON data
    :return: str, sorted JSON array as a compact string
    """
    pattern = r'\[\{.*?\}\]'
    match = re.search(pattern, input_string)

    if match:
        json_str = match.group(0)
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError:
            return None

    return None
