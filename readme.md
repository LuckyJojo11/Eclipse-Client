# Eclipse Client

A custom Minecraft launcher for Windows, created by LuckyJojo11.

Eclipse Client focuses on simple instance management, modded Minecraft support and a built-in game console. It can create separate working directories for every instance, install mods from Modrinth and CurseForge, import `.mrpack` modpacks and start Vanilla, Fabric, Forge or NeoForge profiles.

This project is not an official Minecraft product and is not affiliated with Mojang, Microsoft, Modrinth or CurseForge.

## Features

- Microsoft account login
- Refresh-token login on app start
- Create, edit and delete Minecraft instances
- Separate instance folders for worlds, servers, mods, resource packs, shader packs and settings
- Vanilla, Fabric, Forge and NeoForge support
- Per-instance RAM slider and manual RAM input
- Optional demo mode per instance
- Built-in console for launcher and game output
- Launch, kill and restart controls for running instances
- Mod browser with Modrinth and CurseForge support
- Search by name or description
- Browse mods even with an empty search field
- Page selector and result-count dropdown for mod browsing
- Add and remove mods from the launcher
- Automatic download of required mod dependencies
- Import Modrinth `.mrpack` modpacks while creating an instance
- Bootstrap executable that checks Python, required libraries and GitHub releases

## Download

The easiest way to use Eclipse Client is to download `Eclipse Client.exe` from the GitHub Releases page.

After downloading it, place it in an empty folder and start it with a double click. The launcher will open a small installer-style setup window and check whether the source files, Python and the required libraries are installed. If something is missing, it will ask whether it should download or install the missing parts.

On the first start, Eclipse Client can also create a Desktop shortcut and a Start Menu entry.

When a newer GitHub Release exists, the bootstrap executable can download the latest source code before starting the client. Local instances, worlds, mods, logs and login data are kept.

## Requirements

- Windows
- Python 3.12 if running from source
- A Microsoft account that owns Minecraft
- Internet connection for login, Minecraft downloads, loader downloads and mod search

## Run From Source

Install the Python dependencies:

```bat
py -3 -m pip install -r lib\applicationresources\requirements.txt
```

Start the client:

```bat
py -3 lib\main.py
```

You can also run the setup script:

```bat
lib\applicationresources\Install.bat
```

Then start the client without a console window:

```bat
lib\applicationresources\Eclipse Client.vbs
```

## Build The EXE

Run:

```bat
lib\applicationresources\Build EXE.bat
```

The script creates a local build environment, installs PyInstaller and builds `Eclipse Client.exe`.

Generated build files are ignored by Git:

- `build/`
- `dist/`
- `build_venv/`
- `build_deps/`
- `Eclipse Client.exe`
- `Eclipse Client.spec`

Upload the finished executable as a GitHub Release instead of committing it to the repository.

Before creating a new release, update `APP_VERSION` in `lib/bootstrap.py` to the new release tag, for example `v1.0.1`.

## Project Structure

Files that are needed by the bootstrapper but are not part of the main application UI live in:

```text
lib/applicationresources/
```

This includes setup scripts, build scripts, requirements and local bootstrap logs.

## Instances

Each instance has its own folder in `instances/`. This keeps worlds, servers, mods and settings separate between profiles.

Deleting an instance removes it from the launcher list, but the instance folder is kept. If you create another instance with the same name, version and loader, the old files can be reused.

## Modding

Modded instances can install mods from:

- Modrinth
- CurseForge

The mod page shows results in a scrollable list with preview image, name, description and an `Add` or `Remove` button.

When a mod is installed, Eclipse Client also tries to download required dependencies automatically.

CurseForge support requires an API key. Set it as an environment variable:

```bat
setx CURSEFORGE_API_KEY "your-api-key"
```

Restart the launcher after changing this variable.

## Modpack Import

When creating an instance, you can import a Modrinth `.mrpack` file. The launcher reads the pack metadata, creates a matching instance and downloads the files into that instance directory.

## Local Data

The launcher creates local runtime data while it is used. These files are ignored by Git:

- `instances/`
- `config/`
- `logs/`
- `lib/files/*.json`
- `.eclipse_client_version`
- `lib/applicationresources/.eclipse_client_version`
- `lib/applicationresources/.setup_done`
- `lib/applicationresources/eclipseclientlog.txt`
- `lib/applicationresources/bootstrap.log`
- `eclipseclientlog.txt`
- `bootstrap.log`

This prevents personal worlds, installed mods, local settings and login tokens from being uploaded.

## Supported Loaders

| Loader | Support |
| --- | --- |
| Vanilla | Minecraft versions provided by minecraft-launcher-lib |
| Fabric | Supported Fabric versions |
| Forge | Supported Forge versions |
| NeoForge | Supported NeoForge versions |

Loader support depends on what `minecraft-launcher-lib` and the loader providers expose. See the [minecraft-launcher-lib documentation](https://minecraft-launcher-lib.readthedocs.io/en/stable/) for details.

## Project Status

Eclipse Client is a personal launcher project and still evolving. Some loader versions, mod files or dependency downloads may fail when external providers do not expose compatible files.

## Credits

Created by LuckyJojo11.

Thanks to Jengiz01 for the inspiration.
