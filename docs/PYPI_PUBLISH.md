# PyPI 公開ガイド

このドキュメントでは、NeoDictをPyPI (Python Package Index) に公開する手順を説明します。

## 方法1: PyPI への公開 (推奨)

PyPIに公開すると、誰でも`pip install neodict`でインストールできます。

### 準備

#### 1. PyPIアカウントを作成

- 本番環境: https://pypi.org/account/register/
- テスト環境: https://test.pypi.org/account/register/

#### 2. 必要なツールをインストール

```bash
pip install build twine
```

#### 3. APIトークンを取得

PyPIにログイン後、アカウント設定からAPIトークンを生成します。

### ビルドと公開

#### 1. パッケージをビルド

```bash
cd neodict

# ビルド
python -m build

# 以下のファイルが生成されます:
# dist/neodict-0.1.0.tar.gz
# dist/neodict-0.1.0-py3-none-any.whl
```

#### 2. TestPyPIでテスト (推奨)

本番公開前に、TestPyPIで動作確認:

```bash
# TestPyPIにアップロード
python -m twine upload --repository testpypi dist/*

# ユーザー名: __token__
# パスワード: pypi-から始まるトークン

# TestPyPIからインストールして確認
pip install --index-url https://test.pypi.org/simple/ neodict
```

#### 3. 本番PyPIに公開

```bash
# PyPIにアップロード
python -m twine upload dist/*

# 公開完了!
# https://pypi.org/project/neodict/
```

### アップロード後

公開されたら、誰でもインストールできます:

```bash
pip install neodict
```

### 更新版の公開

バージョンを上げて再公開する手順:

```bash
# 1. バージョンを更新
# src/__init__.py と pyproject.toml の version を変更
# 例: "0.1.0" → "0.1.1"

# 2. 古いビルドを削除
rm -rf dist/

# 3. 再ビルド
python -m build

# 4. アップロード
python -m twine upload dist/*
```

## 方法2: GitHub からの直接インストール

PyPIに公開しなくても、GitHubから直接インストール可能です。

### インストール方法

```bash
# 最新版をインストール
pip install git+https://github.com/cmc-labo/neodict.git

# 特定のブランチをインストール
pip install git+https://github.com/cmc-labo/neodict.git@develop

# 特定のタグ/バージョンをインストール
pip install git+https://github.com/cmc-labo/neodict.git@v0.1.0
```

### requirements.txt に記述

```txt
# GitHub から直接インストール
neodict @ git+https://github.com/cmc-labo/neodict.git@main
```

## 方法3: GitHub Releases の利用

GitHubのReleasesページで配布する方法:

### 1. リリースを作成

GitHub上で:
1. "Releases" → "Create a new release"
2. タグを作成 (例: `v0.1.0`)
3. リリースノートを記述
4. ビルドしたファイルを添付

### 2. インストール

```bash
# wheelファイルをダウンロードしてインストール
pip install https://github.com/cmc-labo/neodict/releases/download/v0.1.0/neodict-0.1.0-py3-none-any.whl
```

## CI/CD による自動公開

GitHub Actions を使って、タグをプッシュしたら自動的にPyPIに公開:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

使い方:
```bash
# タグを作成してプッシュ
git tag v0.1.0
git push origin v0.1.0

# 自動的にPyPIに公開されます
```

## ベストプラクティス

### 1. バージョニング

セマンティックバージョニングを使用:
- `0.1.0` - 初期リリース
- `0.1.1` - バグフィックス
- `0.2.0` - 新機能追加
- `1.0.0` - 安定版

### 2. チェンジログ

`CHANGELOG.md` を作成して変更履歴を記録:

```markdown
# Changelog

## [0.1.1] - 2024-12-01
### Fixed
- クローラーのタイムアウト処理を改善

## [0.1.0] - 2024-11-28
### Added
- 初回リリース
```

### 3. テスト

公開前に必ずテスト:

```bash
# ローカルでインストールテスト
pip install -e .

# テストを実行
pytest tests/

# 実際のインストールをテスト
pip install dist/neodict-0.1.0-py3-none-any.whl
```

### 4. ドキュメント

- README.md を充実させる
- 使用例を追加
- APIドキュメントを作成

## トラブルシューティング

### エラー: File already exists

同じバージョンは再アップロードできません。バージョンを上げてください。

### エラー: Invalid credentials

APIトークンを確認してください。ユーザー名は必ず `__token__` です。

### パッケージ名が既に使われている

PyPIで検索して、名前が利用可能か確認:
https://pypi.org/search/?q=neodict

## 参考リンク

- [PyPI公式ガイド](https://packaging.python.org/tutorials/packaging-projects/)
- [Twineドキュメント](https://twine.readthedocs.io/)
- [setuptools](https://setuptools.pypa.io/)

---

**Note**: 最初は TestPyPI でテストしてから、本番PyPIに公開することを推奨します。
