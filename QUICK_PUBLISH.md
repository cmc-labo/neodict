# NeoDictを公開する - 最短手順

## 🚀 最も簡単な方法: GitHubから直接インストール

**既に公開済みです!** GitHubにプッシュ済みなので、今すぐ使えます:

```bash
pip install git+https://github.com/cmc-labo/neodict.git
```

これだけで誰でもインストールできます。PyPIへの登録は不要です。

---

## 📦 PyPIに公開する場合 (オプション)

PyPIに公開すると `pip install neodict` だけでインストールできるようになります。

### ステップ1: アカウント作成

1. https://pypi.org/account/register/ でアカウント作成
2. メール認証を完了

### ステップ2: ツールをインストール

```bash
pip install build twine
```

### ステップ3: パッケージをビルド

```bash
cd /home/vagrant/neodict
python -m build
```

### ステップ4: PyPIにアップロード

```bash
python -m twine upload dist/*
```

ユーザー名とパスワードを聞かれます:
- Username: PyPIのユーザー名
- Password: PyPIのパスワード (またはAPIトークン)

### 完了!

公開されたら:
```bash
pip install neodict
```

でインストールできます。

---

## 📋 3つの公開方法まとめ

| 方法 | コマンド | メリット | デメリット |
|-----|---------|---------|----------|
| **GitHub直接** | `pip install git+https://github.com/cmc-labo/neodict.git` | 即座に利用可能、登録不要 | 少し長い |
| **PyPI公開** | `pip install neodict` | シンプル、公式 | 審査・登録が必要 |
| **ローカル** | `pip install -e /path/to/neodict` | 開発用 | 他の人は使えない |

---

## 🎯 推奨フロー

1. **今すぐ使いたい** → GitHubから直接インストール (既に可能)
2. **広く使ってほしい** → PyPIに公開
3. **開発中** → ローカルで `pip install -e .`

---

## 使用例

### GitHubから使う場合

```bash
# インストール
pip install git+https://github.com/cmc-labo/neodict.git

# 使ってみる
python -c "from neodict import NeoDict; print('Success!')"
```

### 他のプロジェクトで使う

requirements.txt に追加:
```txt
neodict @ git+https://github.com/cmc-labo/neodict.git
```

---

詳細は [PYPI_PUBLISH.md](docs/PYPI_PUBLISH.md) を参照してください。
