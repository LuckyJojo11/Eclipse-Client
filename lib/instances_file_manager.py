import json
import os
import re
import launcher
from data_reader import *

FILE = "lib\\files\\instances.json"
INSTANCES_FOLDER = "instances"

def ensure_path(path: str):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f, indent=4)

def _read_instances():
    ensure_path(FILE)
    with open(FILE, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return []
    return data

def _write_instances(data):
    ensure_path(FILE)
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_instance(name):
    for instance in get_all_instances():
        if instance.get("name") == name:
            return instance
    return None

def safe_folder_name(name):
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    safe_name = safe_name.strip("._-")
    return safe_name if safe_name else "instance"

def get_unique_instance_directory(name, existing_directory=""):
    if existing_directory:
        return existing_directory

    base_name = safe_folder_name(name)
    directory = os.path.join(INSTANCES_FOLDER, base_name)
    counter = 2
    while os.path.exists(directory):
        directory = os.path.join(INSTANCES_FOLDER, f"{base_name}_{counter}")
        counter += 1
    return directory

def ensure_instance_directory(instance):
    directory = instance.get("directory", "")
    if directory == "":
        directory = get_unique_instance_directory(instance.get("name", "instance"))
        instance["directory"] = directory
    launcher.ensure_game_directory(directory)
    return directory

def ensure_instance_settings(instance):
    changed = False
    if "ram" not in instance:
        instance["ram"] = 4096
        changed = True
    if "demo" not in instance:
        instance["demo"] = False
        changed = True
    if "installed_mods" not in instance:
        instance["installed_mods"] = []
        changed = True
    return changed

# Create a Instance
def create_or_edit_instance(name, version, modinfo, toUpdate="", directory=""):
    ensure_path(FILE)
    name = name.strip()
    version = version.strip()
    if not name or not version or not modinfo:
         return False

    loader = modinfo[0] if len(modinfo) > 0 else ""
    loader_version = modinfo[1] if len(modinfo) > 1 else ""
    if loader not in ["Vanilla", "Fabric", "Forge", "NeoForge"]:
        return False
    if loader in ["Fabric", "Forge", "NeoForge"] and not loader_version.strip():
        return False

    existing_directory = directory
    existing_ram = 4096
    existing_demo = False
    if toUpdate:
        old_instance = get_instance(toUpdate)
        if old_instance is not None:
            existing_directory = old_instance.get("directory", "")
            existing_ram = old_instance.get("ram", 4096)
            existing_demo = old_instance.get("demo", False)

    instance = {
        "name": name,
        "version": version,
        "mod_info": [loader, loader_version.strip()],
        "directory": get_unique_instance_directory(name, existing_directory),
        "ram": existing_ram,
        "demo": existing_demo,
        "installed_mods": old_instance.get("installed_mods", []) if toUpdate and old_instance is not None else []
    }
    ensure_instance_directory(instance)

    data = _read_instances()

    for i in data:
        if i.get("name") == name and i.get("name") != toUpdate:
            return False
    
    new_data = []
    updated = False
    for i in data:
        if i.get("name") == toUpdate:
            new_data.append(instance)
            updated = True
        else:
            new_data.append(i)

    if not updated:
        new_data.insert(0, instance)

    _write_instances(new_data)
    return True

# Delete a Instance
def delete_instance(name):
    ensure_path(FILE)

    data = _read_instances()
    
    new_data = []
    for i in data:
            if not i.get("name") == name:
                new_data.append(i)

    _write_instances(new_data)
    return True

def get_all_instances():
    data = _read_instances()
    changed = False
    for instance in data:
        if ensure_instance_settings(instance):
            changed = True
        if instance.get("directory", "") == "":
            ensure_instance_directory(instance)
            changed = True
        else:
            launcher.ensure_game_directory(instance["directory"])
    if changed:
        _write_instances(data)
    #print(data)
    return data

def start_instance(name):
    ensure_path(FILE)

    data = _read_instances()

    body = []
    play_instance = {}

    for i in data:
        if i.get("name") == name:
            play_instance = i
        else:
            body.append(i)
    if play_instance == {}:
        return False
    ensure_instance_settings(play_instance)
    
    data = [play_instance]
    for i in body:
        data.append(i)

    _write_instances(data)

    instance_directory = ensure_instance_directory(play_instance)
    _write_instances(data)

    launcher.run_game(
        get_permanent_key("name"),
        get_permanent_key("uuid"),
        get_permanent_key("token"),
        play_instance["version"],
        modded=play_instance["mod_info"],
        instance_directory=instance_directory,
        ram=play_instance.get("ram", 4096),
        demo=play_instance.get("demo", False),
        instance_name=play_instance["name"]
    )

def is_instance_running(name):
    return launcher.is_game_running(name)

def kill_instance(name):
    return launcher.kill_game(name)

def restart_instance(name):
    kill_instance(name)
    return start_instance(name)

def update_instance_launch_settings(name, ram, demo):
    data = _read_instances()
    updated = False
    for instance in data:
        if instance.get("name") == name:
            instance["ram"] = int(ram)
            instance["demo"] = bool(demo)
            updated = True
            break
    if updated:
        _write_instances(data)
    return updated

def get_installed_mods(name):
    instance = get_instance(name)
    if instance is None:
        return []
    return instance.get("installed_mods", [])

def add_installed_mod(name, mod):
    data = _read_instances()
    for instance in data:
        if instance.get("name") == name:
            ensure_instance_settings(instance)
            installed = []
            for existing in instance.get("installed_mods", []):
                if not (existing.get("provider") == mod.get("provider") and existing.get("project_id") == mod.get("project_id")):
                    installed.append(existing)
            installed.append(mod)
            instance["installed_mods"] = installed
            _write_instances(data)
            return True
    return False

def remove_installed_mod(name, provider, project_id):
    data = _read_instances()
    for instance in data:
        if instance.get("name") == name:
            ensure_instance_settings(instance)
            removed = None
            installed = []
            for existing in instance.get("installed_mods", []):
                if existing.get("provider") == provider and existing.get("project_id") == project_id:
                    removed = existing
                else:
                    installed.append(existing)
            instance["installed_mods"] = installed
            _write_instances(data)
            return removed
    return None

#start_instance("My second Instance")
