"""
NeoDict 基本的な使い方のサンプル
"""

import sys
from pathlib import Path

# パスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core import NeoDict


def main():
    print("=== NeoDict 基本的な使い方 ===\n")

    # 1. 辞書の初期化
    print("1. 辞書を初期化...")
    neodict = NeoDict()

    # 2. 単語を手動で追加
    print("\n2. 単語を追加...")
    words_to_add = [
        ("ChatGPT", "名詞", "チャットジーピーティー"),
        ("生成AI", "名詞", "セイセイエーアイ"),
        ("推し活", "名詞", "オシカツ"),
        ("エモい", "形容詞", "エモイ"),
    ]

    for surface, pos, reading in words_to_add:
        neodict.add_word(
            surface=surface,
            pos=pos,
            reading=reading,
            source="manual",
            category="流行語"
        )
        print(f"  追加: {surface} ({reading})")

    # 3. 単語を検索
    print("\n3. 単語を検索...")
    queries = ["ChatGPT", "生成AI", "推し"]

    for query in queries:
        results = neodict.search(query, fuzzy=False)
        if results:
            print(f"  '{query}' を検索:")
            for result in results:
                print(f"    - {result['surface']} [{result['pos']}] ({result.get('reading', '-')})")
        else:
            print(f"  '{query}' は見つかりませんでした")

    # 4. あいまい検索
    print("\n4. あいまい検索...")
    fuzzy_query = "AI"
    results = neodict.search(fuzzy_query, fuzzy=True, limit=5)
    print(f"  '{fuzzy_query}' であいまい検索:")
    for result in results:
        print(f"    - {result['surface']} [{result['pos']}]")

    # 5. 統計情報
    print("\n5. 辞書の統計情報...")
    stats = neodict.get_stats()
    print(f"  総単語数: {stats['total_words']}")
    print(f"  品詞種類数: {stats['unique_pos']}")

    if stats['sources']:
        print("  ソース別:")
        for source, count in stats['sources'].items():
            print(f"    - {source}: {count}")

    # 6. エクスポート
    print("\n6. 辞書をエクスポート...")
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # JSON形式でエクスポート
    json_path = output_dir / "dict.json"
    neodict.export_json(str(json_path))

    # MeCab形式でエクスポート
    mecab_dir = output_dir / "mecab"
    neodict.export_mecab(str(mecab_dir))

    print("\n=== 完了 ===")


if __name__ == "__main__":
    main()
