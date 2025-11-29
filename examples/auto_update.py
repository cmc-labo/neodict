"""
NeoDict 自動更新のサンプル
"""

import sys
from pathlib import Path

# パスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core import NeoDict
from updater import DictUpdater, UpdateScheduler


def manual_update_example():
    """手動更新の例"""
    print("=== 手動更新の例 ===\n")

    # 辞書とアップデーターを初期化
    neodict = NeoDict()
    updater = DictUpdater(dict_instance=neodict)

    # 更新を実行
    print("辞書を更新しています...")
    stats = updater.update()

    print("\n更新結果:")
    print(f"  収集した単語数: {stats['collected_words']}")
    print(f"  ユニーク単語数: {stats['unique_words']}")
    print(f"  追加: {stats['added']}")
    print(f"  更新: {stats['updated']}")
    print(f"  所要時間: {stats['duration_seconds']:.2f}秒")


def scheduled_update_example():
    """スケジュール更新の例"""
    print("\n=== スケジュール更新の例 ===\n")

    # スケジューラーを初期化
    scheduler = UpdateScheduler()

    # 毎日3時に更新をスケジュール
    scheduler.schedule_daily(hour=3, minute=0)
    print("毎日3時に更新するようスケジュールしました")

    # または毎時更新
    # scheduler.schedule_hourly(minute=0)

    # カスタム間隔(例: 30分ごと)
    # scheduler.schedule_custom(interval_minutes=30)

    print("\nスケジューラーを起動します (Ctrl+C で停止)")
    print("※ この例ではデモのため、すぐに停止します\n")

    # 実際に起動する場合:
    # try:
    #     scheduler.start(blocking=True)
    # except KeyboardInterrupt:
    #     scheduler.stop()
    #     print("\nスケジューラーを停止しました")


def source_specific_update():
    """特定のソースから更新"""
    print("=== 特定ソースから更新 ===\n")

    updater = DictUpdater()

    # Wikipediaのみから更新
    print("Wikipediaから更新...")
    count = updater.update_from_source(
        "wikipedia",
        recent_changes=True,
        limit=50
    )
    print(f"  追加: {count}語\n")

    # ニュースのみから更新
    print("ニュースサイトから更新...")
    count = updater.update_from_source(
        "news",
        sources=["nhk"],
        limit=30
    )
    print(f"  追加: {count}語")


if __name__ == "__main__":
    # 手動更新の例を実行
    manual_update_example()

    # 特定ソースから更新
    source_specific_update()

    # スケジュール更新の例(コメント解除して実行)
    # scheduled_update_example()

    print("\n=== 完了 ===")
