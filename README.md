# Mod Organizer 2: Mod Requirement Checker
Checks installed mods for missing requirements.

## Installation
Download the latest archive from [releases pages](../../releases/latest) and extract the
contents (including `mod_requirement_checker`) into the MO2 `plugins/` directory.

## Requirements and how to define requirements
Mod Requirement Checker uses `ModRequirement` definitions from the current game
or game feature (implementing `IWithModRequirements`).

See [`basic_games.basic_features`](https://github.com/ZashIn/modorganizer-basic_games/tree/game_valheim/basic_features) (submodule) for details.

Folder structure:
```
plugins/
  basic_games/
    basic_features/
      __init__.py
      mod_requirement.py # IWithModRequirements, ModRequirement
      ...
    games/
      game_xyz.py  # Game implementing IWithModRequirements
      ...
  mod_requirement_checker/
    __init__.py
    ...
ModOrganizer.exe
```

