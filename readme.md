# Eclipse Client

Eclipse Client is a custom Minecraft launcher by LuckyJojo11.

This is not an official Minecraft product. It is not affiliated with Mojang, Microsoft, Modrinth or CurseForge.

## Features

- Microsoft account login with refresh-token support
- Instance sidebar with create, edit and delete actions
- Separate working directory for every instance
- Per-instance worlds, servers, mods, resource packs, shader packs and settings
- Vanilla, Fabric, Forge and NeoForge support
- Per-instance RAM setting and optional demo mode
- Game console output inside the launcher
- Launch, kill and restart controls while a game is running
- Mod browser for Modrinth and CurseForge
- Add and remove mods from the mod browser
- Automatic download of required mod dependencies
- Browsable mod pages even when the search field is empty
- Import Modrinth `.mrpack` modpacks while creating an instance
- Bootstrap executable that checks for Python and required libraries

## Download

For normal users, publish the compiled `Eclipse Client.exe` through the GitHub Releases page.

Build artifacts are ignored by Git and should not be committed directly into the repository. This keeps the repository small and avoids uploading local logs, worlds, tokens and installed mods.

## Upload To GitHub

Create an empty repository on GitHub first. Then run these commands in the project folder:

```bat
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-NAME/YOUR-REPOSITORY.git
git push -u origin main
```

After pushing the source code, build the EXE locally and upload `Eclipse Client.exe` on the GitHub Releases page.

## Run From Source

Requirements:

- Windows
- Python 3.12
- A Microsoft account that owns Minecraft

Install dependencies:

```bat
py -3 -m pip install -r requirements.txt
```

Start the client:

```bat
py -3 lib\main.py
```

You can also run:

```bat
Install.bat
```

After that, start the launcher through:

```bat
Eclipse Client.vbs
```

## Build The EXE

Run:

```bat
Build EXE.bat
```

The script creates a local build environment, installs PyInstaller and builds `Eclipse Client.exe`.

The generated folders and files are ignored:

- `build/`
- `dist/`
- `build_venv/`
- `build_deps/`
- `Eclipse Client.exe`
- `Eclipse Client.spec`

Upload the finished executable to a GitHub Release instead of committing it.

## CurseForge

CurseForge support uses the official CurseForge API.

Set this environment variable before using CurseForge search:

```bat
setx CURSEFORGE_API_KEY "your-api-key"
```

Restart the launcher after changing the variable.

## Local Data

The launcher creates local runtime data while it is used. These files are ignored by Git:

- `instances/`
- `config/`
- `logs/`
- `lib/files/*.json`
- `eclipseclientlog.txt`
- `bootstrap.log`

This protects personal worlds, installed mods, local settings and login tokens from being uploaded.

## Supported Loaders

| Loader | Versions |
| --- | --- |
| Vanilla | All versions |
| Fabric | Supported by minecraft-launcher-lib |
| Forge | Supported by minecraft-launcher-lib |
| NeoForge | Supported by minecraft-launcher-lib |

For loader compatibility details, see the [minecraft-launcher-lib documentation](https://minecraft-launcher-lib.readthedocs.io/en/stable/).

## Project Status

Version 1.0 is a personal launcher project and still evolving. Expect rough edges around mod loader support, mod dependency handling and provider API behavior.

## Credits

Created by LuckyJojo11.

Thanks to Jengiz01 for the inspiration.
