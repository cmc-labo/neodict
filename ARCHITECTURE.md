# NeoDict アーキテクチャ設計

## システム概要

NeoDictは、ウェブから自動的に新語や固有表現を収集し、形態素解析器用の辞書として提供するシステムです。

## コンポーネント構成

```
┌─────────────────────────────────────────────────┐
│                  CLI / API                      │
│            (ユーザーインターフェース)              │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌──────────┐
│ 辞書管理 │ │クローラー│ │アップデート│
│  Core   │ │ Crawler │ │ Updater  │
└────┬────┘ └────┬────┘ └────┬─────┘
     │           │            │
     └───────────┴────────────┘
                 │
                 ▼
         ┌──────────────┐
         │   Storage    │
         │   (SQLite)   │
         └──────────────┘
```

## モジュール詳細

### 1. Core (コア辞書機能)

**責務**: 辞書データの基本操作

**主要クラス**:

- `NeoDict`: 辞書のメインインターフェース
- `Word`: 単語の基本情報を保持
- `WordEntry`: 辞書エントリー(品詞、頻度等の拡張情報)
- `DictStorage`: SQLiteベースの永続化層

**設計パターン**:

- Repository Pattern (DictStorage)
- Data Transfer Object (Word, WordEntry)

### 2. Crawler (ウェブクローラー)

**責務**: ウェブソースからの新語収集

**主要クラス**:

- `BaseCrawler`: クローラーの抽象基底クラス
- `WikipediaCrawler`: Wikipedia日本語版のクローラー
- `NewsCrawler`: ニュースサイトのクローラー
- `WordExtractor`: テキストから新語を抽出

**設計パターン**:

- Strategy Pattern (各クローラー)
- Template Method Pattern (BaseCrawler)

**拡張性**:

新しいソースを追加する場合は`BaseCrawler`を継承:

```python
class CustomCrawler(BaseCrawler):
    def crawl(self, **kwargs):
        # 実装
        pass
```

### 3. Updater (自動更新システム)

**責務**: 辞書の定期更新とスケジューリング

**主要クラス**:

- `DictUpdater`: 辞書更新ロジック
- `UpdateScheduler`: スケジューリング

**設計パターン**:

- Observer Pattern (スケジューラー)
- Command Pattern (更新ジョブ)

### 4. CLI (コマンドラインインターフェース)

**責務**: ユーザーインターフェース

**主要機能**:

- 辞書の検索・追加・削除
- 更新実行
- エクスポート
- 統計表示

**使用ライブラリ**:

- Click (コマンドライン)
- Rich (表示)

## データフロー

### 更新フロー

```
1. Scheduler
   ↓ トリガー
2. DictUpdater
   ↓ クロール要求
3. Crawler (Wikipedia, News, etc.)
   ↓ テキスト取得
4. WordExtractor
   ↓ 新語抽出
5. DictUpdater
   ↓ 頻度集計・フィルタリング
6. NeoDict / Storage
   ↓ 永続化
7. SQLite Database
```

### 検索フロー

```
1. CLI / API
   ↓ 検索クエリ
2. NeoDict
   ↓ クエリ実行
3. DictStorage
   ↓ SQL実行
4. SQLite Database
   ↓ 結果
5. WordEntry
   ↓ シリアライズ
6. Dict / JSON
   ↓ レスポンス
7. User
```

## データモデル

### ER図

```
┌──────────────────────────────┐
│         words                │
├──────────────────────────────┤
│ id (PK)                      │
│ surface (UNIQUE)             │
│ reading                      │
│ pronunciation                │
│ pos                          │
│ pos_detail1/2/3              │
│ conjugation_type/form        │
│ base_form                    │
│ frequency                    │
│ source                       │
│ category                     │
│ cost                         │
│ left_context_id              │
│ right_context_id             │
│ added_date                   │
│ last_updated                 │
└──────────────────────────────┘

┌──────────────────────────────┐
│       versions               │
├──────────────────────────────┤
│ version_id (PK)              │
│ created_date                 │
│ word_count                   │
│ description                  │
└──────────────────────────────┘
```

### インデックス戦略

```sql
-- 検索用
CREATE INDEX idx_surface ON words(surface);
CREATE INDEX idx_reading ON words(reading);

-- フィルタリング用
CREATE INDEX idx_pos ON words(pos);
CREATE INDEX idx_source ON words(source);

-- ソート用
CREATE INDEX idx_frequency ON words(frequency DESC);
```

## パフォーマンス最適化

### 1. データベース

- SQLiteのWALモード使用
- バッチインサート
- インデックスの最適化

### 2. クローラー

- リクエスト間の適切な遅延
- セッションの再利用
- タイムアウト設定

### 3. 更新

- 差分更新(全更新との選択)
- 頻度フィルタリング
- 並列処理(将来実装)

## セキュリティ

### 1. Webスクレイピング

- robots.txt の遵守
- User-Agent の明示
- レート制限

### 2. データ検証

- 入力サニタイゼーション
- SQL インジェクション対策(パラメータ化クエリ)
- パスインジェクション対策

## エラーハンドリング

### クローラーエラー

```python
try:
    soup = self.fetch(url)
except requests.Timeout:
    logger.error(f"Timeout: {url}")
except requests.HTTPError as e:
    logger.error(f"HTTP Error: {e}")
```

### データベースエラー

```python
try:
    cursor.execute(...)
except sqlite3.IntegrityError:
    # 重複の場合は更新
    return self.update_word(entry)
```

## テスト戦略

### 1. ユニットテスト

- 各モジュールの独立したテスト
- pytest使用
- カバレッジ目標: 80%以上

### 2. 統合テスト

- 辞書全体のワークフロー
- 一時データベース使用

### 3. E2Eテスト

- CLIコマンドの動作確認
- サンプルデータでの検証

## 拡張性

### 新しいソースの追加

```python
from crawler.base import BaseCrawler

class NewSourceCrawler(BaseCrawler):
    def crawl(self, **kwargs):
        # 実装
        pass

# 登録
updater = DictUpdater()
updater.register_crawler('newsource', NewSourceCrawler())
```

### 新しいエクスポート形式

```python
class NeoDict:
    def export_sudachi(self, output_path: str):
        # Sudachi形式でエクスポート
        pass
```

## デプロイメント

### 本番環境での推奨構成

```yaml
# docker-compose.yml
services:
  neodict:
    image: neodict:latest
    volumes:
      - ./data:/data
    environment:
      - NEODICT_DB_PATH=/data/dict.db
      - NEODICT_UPDATE_SCHEDULE="0 3 * * *"
```

### システム要件

- Python 3.9+
- メモリ: 512MB以上
- ディスク: 1GB以上(辞書サイズによる)

## モニタリング

### ログ

```python
# ログレベル
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### メトリクス

- 更新頻度
- 収集語数
- エラー率
- 応答時間

## 今後の拡張

### Phase 2

- [ ] 機械学習による品詞推定
- [ ] トレンド分析機能
- [ ] Webダッシュボード

### Phase 3

- [ ] 分散クローリング
- [ ] リアルタイム更新
- [ ] クラウドデプロイ対応

---

**Version**: 0.1.0
**Last Updated**: 2024-11-28
