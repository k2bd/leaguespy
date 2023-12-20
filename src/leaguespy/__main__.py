#imports
import pandas as pd
import typer
from tabulate import tabulate

from leaguespy.player_stats import get_player_stats
from leaguespy.player_task_info import PlayerTaskInfo

app = typer.Typer()
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

REGIONS_OPTION = typer.Option(
    None,
    help="Comma-separated list of regions to include. "
    "Valid values: asgarnia, desert, fremennik, kandarin, morytania, tirannwn, "
    "wilderness, kourend",
)
EXCLUDE_GLOBAL_OPTION = typer.Option(
    False, help="Exclude general and shared-region tasks from the report"
)
PLAYERS_ARGUMENT = typer.Argument(
    ...,
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


def get_tasks_df(
    regions_str: str,
    exclude_global: bool,
    players: list[str],
):
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
    for task_id, task in main_player_stats.items():
        record = {
            "task_id": task_id,
            "region": task.region,
            "description": task.description,
            "points": task.points,
            "completion_pct": task.completion_pct,
        }

        for player in players:
            record[player] = players_stats[player][task_id].player_completed

        records.append(record)

    return pd.DataFrame.from_records(records)

# define typer commands

@app.command()
def tasks(
    regions: str = REGIONS_OPTION,
    exclude_global: bool = EXCLUDE_GLOBAL_OPTION,
    players: list[str] = PLAYERS_ARGUMENT,
):
    if len(players) == 0:
        raise ValueError("Must specify at least one player")

    tasks_df = get_tasks_df(regions, exclude_global, players)
    tasks_to_report = tasks_df[tasks_df[players].any(axis=1)]
    print(tabulate(tasks_to_report, headers="keys", showindex=False))


@app.command()
def suggest(
    regions: str = REGIONS_OPTION,
    exclude_global: bool = EXCLUDE_GLOBAL_OPTION,
    players: list[str] = PLAYERS_ARGUMENT,
):
    if len(players) < 2:
        raise ValueError("Must specify at least two players")

    tasks_df = get_tasks_df(regions, exclude_global, players)
    main_player = players[0]
    any_tasks_done = tasks_df[tasks_df[players].any(axis=1)]
    tasks_main_hasnt_done = any_tasks_done[~any_tasks_done[main_player]]

    print(tabulate(tasks_main_hasnt_done, headers="keys", showindex=False))


if __name__ == "__main__":
    app()
