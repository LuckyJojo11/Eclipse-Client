import json
import os
import shutil
import zipfile
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import launcher

USER_AGENT = "EclipseClient/1.0"

def request_json(url, headers=None):
    request_headers = {"User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))

def download_file(url, path, hashes=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        with open(path, "wb") as file:
            shutil.copyfileobj(response, file)
    return path

def mod_loader(loader):
    loader = loader.lower()
    if loader == "neoforge":
        return "neoforge"
    if loader == "forge":
        return "forge"
    if loader == "fabric":
        return "fabric"
    return loader

def search_modrinth(query, minecraft_version, loader, search_mode="Name", limit=20, offset=0):
    facets = [
        ["project_type:mod"],
        [f"versions:{minecraft_version}"],
        [f"categories:{mod_loader(loader)}"]
    ]
    params_data = {
        "limit": limit,
        "offset": offset,
        "facets": json.dumps(facets),
        "index": "downloads" if query == "" else "relevance"
    }
    if query != "":
        params_data["query"] = query
    params = urlencode(params_data)
    data = request_json(f"https://api.modrinth.com/v2/search?{params}")
    results = []
    for hit in data.get("hits", []):
        results.append({
            "provider": "Modrinth",
            "title": hit.get("title", ""),
            "project_id": hit.get("project_id", ""),
            "description": hit.get("description", ""),
            "icon_url": hit.get("icon_url", "")
        })
    return results

def select_primary_file(files):
    primary = None
    for file in files:
        if file.get("primary", False):
            primary = file
            break
    if primary is None and files:
        primary = files[0]
    return primary

def download_selected_file(selected, instance_directory, provider):
    if "files" in selected:
        primary = select_primary_file(selected.get("files", []))
    else:
        primary = selected
    if primary is None:
        raise RuntimeError(f"{provider} version has no files.")

    filename = primary.get("filename") or primary.get("fileName") or "mod.jar"
    download_url = primary.get("url") or primary.get("downloadUrl", "")
    if download_url == "":
        raise RuntimeError(f"{provider} did not provide a download URL for this file.")

    destination = os.path.join(instance_directory, "mods", filename)
    download_file(download_url, destination, primary.get("hashes", {}))
    return {
        "path": destination,
        "filename": filename
    }

def modrinth_project_title(project_id):
    try:
        project = request_json(f"https://api.modrinth.com/v2/project/{project_id}")
        return project.get("title", project_id)
    except Exception:
        return project_id

def select_modrinth_version(project_id, minecraft_version, loader):
    loaders = mod_loader(loader)
    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    versions = request_json(url)
    for version in versions:
        if minecraft_version in version.get("game_versions", []) and loaders in version.get("loaders", []):
            return version
    raise RuntimeError("No compatible Modrinth file found.")

def install_modrinth_version(version, minecraft_version, loader, instance_directory, installed_project_ids):
    project_id = version.get("project_id", "")
    if project_id in installed_project_ids:
        return {"path": "", "filename": "", "dependencies": []}
    installed_project_ids.add(project_id)

    installed = download_selected_file(version, instance_directory, "Modrinth")
    dependencies = []
    for dependency in version.get("dependencies", []):
        if dependency.get("dependency_type") != "required":
            continue
        dependency_project_id = dependency.get("project_id", "")
        try:
            if dependency.get("version_id", "") != "":
                dependency_version = request_json(f"https://api.modrinth.com/v2/version/{dependency.get('version_id')}")
                dependency_project_id = dependency_version.get("project_id", dependency_project_id)
            else:
                dependency_version = select_modrinth_version(dependency_project_id, minecraft_version, loader)

            dependency_installed = install_modrinth_version(
                dependency_version,
                minecraft_version,
                loader,
                instance_directory,
                installed_project_ids
            )
            if dependency_installed.get("path", "") != "":
                dependencies.append({
                    "provider": "Modrinth",
                    "project_id": dependency_project_id,
                    "title": modrinth_project_title(dependency_project_id),
                    "path": dependency_installed.get("path", "")
                })
            dependencies.extend(dependency_installed.get("dependencies", []))
        except Exception as e:
            launcher.log(f"Could not install Modrinth dependency {dependency_project_id}: {e}")

    installed["dependencies"] = dependencies
    return installed

def install_modrinth(project_id, minecraft_version, loader, instance_directory, installed_project_ids=None):
    if installed_project_ids is None:
        installed_project_ids = set()
    selected = select_modrinth_version(project_id, minecraft_version, loader)
    return install_modrinth_version(selected, minecraft_version, loader, instance_directory, installed_project_ids)

def curseforge_headers():
    api_key = os.environ.get("CURSEFORGE_API_KEY", "")
    if api_key == "":
        raise RuntimeError("CurseForge needs CURSEFORGE_API_KEY in your environment.")
    return {"x-api-key": api_key}

def search_curseforge(query, minecraft_version, loader, search_mode="Name", limit=20, offset=0):
    loader_ids = {"forge": 1, "fabric": 4, "neoforge": 6}
    params_data = {
        "gameId": 432,
        "classId": 6,
        "gameVersion": minecraft_version,
        "modLoaderType": loader_ids.get(mod_loader(loader), 0),
        "pageSize": limit,
        "index": offset,
        "sortField": 2,
        "sortOrder": "desc"
    }
    if query != "":
        params_data["searchFilter"] = query
    params = urlencode(params_data)
    data = request_json(f"https://api.curseforge.com/v1/mods/search?{params}", curseforge_headers())
    results = []
    for item in data.get("data", []):
        logo = item.get("logo") or {}
        results.append({
            "provider": "CurseForge",
            "title": item.get("name", ""),
            "project_id": str(item.get("id", "")),
            "description": item.get("summary", ""),
            "icon_url": logo.get("thumbnailUrl", "")
        })
    return results

def curseforge_mod_name(project_id):
    try:
        data = request_json(f"https://api.curseforge.com/v1/mods/{project_id}", curseforge_headers())
        return data.get("data", {}).get("name", str(project_id))
    except Exception:
        return str(project_id)

def install_curseforge(project_id, minecraft_version, loader, instance_directory, installed_project_ids=None):
    if installed_project_ids is None:
        installed_project_ids = set()
    project_id = str(project_id)
    if project_id in installed_project_ids:
        return {"path": "", "filename": "", "dependencies": []}
    installed_project_ids.add(project_id)

    loader_ids = {"forge": 1, "fabric": 4, "neoforge": 6}
    params = urlencode({
        "gameVersion": minecraft_version,
        "modLoaderType": loader_ids.get(mod_loader(loader), 0),
        "pageSize": 20
    })
    data = request_json(f"https://api.curseforge.com/v1/mods/{project_id}/files?{params}", curseforge_headers())
    files = data.get("data", [])
    if not files:
        raise RuntimeError("No compatible CurseForge file found.")
    selected = files[0]
    installed = download_selected_file(selected, instance_directory, "CurseForge")
    dependencies = []
    for dependency in selected.get("dependencies", []):
        if dependency.get("relationType") != 3:
            continue
        dependency_project_id = str(dependency.get("modId", ""))
        try:
            dependency_installed = install_curseforge(
                dependency_project_id,
                minecraft_version,
                loader,
                instance_directory,
                installed_project_ids
            )
            if dependency_installed.get("path", "") != "":
                dependencies.append({
                    "provider": "CurseForge",
                    "project_id": dependency_project_id,
                    "title": curseforge_mod_name(dependency_project_id),
                    "path": dependency_installed.get("path", "")
                })
            dependencies.extend(dependency_installed.get("dependencies", []))
        except Exception as e:
            launcher.log(f"Could not install CurseForge dependency {dependency_project_id}: {e}")

    installed["dependencies"] = dependencies
    return installed

def search_mods(provider, query, minecraft_version, loader, search_mode="Name", limit=20, offset=0):
    if provider == "Modrinth":
        return search_modrinth(query, minecraft_version, loader, search_mode, limit, offset)
    if provider == "CurseForge":
        return search_curseforge(query, minecraft_version, loader, search_mode, limit, offset)
    return []

def install_mod(provider, project_id, minecraft_version, loader, instance_directory):
    if provider == "Modrinth":
        return install_modrinth(project_id, minecraft_version, loader, instance_directory)
    if provider == "CurseForge":
        return install_curseforge(project_id, minecraft_version, loader, instance_directory)
    raise RuntimeError("Unknown mod provider.")

def import_mrpack(path, target_directory):
    with zipfile.ZipFile(path, "r") as pack:
        index = json.loads(pack.read("modrinth.index.json").decode("utf-8"))
        dependencies = index.get("dependencies", {})
        minecraft_version = dependencies.get("minecraft", "")
        loader = "Vanilla"
        loader_version = ""
        for key, label in [("fabric-loader", "Fabric"), ("forge", "Forge"), ("neoforge", "NeoForge")]:
            if key in dependencies:
                loader = label
                loader_version = dependencies[key]
                break

        launcher.ensure_game_directory(target_directory)
        for item in index.get("files", []):
            env = item.get("env", {})
            if env.get("client") == "unsupported":
                continue
            downloads = item.get("downloads", [])
            if not downloads:
                continue
            destination = os.path.join(target_directory, item.get("path", ""))
            download_file(downloads[0], destination, item.get("hashes", {}))

        for member in pack.namelist():
            if not member.startswith("overrides/") or member.endswith("/"):
                continue
            relative = member[len("overrides/"):]
            destination = os.path.join(target_directory, relative)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with pack.open(member) as source, open(destination, "wb") as target:
                shutil.copyfileobj(source, target)

    return {
        "name": index.get("name", os.path.splitext(os.path.basename(path))[0]),
        "version": minecraft_version,
        "mod_info": [loader, loader_version]
    }
