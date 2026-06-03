import os
import json

# Paths to the Save Files
TEMPORARY = "lib\\files\\temporary_data.json" # Saves Temporary Data, like Variables. Is cleared at every start.
PERMANENT = "lib\\files\\permanent_data.json" # Saves Permanent Data, like Username, UUID and Refresh Token.

# Creates the Path, if the File doesn't exist
def ensure_path(path: str = ""):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("{}")

# Clears the Temporary Data
def clear_temporary_data(info: str = "{}"):
    ensure_path(TEMPORARY)
    
    with open(TEMPORARY, "w") as f:
        json.dump(info, f, indent=4)
    return

# Clears the Permanent Data
def clear_permanent_data(info: str = "{}"): #DANGER
    ensure_path(PERMANENT)
    
    with open(PERMANENT, "w") as f:
        json.dump(info, f, indent=4)
    return

# Reads the Temporary Data
def get_temporary_data():
    info = "{}"
    ensure_path(TEMPORARY)
    with open(TEMPORARY, "r") as f:
        info = json.load(f)
    return info

# Reads the Permanent Data
def get_permanent_data():
    info = "{}"
    ensure_path(PERMANENT)
    with open(PERMANENT, "r") as f:
        info = json.load(f)
    return info

# Deletes a specific Key from Temporary Data
def delete_temporary_key(key: str = ""):
    ensure_path(TEMPORARY)
    if key == "":
        return
    with open(TEMPORARY, "r") as f:
        data = json.load(f)  
    data.pop(key, None)
    with open(TEMPORARY, "w") as f:
        json.dump(data, f, indent=4)
    return
    
# Deletes a specific Key from Permanent Data
def delete_permanent_key(key: str = ""):
    ensure_path(PERMANENT)
    if key == "":
        return
    with open(PERMANENT, "r") as f:
        data = json.load(f)  
    data.pop(key, None)
    with open(PERMANENT, "w") as f:
        json.dump(data, f, indent=4)
    return

# Creates a Key + Value from Temporary Data
def create_temporary_key(key, value):
    ensure_path(TEMPORARY)
    if key == "":
        return
    with open(TEMPORARY, "r") as f:
        data = json.load(f)
    data[key] = value
    
    with open(TEMPORARY, "w") as f:
        json.dump(data, f, indent=4)
    return

# Creates a Key + Value from Permanent Data
def create_permanent_key(key, value):
    ensure_path(PERMANENT)
    if key == "":
        return
    with open(PERMANENT, "r") as f:
        data = json.load(f)
    data[key] = value
    
    with open(PERMANENT, "w") as f:
        json.dump(data, f, indent=4)
    return

# Returns a Key + Value from Temporary Data
def get_temporary_key(key):
    ensure_path(TEMPORARY)
    if key == "":
        return
    with open(TEMPORARY, "r") as f:
        data = json.load(f)
    value = data[key]
    return value

# Returns a Key + Value from Permanent Data
def get_permanent_key(key):
    ensure_path(PERMANENT)
    if key == "":
        return
    with open(PERMANENT, "r") as f:
        data = json.load(f)
    value = data[key]
    return value

if __name__ == "__main__":
    print("Please run the App via 'main.py'")
