# NeoDict クイックスタートガイド

## インストール

### 前提条件

- Python 3.9以上
- pip

### インストール手順

```bash
# リポジトリをクローン
git clone https://github.com/cmc-labo/neodict.git
cd neodict

# 依存ライブラリをインストール
pip install -r requirements.txt

# 開発モードでインストール
pip install -e .
```

## 基本的な使い方

### 1. Pythonコードで使用

```python
from neodict import NeoDict

# 辞書を初期化
neodict = NeoDict()

# 単語を追加
neodict.add_word(
    surface="生成AI",
    pos="名詞",
    reading="セイセイエーアイ",
    source="manual"
)

# 単語を検索
results = neodict.search("生成AI")
print(results)

# 統計情報を取得
stats = neodict.get_stats()
print(f"総単語数: {stats['total_words']}")
```

### 2. CLIで使用

```bash
# 単語を追加
neodict add "ChatGPT" --pos 名詞 --reading チャットジーピーティー

# 単語を検索
neodict search "ChatGPT"

# 辞書を更新
neodict update

# 統計情報を表示
neodict stats

# MeCab形式でエクスポート
neodict export --format mecab --output ./mecab_dict
```

### 3. 自動更新の設定

```python
from neodict.updater import DictUpdater, UpdateScheduler

# 手動で更新
updater = DictUpdater()
stats = updater.update()
print(stats)

# 自動更新をスケジュール(毎日3時)
scheduler = UpdateScheduler()
scheduler.schedule_daily(hour=3, minute=0)
scheduler.start(blocking=True)
```

## MeCabとの連携

### 辞書をエクスポート

```bash
# MeCab形式で出力
neodict export --format mecab --output /tmp/neodict_mecab

# MeCabでコンパイル
cd /tmp/neodict_mecab
/usr/lib/mecab/mecab-dict-index \
  -d /usr/lib/x86_64-linux-gnu/mecab/dic/debian \
  -u neodict.dic \
  -f utf-8 \
  -t utf-8 \
  neodict.csv

# MeCabで使用
mecab -u /tmp/neodict_mecab/neodict.dic
```

### Pythonから使用

```python
import MeCab

# ユーザー辞書を指定
tagger = MeCab.Tagger('-u /tmp/neodict_mecab/neodict.dic')

# 形態素解析
text = "ChatGPTで生成AIを使った開発をしています"
result = tagger.parse(text)
print(result)
```

## サンプルコード

サンプルコードは `examples/` ディレクトリにあります:

- `basic_usage.py` - 基本的な使い方
- `auto_update.py` - 自動更新の例

実行方法:

```bash
cd examples
python basic_usage.py
python auto_update.py
```

## よくある質問

### Q: どのくらいの頻度で更新すべきですか?

A: 用途によりますが、一般的には1日1回の更新で十分です。ニュース性の高いアプリケーションでは数時間ごとの更新も検討できます。

### Q: 特定のカテゴリのみを収集できますか?

A: はい、設定ファイル(`config/config.yaml`)でカテゴリを指定できます。

### Q: 手動で単語を追加した場合、自動更新で削除されますか?

A: いいえ、手動追加した単語(`source="manual"`)は自動更新の影響を受けません。

### Q: 既存のNEologd辞書と併用できますか?

A: はい、両方の辞書をMeCabのユーザー辞書として登録することで併用できます。

## トラブルシューティング

### データベースエラーが発生する

データベースファイルが破損している可能性があります:

```bash
# バックアップを取得
cp ~/.neodict/dict.db ~/.neodict/dict.db.backup

# データベースを再初期化
rm ~/.neodict/dict.db
python -c "from neodict import NeoDict; NeoDict()"
```

### クローラーがエラーになる

ネットワークの問題やサイトの構造変更が原因の可能性があります:

```python
# 特定のソースのみを使用
from neodict.updater import DictUpdater

updater = DictUpdater(sources=["wikipedia"])  # ニュースを除外
updater.update()
```

## 次のステップ

- [詳細なドキュメント](./DOCUMENTATION.md) を参照
- [開発に貢献](../CONTRIBUTING.md) する
- [Issue](https://github.com/cmc-labo/neodict/issues) を報告

Happy Coding!
