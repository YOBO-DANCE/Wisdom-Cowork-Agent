ai_response = {
    "status": "call_tool",
    "tool_call": {
        "name": "move_file",
        "arguments": {
            "source_path": "Desktop/notes.txt",
            "destination_folder": "Desktop/Backup"
        }
    }
}

name = ai_response["tool_call"]
func_name = name["name"]

arg = name["arguments"]

s_path = arg["source_path"]
des_path = arg["destination_folder"]

print(f"Executing {func_name} from {s_path} to {des_path}")