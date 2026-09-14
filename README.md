Sledenje objektom
=================
Install from git:
```shell
pip install git+https://github.com/RoboLiga/sledenje-objektom-2
```

Install locally:
```
pip install -e <path-to-folder>
```

### CLI reference

#### `main.py` — run the Robo Liga FRI tracker server

**Synopsis**

```shell
uv run main.py [-g PATH] [-t PATH] [-s]
uv run main.py -h
```

Starts the tracker server or runs an interactive setup to mark the game area and fields.

**Options**

| Flag | Long form | Argument | Description |
|------|-----------|----------|--------------|
| `-h` | `--help` | | Show usage information and exit. |
| `-g` | `--game-config` | `PATH` | Path to the game configuration YAML file. |
| `-t` | `--tracker-config` | `PATH` | Path to the tracker configuration YAML file. Default: `./tracker_config.yaml`. |
| `-s` | `--setup` | | Run tracker setup instead of starting the server, to mark the game area and fields before the first run of a game. |

**Examples**

Mark the game area and fields for `orchard_config.yaml` before first use:
```shell
uv run main.py --game-config './orchard_config.yaml' --setup
```

Run the tracker server for `orchard_config.yaml`:
```shell
uv run main.py --game-config './orchard_config.yaml'
```

**Exit status:** `0` on success or `--help`, `1` on an invalid option, and an unhandled exception (e.g. missing `--game`) otherwise.