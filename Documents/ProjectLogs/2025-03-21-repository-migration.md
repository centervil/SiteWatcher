# 2025-03-21 repository-migration

## 今日の開発テーマ

今日の開発テーマは、diary-converterを独立したリポジトリとして移行することです。GitHub Actionsのコンポーザブルアクションとして利用できるように設定を行います。

## 前日までの活動履歴

前日までの活動履歴は以下の通りです：
* 2025-03-20: diary-converter-independence
* 2025-03-19: development
* 2025-03-18: zenn-article-format-fix
* 2025-03-17: cicd-pipeline-fix
* 2025-03-16: zenn-template-application
* 2025-03-15: zenn-repo-push-integration

## 会話ログ

- ユーザー: 今日の開発を始めます。@Auto_Logging_Guide.md を読んで。
昨日の開発履歴は、 @2025-03-20-diary-converter-independence.md です。
今日は、昨日準備をしたリポジトリ移動を開発テーマとします。
準備が出来たら教えて。
- LLM: 開発日記ファイルを作成しました。昨日までの活動履歴を確認し、今日のテーマを「リポジトリ移動」に設定しました。準備ができましたので、リポジトリ移動の作業を進めていきましょう。

- ユーザー: すでにGithubで移動先のリポジトリは作ってあります。
@Diary-Converter にcloneしてあるので、移動を開始してください
- LLM: リポジトリ移動作業を開始します。まず現在の状況を確認し、以下の手順で移行を進めました：

1. ファイルの移動：
   - SiteWatcher/tools/diary-converterの内容を/home/centervil/Diary-Converterにコピー
   - INDEPENDENT_README.mdを正式なREADME.mdとして設定

2. 移行先リポジトリの更新：
   - 全ファイルをステージング
   - 初期コミットを作成
   - GitHubにプッシュ

3. SiteWatcherリポジトリの更新：
   - CI/CDパイプライン（deploy.yml）を修正
   - GitHub Actionsのコンポーザブルアクションを使用するよう変更
   - 元のdiary-converterディレクトリを削除
   - 変更をコミット・プッシュ

- ユーザー: なるほど、理解しました。今日はGitHubアクションのコンポーザブルアクションについて学べてよかったです。この機能についての説明は、zenn公開用日記にも詳しく載せておきたいので、開発日記に詳細に記載しておいてください
- LLM: ## GitHub Actionsのコンポーザブルアクション解説

今回の開発で学んだGitHub Actionsのコンポーザブルアクションについて、以下に詳細を記録します：

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

### diary-converterでの実装例

今回実装したdiary-converterのコンポーザブルアクションは以下のように使用できます：

```yaml
- name: Run diary-converter
  uses: centervil/Diary-Converter@main
  with:
    source_file: path/to/source.md
    destination_file: path/to/output.md
    api_key: ${{ secrets.GOOGLE_API_KEY }}
    model: gemini-2.0-flash-001
    template: path/to/template.md
    debug: 'true'
```

この実装により、diary-converterの機能を他のプロジェクトから簡単に利用できるようになりました。 