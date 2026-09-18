import json

find_file_schema = {
    "type": "function",
    "function": {
        "name": "find_file",
        "description": "Searches the system for a file matching a given name.",
        "parameters": {
                "type": "object",
                "required": ["filename"],
                "properties": {
                    "filename": {"type": "string", "description": "The exact or partial name of the file to locate."}
                }
            }
    },
}

print(json.dumps(find_file_schema, indent=2))