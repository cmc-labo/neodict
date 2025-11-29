"""
CLIコマンド定義
"""

import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# パスを追加してインポート
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import NeoDict
from updater import DictUpdater, UpdateScheduler

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """NeoDict - 自動更新型日本語新語辞書"""
    pass


@main.command()
@click.option("--sources", "-s", multiple=True, help="更新元(wikipedia, news)")
@click.option("--full", is_flag=True, help="全更新を実行")
def update(sources, full):
    """辞書を最新の情報で更新"""
    console.print("[bold blue]辞書を更新しています...[/bold blue]")

    source_list = list(sources) if sources else ["wikipedia", "news"]
    updater = DictUpdater(sources=source_list)

    try:
        stats = updater.update(full_update=full)

        console.print("[bold green]✓ 更新が完了しました[/bold green]")
        console.print(f"収集した単語: {stats['collected_words']}")
        console.print(f"ユニーク単語: {stats['unique_words']}")
        console.print(f"追加: {stats['added']}")
        console.print(f"更新: {stats['updated']}")
        console.print(f"所要時間: {stats['duration_seconds']:.2f}秒")

    except Exception as e:
        console.print(f"[bold red]✗ エラー: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.argument("query")
@click.option("--fuzzy", "-f", is_flag=True, help="あいまい検索")
@click.option("--limit", "-l", default=10, help="最大表示数")
def search(query, fuzzy, limit):
    """単語を検索"""
    neodict = NeoDict()
    results = neodict.search(query, fuzzy=fuzzy, limit=limit)

    if not results:
        console.print(f"[yellow]'{query}' は見つかりませんでした[/yellow]")
        return

    table = Table(title=f"検索結果: {query}")
    table.add_column("表層形", style="cyan")
    table.add_column("読み", style="magenta")
    table.add_column("品詞", style="green")
    table.add_column("頻度", style="yellow")
    table.add_column("ソース", style="blue")

    for result in results:
        table.add_row(
            result["surface"],
            result.get("reading") or "-",
            result["pos"],
            str(result["frequency"]),
            result["source"]
        )

    console.print(table)


@main.command()
@click.argument("word")
@click.option("--pos", "-p", default="名詞", help="品詞")
@click.option("--reading", "-r", help="読み")
@click.option("--category", "-c", help="カテゴリ")
def add(word, pos, reading, category):
    """単語を手動で追加"""
    neodict = NeoDict()

    try:
        neodict.add_word(
            surface=word,
            pos=pos,
            reading=reading,
            source="manual",
            category=category
        )
        console.print(f"[bold green]✓ '{word}' を追加しました[/bold green]")

    except Exception as e:
        console.print(f"[bold red]✗ エラー: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.argument("word")
def remove(word):
    """単語を削除"""
    neodict = NeoDict()

    count = neodict.remove_word(word)

    if count > 0:
        console.print(f"[bold green]✓ '{word}' を削除しました[/bold green]")
    else:
        console.print(f"[yellow]'{word}' は見つかりませんでした[/yellow]")


@main.command()
def stats():
    """辞書の統計情報を表示"""
    neodict = NeoDict()
    stats = neodict.get_stats()

    console.print("[bold]辞書統計情報[/bold]")
    console.print(f"総単語数: {stats['total_words']:,}")
    console.print(f"品詞種類数: {stats['unique_pos']}")

    # ソース別統計
    console.print("\n[bold]ソース別[/bold]")
    for source, count in stats['sources'].items():
        console.print(f"  {source}: {count:,}")

    # 品詞別統計
    console.print("\n[bold]品詞別[/bold]")
    for pos, count in list(stats['pos_distribution'].items())[:10]:
        console.print(f"  {pos}: {count:,}")


@main.command()
@click.option("--format", "-f", type=click.Choice(["mecab", "json"]), default="mecab", help="出力形式")
@click.option("--output", "-o", required=True, help="出力先パス")
def export(format, output):
    """辞書をエクスポート"""
    neodict = NeoDict()

    try:
        if format == "mecab":
            neodict.export_mecab(output)
        elif format == "json":
            neodict.export_json(output)

        console.print(f"[bold green]✓ {format}形式で出力しました: {output}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]✗ エラー: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.option("--daily", is_flag=True, help="毎日更新")
@click.option("--hourly", is_flag=True, help="毎時更新")
@click.option("--hour", default=3, help="実行時(0-23)")
@click.option("--minute", default=0, help="実行分(0-59)")
def schedule(daily, hourly, hour, minute):
    """自動更新をスケジュール"""
    scheduler = UpdateScheduler()

    if daily:
        scheduler.schedule_daily(hour=hour, minute=minute)
        console.print(f"[bold green]✓ 毎日 {hour:02d}:{minute:02d} に更新するようスケジュールしました[/bold green]")
    elif hourly:
        scheduler.schedule_hourly(minute=minute)
        console.print(f"[bold green]✓ 毎時 {minute:02d}分 に更新するようスケジュールしました[/bold green]")
    else:
        console.print("[yellow]オプションを指定してください: --daily または --hourly[/yellow]")
        return

    console.print("[bold blue]スケジューラーを起動しています...[/bold blue]")
    console.print("Ctrl+C で停止")

    try:
        scheduler.start(blocking=True)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]スケジューラーを停止しました[/bold yellow]")


if __name__ == "__main__":
    main()
