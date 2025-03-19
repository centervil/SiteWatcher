# 2025-03-20 diary-converter-independence

## 今日の開発テーマ

今日の開発テーマは、diary_converter.py を別の開発プロジェクト（別リポジトリ）からでも使えるようにすることです。

## 前日までの活動履歴

前日までの活動履歴は以下の通りです：
* 2025-03-19: development
* 2025-03-18: zenn-article-format-fix
* 2025-03-17: cicd-pipeline-fix
* 2025-03-16: zenn-template-application
* 2025-03-15: zenn-repo-push-integration
* 2025-03-13: diary-converter-CI-CD組み込み

## 会話ログ

- ユーザー: 今日の開発テーマは、 @diary_converter.py  を別の開発プロジェクトから（つまり別のリポジトリから）でも使えるようにすることです。
具体的には、 @diary-converter フォルダ以下を別リポジトリとして独立させ、このリポジトリまたは別のリポジトリからは、CI/CDパイプライン中にその独立させたリポジトリから @diary_converter.py を取得して、開発日記の変換を行いたいのです。
- LLM: 開発日記ファイルを作成します。diary-converterを独立したリポジトリとして切り出し、CI/CDパイプラインから利用できるようにするための計画を立てました。この計画に基づいて必要な作業を進めていきます。
- ユーザー: 
- LLM: diary-converterを独立リポジトリとして機能させるための主要な変更を実装しました。以下に実装した内容をまとめます：

1. 独立リポジトリ用の新しいREADMEを作成（INDEPENDENT_README.md）
   - 基本的な使用方法、インストール手順の説明
   - CI/CDパイプラインでの使用方法を3つのアプローチで解説
   - 開発貢献やテスト方法なども記載

2. GitHub Actionsのコンポーザブルアクション用の設定ファイル（action.yml）を作成
   - 入力パラメータの定義（ソースファイル、出力先、APIキーなど）
   - Pythonの設定や依存関係のインストール手順
   - テンプレートパスやデバッグモードなどのオプション対応

3. テンプレートファイルのディレクトリ構造を整理
   - `templates/zenn_template.md` としてテンプレートを配置
   - テンプレートの内容をそのまま維持

4. diary_converter.pyの修正
   - デフォルトテンプレートパスを相対パス（`./templates/zenn_template.md`）に変更
   - テンプレート読み込み処理で相対パスを正しく解決するロジックを追加
   - 不要なパス調整コードを削除

5. Docker関連ファイルの整備
   - docker-compose.ymlファイルを作成
   - ボリュームマウントで入力、出力、テンプレートディレクトリを適切に設定

これらの変更により、diary-converterは独立したリポジトリとして機能し、他のプロジェクトからCI/CDパイプラインを通じて利用できるようになりました。特にGitHub Actionsのコンポーザブルアクションを使用することで、最も簡単に連携できます。

- ユーザー: ありがとうございます。想定通りの結果となり良かったです。ところで、GitHub Actionsコンポーザブルアクション設定 とはなんですか？
- LLM: GitHubアクションのコンポーザブルアクション設定は、複数のステップをひとつのパッケージ化されたアクションとして定義できるGitHub Actionsの機能です。

主な特徴：
- 複数のコマンドやジョブを「一つのアクション」として再利用可能
- `action.yml`ファイルに入力パラメータや実行ステップを定義
- 他のプロジェクトから簡単に呼び出して使用できる
- 環境設定やツール実行などの複雑な処理を簡単に共有できる

今回のdiary-converterでは、Pythonのセットアップ、依存関係のインストール、コンバーターの実行など複数のステップを一つのアクションにまとめています。これにより、他のプロジェクトからシンプルに次のように呼び出すだけで実行できます：

```yaml
- name: Run diary-converter
  uses: [username]/diary-converter@v1
  with:
    source_file: Documents/ProjectLogs/latest.md
    destination_file: articles/output.md
    api_key: ${{ secrets.GOOGLE_API_KEY }}
```

このアプローチは、複雑な処理を簡単に再利用可能にし、メンテナンスも容易になります。

- ユーザー: これは、呼び出し元のリポジトリが、この yml が保存されているリポジトリと別でも使えるの？もしそうならどういう仕組み？また、destination_file が、呼び出し元リポジトリとは別リポジトリであっても機能するもの？
- LLM: はい、GitHubアクションのコンポーザブルアクションは呼び出し元リポジトリと別のリポジトリからでも使えます。

仕組みとしては：
1. **参照方法**:
   ```yaml
   uses: [owner]/[repo-name]@[ref]
   ```
   - `owner`: リポジトリ所有者名
   - `repo-name`: リポジトリ名
   - `ref`: タグ（v1など）、ブランチ名、コミットハッシュ

2. **実行方法**:
   - GitHubは指定されたリポジトリの`action.yml`を読み込む
   - アクションのコードを一時的に呼び出し元のワークフロー環境にダウンロード
   - `action.yml`に定義されたステップを実行

3. **入力パラメータ**:
   - `with`キーワードで指定した値がアクションに渡される
   - アクション内部では`${{ inputs.parameter_name }}`で参照可能

`destination_file`は**呼び出し元リポジトリのパス**を参照します：
- アクションは呼び出し元リポジトリのワークスペース（`${{ github.workspace }}`）内で実行される
- 別リポジトリのファイルに直接書き込むことはできない

別リポジトリに出力するには：
1. 呼び出し元で一時ファイルを生成
2. 別のステップで目的のリポジトリをクローン
3. 一時ファイルをコピー
4. 変更をコミット・プッシュ

実装時にはこの点に注意し、別リポジトリへの書き込みには適切なアクセストークンと追加ステップが必要です。

- ユーザー: なるほど、理解しました。今日はGitHubアクションのコンポーザブルアクションについて学べてよかったです。この機能についての説明は、zenn公開用日記にも詳しく載せておきたいので、開発日記に詳細に記載しておいてください

## 計画: diary-converterの独立リポジトリ化

diary-converterを独立したリポジトリとして切り出し、CI/CDパイプラインから利用できるようにするための計画を立てます。

### 1. 独立リポジトリの作成

1. 新しいGitHubリポジトリ「diary-converter」を作成
2. 現在の `tools/diary-converter` フォルダの内容を新リポジトリに移行
3. READMEの更新と必要なドキュメントの追加

### 2. 依存関係の整理

1. `requirements.txt` の検証と更新
2. 環境変数やパスの調整（独立リポジトリとして動作するように）
3. テストスクリプトの確認と更新

### 3. CI/CDパイプラインへの統合方法の実装

1. CI/CDパイプラインからdiary-converterを取得する方法を検討
   - GitリポジトリのクローンによるアプローチNS
   - GitHubリリースからのダウンロードによるアプローチ
   - GitHub Actionsのサブモジュールアクションによるアプローチ
2. 最適な方法を選択して実装

### 4. 実装予定のCI/CD連携方法

以下の方法を実装予定：

#### A. GitリポジトリのクローンによるアプローチNS

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
    python diary_converter.py ../Documents/ProjectLogs/[latest].md ../articles/[output].md
```

#### B. GitHubリリースからのダウンロードによるアプローチ

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
    python diary_converter.py ../Documents/ProjectLogs/[latest].md ../articles/[output].md
```

#### C. GitHub Actionsのコンポーザブルアクションによるアプローチ

```yaml
- name: Run diary-converter
  uses: [username]/diary-converter@v1
  with:
    source_file: Documents/ProjectLogs/[latest].md
    destination_file: articles/[output].md
    api_key: ${{ secrets.GOOGLE_API_KEY }}
```

### 5. テストとデプロイ

1. 新リポジトリの機能テスト
2. 既存プロジェクトとの連携テスト
3. CI/CDパイプラインでの検証
4. ドキュメント作成と配布

## 実装内容

### 1. 独立リポジトリ用のREADME.mdの作成

独立したリポジトリで使用するための新しいREADMEファイルを作成しました。このファイルにはツールの概要、インストール方法、使用方法、CI/CDパイプラインでの利用方法など、詳細な情報を記載しています。

### 2. GitHub Actionsのコンポーザブルアクションの設定

`action.yml`ファイルを作成し、GitHub Actionsのコンポーザブルアクションとして利用できるようにしました。このアクションは以下のような形式で簡単に利用できます：

```yaml
- name: Run diary-converter
  uses: [username]/diary-converter@v1
  with:
    source_file: Documents/ProjectLogs/latest.md
    destination_file: articles/output.md
    api_key: ${{ secrets.GOOGLE_API_KEY }}
```

### 3. テンプレートファイルの調整

テンプレートファイルを`templates`ディレクトリに配置し、独立リポジトリとして機能するように構造を整理しました。

### 4. diary_converter.pyの修正

- デフォルトテンプレートパスを相対パスに変更
- テンプレート読み込み処理を改善し、相対パスを正しく解決できるようにしました
- 独立リポジトリとして機能するために不要な特定のパス調整コードを削除

### 5. Docker関連ファイルの整備

独立リポジトリで使用するためのdocker-compose.ymlファイルを作成し、適切なボリュームマウントと環境変数設定を行いました。

## GitHub Actionsのコンポーザブルアクションについての理解

今回の開発作業を通じて、GitHub Actionsのコンポーザブルアクションについて深く理解することができました。これは今後のCI/CD開発において非常に有用な知識となります。

### コンポーザブルアクションとは

コンポーザブルアクションは、複数のステップをまとめて再利用可能な形にパッケージ化するGitHub Actionsの機能です。通常のワークフロー（`.github/workflows/*.yml`）が単一のリポジトリ内で定義・実行されるのに対し、コンポーザブルアクションは異なるリポジトリ間で共有・再利用できます。

### 主な利点

1. **再利用性**: 同じ処理を複数のリポジトリやワークフローで再利用できる
2. **カプセル化**: 複雑な処理をシンプルなインターフェースで提供できる
3. **メンテナンス性**: 実装の変更を一箇所で行い、利用側は参照を更新するだけでよい
4. **バージョン管理**: タグやリリースを通じてバージョン管理ができる

### コンポーザブルアクションの定義方法

1. **action.yml ファイルの作成**: アクションのメタデータと実行内容を定義

```yaml
name: 'アクション名'
description: 'アクションの説明'
inputs:
  input_name:
    description: '入力の説明'
    required: true/false
    default: 'デフォルト値'
outputs:
  output_name:
    description: '出力の説明'
runs:
  using: 'composite'  # コンポジットアクションの場合
  steps:
    - name: 'ステップ1'
      run: 'コマンド'
      shell: bash
    - name: 'ステップ2'
      run: 'コマンド'
      shell: bash
```

2. **実行方法の指定**: `runs`セクションで以下のいずれかを指定
   - `composite`: シェルコマンドやアクションの組み合わせ
   - `docker`: Dockerコンテナを使用
   - `node16`/`node20`: JavaScriptアクション

### 他のリポジトリからの利用方法

アクションを利用するリポジトリのワークフロー（`.github/workflows/*.yml`）で以下のように参照します：

```yaml
jobs:
  job_name:
    runs-on: ubuntu-latest
    steps:
      - name: 'アクションを使用'
        uses: owner/repo-name@ref  # owner/repo-name@v1 など
        with:
          input_name: 'input value'
```

ここで重要なのは：
- `owner/repo-name`: アクションが定義されているリポジトリ
- `@ref`: ブランチ名、タグ、またはコミットSHA

### 仕組みと動作原理

1. **アクションの取得**:
   - ワークフローの実行時、GitHubはアクションリポジトリを指定された参照（ref）で取得
   - アクションのコードは一時的にワークフロー実行環境にダウンロードされる

2. **パラメータの受け渡し**:
   - `with`で指定した入力値が`inputs`として渡される
   - アクション内では`${{ inputs.input_name }}`で参照できる

3. **実行コンテキスト**:
   - アクションは呼び出し元のワークフローコンテキスト内で実行される
   - `${{ github.workspace }}`は呼び出し元リポジトリのチェックアウトパス

4. **ファイル操作の制約**:
   - アクションは呼び出し元のワークスペース内のファイルにアクセス・操作できる
   - 別リポジトリへの書き込みは追加のチェックアウトやアクセス許可が必要

### コンポーザブルアクションでの別リポジトリとのファイル連携

別リポジトリへの出力ファイル生成など、リポジトリ間のファイル連携をする場合は、以下のパターンが一般的です：

```yaml
jobs:
  job_name:
    runs-on: ubuntu-latest
    steps:
      # ステップ1: メインリポジトリのチェックアウト
      - name: Checkout main repo
        uses: actions/checkout@v3
        
      # ステップ2: コンポーザブルアクションを実行して一時ファイルを生成
      - name: Run diary-converter
        uses: username/diary-converter@v1
        with:
          source_file: path/to/source.md
          destination_file: temp-output.md
          api_key: ${{ secrets.API_KEY }}
          
      # ステップ3: 別リポジトリをチェックアウト
      - name: Checkout target repo
        uses: actions/checkout@v3
        with:
          repository: username/target-repo
          path: target-repo
          token: ${{ secrets.TARGET_REPO_TOKEN }}
          
      # ステップ4: ファイルをコピーして変更をコミット
      - name: Copy and commit file
        run: |
          cp temp-output.md target-repo/path/to/destination.md
          cd target-repo
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add path/to/destination.md
          git commit -m "Update generated file"
          git push
```

### 今回の diary-converter で実装したコンポーザブルアクションの特徴

1. **柔軟な入力パラメータ**:
   - ソースファイル、出力先、APIキー、モデル名などを柔軟に設定可能
   - オプションパラメータにはデフォルト値を設定

2. **環境設定の自動化**:
   - Pythonのセットアップ
   - 依存関係のインストール
   - 出力ディレクトリの準備

3. **パス解決の工夫**:
   - 相対パスと絶対パスの両方に対応
   - スクリプトディレクトリからの相対パスを正しく解決

4. **エラーハンドリング**:
   - 出力ファイルの検証
   - エラー時の適切な終了コード

これらの機能により、diary-converterのコンポーザブルアクションは再利用性が高く、様々なプロジェクトで簡単に利用できるようになっています。 