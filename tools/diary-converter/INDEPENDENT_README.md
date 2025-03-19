# 開発日記変換ツール (Diary Converter)

開発日記をZenn公開用の記事に変換するツールです。Gemini APIを使用して、開発中の会話ログを読みやすい技術記事に変換します。

## 機能

- マークダウン形式の開発日記を読み込み
- Gemini APIを使用して内容を構造化・改善
- Zenn公開用の形式に変換（frontmatter付き）
- 変換結果を指定先に保存

## インストール方法

### リポジトリのクローン

```bash
git clone https://github.com/[username]/diary-converter.git
cd diary-converter
```

### 依存関係のインストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```bash
python diary_converter.py path/to/source/diary.md path/to/destination/article.md
```

### 詳細オプション

```bash
python diary_converter.py path/to/source/diary.md path/to/destination/article.md \
  --model gemini-2.0-flash-001 \
  --debug \
  --template path/to/template.md \
  --cycle-article https://zenn.dev/username/articles/your-article-id
```

#### オプション説明

- `--model` : 使用するGeminiモデル (デフォルト: gemini-2.0-flash-001)
- `--debug` : デバッグモードを有効にする
- `--template` : 使用するテンプレートファイルのパス (デフォルト: Documents/zenn_template.md)
- `--cycle-article` : 開発サイクルの紹介記事へのリンク

### 環境変数の設定

Gemini APIキーを環境変数に設定してください：

```bash
export GOOGLE_API_KEY=your_api_key_here
```

## Docker環境での実行

### イメージのビルド

```bash
docker build -t diary-converter .
```

### コンテナの実行

```bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output \
  -e GOOGLE_API_KEY=your_api_key_here \
  diary-converter input/your-diary.md output/your-article.md
```

### docker-composeでの実行

```bash
docker-compose build diary-converter
docker-compose run diary-converter input/your-diary.md output/your-article.md
```

## CI/CDパイプラインでの使用方法

### GitHubリポジトリからクローンする方法

```yaml
- name: Clone diary-converter repository
  uses: actions/checkout@v3
  with:
    repository: [username]/diary-converter
    path: ./diary-converter
    token: ${{ secrets.DIARY_CONVERTER_TOKEN }}

- name: Run diary-converter
  run: |
    cd diary-converter
    pip install -r requirements.txt
    python diary_converter.py ../path/to/source.md ../path/to/output.md
    cd ..
```

### GitHubリリースからダウンロードする方法

```yaml
- name: Download diary-converter release
  run: |
    mkdir -p ./diary-converter
    curl -L https://github.com/[username]/diary-converter/releases/latest/download/diary-converter.zip -o diary-converter.zip
    unzip diary-converter.zip -d ./diary-converter

- name: Run diary-converter
  run: |
    cd diary-converter
    pip install -r requirements.txt
    python diary_converter.py ../path/to/source.md ../path/to/output.md
    cd ..
```

### GitHub Actionsのコンポーザブルアクション

```yaml
- name: Run diary-converter
  uses: [username]/diary-converter@v1
  with:
    source_file: path/to/source.md
    destination_file: path/to/output.md
    api_key: ${{ secrets.GOOGLE_API_KEY }}
    model: gemini-2.0-flash-001
    template: path/to/template.md
    cycle_article: https://zenn.dev/username/articles/your-article-id
```

## 開発に貢献する

1. このリポジトリをフォークする
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## テスト

テストを実行するには：

```bash
cd tests
./run_test.sh
```

Docker環境でテストするには：

```bash
cd tests
./docker_test.sh
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。 