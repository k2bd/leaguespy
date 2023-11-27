# OSRS Leagues Comparison Tool

This package can be used to compare OSRS leagues accounts on an individual task level.


## Installation

```bash
pip install leaguespy
```


## Usage

See available commands with:

```bash
leaguespy --help
```

### Listing completed tasks

This will list all tasks any of the given players have done

```bash
leaguespy tasks [--regions asgarnia,morytania] [--exclude-global] player1 player2 [...]
```

### Suggesting tasks

This will list any tasks you haven't done and that any of your friends have done. Put yourself first in the player list.

```bash
leaguespy suggest [--regions asgarnia,morytania] [--exclude-global] player1 player2 [...]
```
