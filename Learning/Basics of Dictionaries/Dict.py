# My Solution
Main_dict = {"name": "organize_desktop", "enabled": True, "version": 1.0}

Main_dict.update({"category": "file_system"})
print(Main_dict)

print(Main_dict["name"])
print(Main_dict.get("description", "No description provided"))


# AI Solution
# Fixed data types: True (bool), 1.0 (float)
Main_dict = {
    "name": "organize_desktop", 
    "enabled": True, 
    "version": 1.0
}

# Simplified key insertion
Main_dict["category"] = "file_system"

# Retrieval
print(Main_dict["name"])
print(Main_dict.get("description", "No description provided"))