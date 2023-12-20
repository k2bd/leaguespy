#imports
import pandas as pd
import typer
from tabulate import tabulate

from leaguespy.player_stats import get_player_stats
from leaguespy.player_task_info import PlayerTaskInfo
from typing_extensions import Annotated

# define typer app
app = typer.Typer(
    help="OSRS Leagues Comparison Tool",
    add_completion=False)

# define constants
ASGARNIA = "asgarnia"
DESERT = "desert"
FREMENNIK = "fremennik"
KANDARIN = "kandarin"
MORYTANIA = "morytania"
TIRANNWN = "tirannwn"
WILDERNESS = "wilderness"
KOUREND = "kourend"
GENERAL = "general"
KARAMJA = "karamja"
MISTHALIN = "misthalin"

COL_TASKID = "taskid"
COL_REGION = "region"
COL_DESCRIPTION = "description"
COL_POINTS = "points"
COL_COMPLETION_PCT = "completion_pct"
COL_USERNAMES = "usernames"

# define arguments
REGIONS_OPTION = typer.Option(
    help="Comma-separated list of regions to include. "
    "Valid values: asgarnia, desert, fremennik, kandarin, morytania, tirannwn, "
    "wilderness, kourend",
)
COLUMNS_OPTION = typer.Option(
    help="Comma-separated list of columns to exclude. "
    "Valid values: taskid, region, description, points, completion_pct, usernames",
)
EXCLUDE_GLOBAL_OPTION = typer.Option(
    help="Exclude general and shared-region tasks from the results"
)
PLAYERS_ARGUMENT = typer.Argument(
    help="Players to report task completion on",
)

# define functions
def parse_regions(regions_str: str) -> list[str]:
    regions = (
        [r.strip().lower() for r in regions_str.split(",")]
        if regions_str
        else [
            ASGARNIA,
            DESERT,
            FREMENNIK,
            KANDARIN,
            MORYTANIA,
            TIRANNWN,
            WILDERNESS,
            KOUREND,
        ]
    )

    results = set()
    for region in regions:
        if region in ["a", ASGARNIA, "asg"]:
            results.add(ASGARNIA)
        elif region in ["d", DESERT, "des"]:
            results.add(DESERT)
        elif region in ["f", FREMENNIK, "frem"]:
            results.add(FREMENNIK)
        elif region in ["k", KANDARIN, "kand"]:
            results.add(KANDARIN)
        elif region in ["m", MORYTANIA, "mory"]:
            results.add(MORYTANIA)
        elif region in ["t", TIRANNWN, "elf", "tir"]:
            results.add(TIRANNWN)
        elif region in ["w", WILDERNESS, "wildy"]:
            results.add(WILDERNESS)
        elif region in ["z", KOUREND, "zeah"]:
            results.add(KOUREND)
        else:
            raise ValueError(f"Unknown region: {region}")

    return list(results)


def parse_columns(columns_str: str) -> list[str]:
    columns = (
        [r.strip().lower() for r in columns_str.split(",")]
        if columns_str
        else [
            COL_TASKID,
            COL_REGION,
            COL_DESCRIPTION,
            COL_POINTS,
            COL_COMPLETION_PCT,
            COL_USERNAMES,
        ]
    )

    results = set()
    for col in columns:
        if col == COL_TASKID:
            results.add(COL_TASKID)
        elif col == COL_REGION:
            results.add(COL_REGION)
        elif col == COL_DESCRIPTION:
            results.add(COL_DESCRIPTION)
        elif col == COL_POINTS:
            results.add(COL_POINTS)
        elif col == COL_COMPLETION_PCT:
            results.add(COL_COMPLETION_PCT)
        elif col == COL_USERNAMES:
            results.add(COL_USERNAMES)
        else:
            raise ValueError(f"Unknown column: {col}")

    return list(results)

def get_tasks_df(
    regions_str: str,
    columns_str: str,
    exclude_global: bool,
    players: list[str],
):
    """Get a players tasks and returns a dataframe with the results"""
    if len(players) == 0:
        raise ValueError("Must specify at least one player")

    selected_regions = parse_regions(regions_str)

    if not exclude_global:
        selected_regions.extend([GENERAL, MISTHALIN, KARAMJA])

    players_stats: dict[str, dict[int, PlayerTaskInfo]] = {}

    for player in players:
        stats = get_player_stats(player)

        players_stats[player] = {
            stat.task_id: stat for stat in stats if stat.region in selected_regions
        }

    records = []
    main_player_stats = players_stats[players[0]]
    
    selected_columns = parse_columns(columns_str)
    
    # Get task info
    for task_id, task in main_player_stats.items():
        record = {}
                
        if(COL_TASKID in selected_columns):
            record["task_id"] = task_id
                        
        if(COL_REGION in selected_columns):
            record["region"] = task.region
                        
        if(COL_DESCRIPTION in selected_columns):
            record["description"] = task.description
                        
        if(COL_POINTS in selected_columns):
            record["points"] = task.points
                        
        if(COL_COMPLETION_PCT in selected_columns):
            record["completion_pct"] = task.completion_pct

        if(COL_USERNAMES in selected_columns):
            for player in players:
                record[player] = players_stats[player][task_id].player_completed

        records.append(record)

    return pd.DataFrame.from_records(records)

# define typer commands

def tasks(
    regions: Annotated[str, REGIONS_OPTION] = None,
    columns: Annotated[str, COLUMNS_OPTION] = None,
    exclude_global: Annotated[bool, EXCLUDE_GLOBAL_OPTION] = False,
    players: Annotated[list[str], PLAYERS_ARGUMENT] = ...,
):
    """
    List all tasks any of the given players have done
    """
    if len(players) == 0:
        raise ValueError("Must specify at least one player")

    tasks_df = get_tasks_df(regions, columns, exclude_global, players)
    tasks_to_report = tasks_df[tasks_df[players].any(axis=1)]
    print(tabulate(tasks_to_report, headers="keys", showindex=False))


@app.command()
def suggest(
    regions: Annotated[str, REGIONS_OPTION] = None,
    columns: Annotated[str, COLUMNS_OPTION] = None,
    exclude_global: Annotated[bool, EXCLUDE_GLOBAL_OPTION] = False,
    players: Annotated[list[str], PLAYERS_ARGUMENT] = ...,
):
    """
    List all tasks you haven't done and that any of your friends have done. Put yourself first in the list.
    """
    if len(players) < 2:
        raise ValueError("Must specify at least two players")

    tasks_df = get_tasks_df(regions, columns, exclude_global, players)
    main_player = players[0]
    any_tasks_done = tasks_df[tasks_df[players].any(axis=1)]
    tasks_main_hasnt_done = any_tasks_done[~any_tasks_done[main_player]]

    print(tabulate(tasks_main_hasnt_done, headers="keys", showindex=False))


if __name__ == "__main__":
    app()
