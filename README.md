# OSRS Leagues Comparison Tool

This package can be used to compare OSRS leagues accounts on an individual task level.

It takes a little bit to run while it emulates opening a browser to grab league progress.


## Installation

```bash
pip install git+https://github.com/k2bd/leaguespy
```


## Usage

See available commands with:

```bash
leaguespy --help
```

Commands have some shared optional arguments:
- `--regions`: A comma-separated list of unlockable regions to include. Defaults to all regions. You can type full names, or common single-letter abbreviations (e.g. 'a' for Asgarnia, 'z' for Zeah, ...)
- `--columns`: A comma-separated list of table columns to include. Defaults to all columns.
- `--exclude-global`: Exclude global tasks and tasks from Misthalin and Karamja
### Suggesting tasks

This will list any tasks you haven't done and that any of your friends have done. Put yourself first in the list.

```bash
leaguespy suggest [--regions [...]] [--exclude-global] player1 player2 [...]
```

### Listing tasks completed by a group

This will list all tasks any of the given players have done

```bash
leaguespy tasks [--regions [...]] [--exclude-global] player1 player2 [...]
```
