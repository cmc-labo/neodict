# NeoDict - 自動更新型日本語新語辞書ライブラリ

**最新のウェブから新語・固有表現を自動収集する次世代日本語辞書**

NEologdの後継として、ウェブ上の最新情報から新語や固有表現を自動的に収集・更新する日本語辞書ライブラリです。

## 特徴

### 🚀 自動更新システム
- **定期的なウェブクロール**: Wikipedia、ニュースサイト、SNSトレンドから最新の語彙を収集
- **差分更新機能**: 効率的な増分更新で辞書を常に最新の状態に保持
- **スケジューラー内蔵**: cron不要で自動更新をスケジュール

### 📚 豊富な語彙データ
- **新語**: 最新のIT用語、流行語、ネットスラング
- **固有表現**: 人名、地名、組織名、商品名、イベント名
- **複合語**: 自動的に検出された複合表現
- **トレンド語**: SNSやニュースでのトレンドを反映

### 🔧 形態素解析器との連携
- MeCab対応(ipadic、unidic形式)
- Sudachi対応
- Janome対応
- カスタム辞書フォーマット対応

### 🎯 高精度な品詞推定
- 機械学習による品詞自動推定
- 文脈を考慮した分類
- 手動修正機能

## アーキテクチャ

```
┌─────────────────────────────────────────┐
│    データソース                            │
│  Wikipedia / ニュース / SNS / Web         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    クローラーモジュール                      │
│  - URL収集                                │
│  - コンテンツ抽出                           │
│  - 新語検出                                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    辞書ビルダー                            │
│  - 品詞推定                                │
│  - 頻度計算                                │
│  - 重複除去                                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    辞書データベース                         │
│  - SQLiteストレージ                        │
│  - バージョン管理                           │
│  - 形態素解析器用エクスポート                 │
└─────────────────────────────────────────┘
```

## インストール

### 前提条件

```bash
# Python 3.9以上
python --version

# 依存ライブラリ
pip install -r requirements.txt
```

### PyPIからインストール

```bash
pip install neodict
```

### ソースからインストール

```bash
git clone https://github.com/cmc-labo/neodict.git
cd neodict
pip install -e .
```

## クイックスタート

### 1. 辞書の初期化

```python
from neodict import NeoDict

# 辞書の初期化(初回は自動ダウンロード)
neodict = NeoDict()

# 語彙を検索
result = neodict.search("生成AI")
print(result)
# Output: {'word': '生成AI', 'pos': '名詞', 'reading': 'セイセイエーアイ', 'frequency': 1250}
```

### 2. 辞書の更新

```python
from neodict.updater import DictUpdater

# 自動更新
updater = DictUpdater()
updater.update()  # 最新の語彙を収集して辞書を更新

# スケジュール設定(毎日3時に更新)
updater.schedule(hour=3, minute=0)
```

### 3. MeCabで使用

```bash
# MeCab用辞書として出力
neodict export --format mecab --output /usr/local/lib/mecab/dic/neodict

# MeCabで使用
mecab -d /usr/local/lib/mecab/dic/neodict
```

### 4. CLI使用例

```bash
# 辞書を更新
neodict update

# 語彙を検索
neodict search "ChatGPT"

# 統計情報を表示
neodict stats

# 辞書をエクスポート
neodict export --format mecab --output ./mecab_dict
```

## 主要機能

### 辞書管理

```python
from neodict import NeoDict

dict = NeoDict()

# 語彙を追加
dict.add_word("新語", pos="名詞", reading="シンゴ", source="manual")

# 語彙を検索
words = dict.search("新語", fuzzy=True)

# 語彙を削除
dict.remove_word("古い語")

# 辞書の統計
stats = dict.get_stats()
print(f"総語彙数: {stats['total_words']}")
```

### 自動クロール

```python
from neodict.crawler import WebCrawler

crawler = WebCrawler()

# Wikipediaから新語を収集
crawler.crawl_wikipedia(categories=["IT", "エンターテインメント"])

# ニュースサイトから収集
crawler.crawl_news(sources=["yahoo", "nhk", "asahi"])

# Twitterトレンドから収集
crawler.crawl_trends(platform="twitter", limit=100)
```

### カスタマイズ

```python
from neodict import NeoDict
from neodict.config import Config

# カスタム設定
config = Config(
    update_interval_hours=24,
    min_frequency=5,
    sources=["wikipedia", "news", "twitter"],
    excluded_categories=["アダルト", "ギャンブル"]
)

dict = NeoDict(config=config)
```

## データソース

### 標準ソース
- **Wikipedia日本語版**: 最新の記事タイトルと本文から固有名詞を抽出
- **ニュースサイト**: Yahoo!ニュース、NHK、朝日新聞などから時事用語を収集
- **SNSトレンド**: Twitter/X、はてなブックマークのトレンドワード

### カスタムソース追加

```python
from neodict.crawler import CustomSource

# カスタムソースを定義
class MyCustomSource(CustomSource):
    def fetch(self):
        # スクレイピングロジック
        return extracted_words

# ソースを登録
crawler.register_source(MyCustomSource())
```

## 設定ファイル

`~/.neodict/config.yaml`:

```yaml
# 更新設定
update:
  interval_hours: 24
  auto_update: true
  schedule: "0 3 * * *"  # cron形式

# データソース
sources:
  wikipedia:
    enabled: true
    categories: ["全般"]
  news:
    enabled: true
    sites: ["yahoo", "nhk"]
  twitter:
    enabled: false  # API キー必要

# フィルタリング
filter:
  min_frequency: 3
  min_length: 2
  max_length: 20
  exclude_patterns:
    - "^[0-9]+$"
    - "^[a-zA-Z]+$"

# ストレージ
storage:
  database: "~/.neodict/dict.db"
  backup_enabled: true
  backup_keep_days: 30
```

## プロジェクト構造

```
neodict/
├── src/
│   ├── core/              # コア辞書機能
│   │   ├── dictionary.py  # 辞書クラス
│   │   ├── word.py        # 語彙データモデル
│   │   └── storage.py     # データベース管理
│   ├── crawler/           # ウェブクローラー
│   │   ├── wikipedia.py   # Wikipedia クローラー
│   │   ├── news.py        # ニュースクローラー
│   │   ├── social.py      # SNS クローラー
│   │   └── extractor.py   # 新語抽出器
│   ├── updater/           # 自動更新システム
│   │   ├── scheduler.py   # スケジューラー
│   │   ├── differ.py      # 差分検出
│   │   └── merger.py      # 辞書マージ
│   └── cli/               # CLI ツール
│       └── commands.py
├── tests/                 # テストコード
├── data/                  # 辞書データ
├── config/                # 設定ファイル
├── docs/                  # ドキュメント
├── examples/              # サンプルコード
├── requirements.txt
├── setup.py
└── README.md
```

## 出力形式

### MeCab形式

```csv
表層形,左文脈ID,右文脈ID,コスト,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音
ChatGPT,1285,1285,6000,名詞,固有名詞,一般,*,*,*,ChatGPT,チャットジーピーティー,チャットジーピーティー
```

### JSON形式

```json
{
  "words": [
    {
      "surface": "生成AI",
      "pos": "名詞",
      "pos_detail": ["一般"],
      "reading": "セイセイエーアイ",
      "pronunciation": "セイセイエーアイ",
      "frequency": 1250,
      "source": "wikipedia",
      "added_date": "2024-01-15",
      "category": "IT"
    }
  ]
}
```

## ベンチマーク

| 辞書サイズ | 検索速度 | 更新時間 | メモリ使用量 |
|-----------|---------|---------|------------|
| 10万語 | 0.5ms | 5分 | 50MB |
| 50万語 | 1.2ms | 20分 | 200MB |
| 100万語 | 2.5ms | 45分 | 400MB |

## ライセンス

MIT License - 詳細は `LICENSE` ファイルを参照

## 貢献

バグレポート、機能リクエスト、プルリクエストを歓迎します!

## 参考資料

- [mecab-ipadic-NEologd](https://github.com/neologd/mecab-ipadic-neologd)
- [MeCab公式ドキュメント](https://taku910.github.io/mecab/)
- [Sudachi](https://github.com/WorksApplications/Sudachi)

---

**最新の日本語で、より良い自然言語処理を!**
