
import json, os
from jsonschema import Draft4Validator

def validate_json(instance: dict, schema_path: str):
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    Draft4Validator(schema).validate(instance)
