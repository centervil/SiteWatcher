---
title: "VSCode拡張機能Clineの設定最適化とLLMモデル選択ガイド"
emoji: "⚙️"
type: "tech"
topics: ["vscode", "cline", "llm", "ai", "開発効率化"]
published: true
---

# VSCode拡張機能Clineの設定最適化とLLMモデル選択ガイド

## はじめに

VSCode拡張機能の「Cline」は、AIを活用したコーディング支援ツールとして注目を集めています。しかし、最適な設定や適切なLLMモデルの選択は、その効果を最大限に引き出すために重要です。本記事では、Clineの設定最適化と無料で利用可能なLLMモデルの選択について解説します。

## Clineとは

Clineは、VSCode上でAIを活用したコーディング支援を行う拡張機能です。ファイルの作成・編集、コマンドの実行、ブラウザの操作など、様々な機能を提供します。ユーザーの許可を得ながら、段階的に開発を支援してくれる強力なツールです。

## 利用可能なLLMモデル比較

Cline拡張機能では、以下のLLMモデルが利用可能です：

### 1. Anthropic Claude 3.5-Sonnet
- **特徴**: コーディングに最適と推奨されています
- **制限**: 有料です
- **推奨度**: ★★★★★（コーディングタスクに最適）

### 2. DeepSeek Chat
- **特徴**: コスト効率の良い代替手段として紹介されています
- **制限**: 大規模プロジェクトには不向き
- **推奨度**: ★★★☆☆（中小規模プロジェクトに適している）

### 3. Google Gemini 2.0 Flash
- **特徴**: 無料で利用可能
- **制限**: レート制限に頻繁に達する可能性があります
- **推奨度**: ★★☆☆☆（無料で試すには良いが、本格利用には制限あり）

## DeepSeekモデルの注意点

DeepSeekモデルを使用する際には、以下の点に注意が必要です：

- DeepSeek-r1はAPIエラーが頻発する問題があります
- DeepSeek-r1-zeroは開発テーマを勝手に決めるなど使用感が良くない場合があります
- 大規模プロジェクトではDeepSeek + Clineの組み合わせは推奨されていません
- 大量のコードコンテキストを持つプロジェクトではAPIリクエスト処理が著しく遅くなる可能性があります

## Clineの設定最適化

### Auto Approve機能の無効化

DeepSeekを使用する場合、リソース消費を減らし、複数の同時リクエストによるラグのリスクを最小限に抑えるため、Auto Approve機能を無効化することをお勧めします。

```json
{
  "cline": {
    "autoApprove": false
  }
}
```

### 修正版Clineの使用

Roo-ClineやALineなどの修正版は、比較的短いコンテキストを持ち、リクエストをよりスムーズに処理し、キャッシュヒット率が高いため、APIコール費用の節約に役立ちます。

### カスタム指示の設定

VSCodeのCline拡張機能設定で「Custom Instructions」フィールドを使用して、コーディング標準、品質要件、エラー処理の設定などを指定できます。

```json
{
  "cline": {
    "customInstructions": {
      "language": "日本語",
      "codingStandards": {
        "indentation": "2 spaces",
        "maxLineLength": 120,
        "quotes": "single",
        "semicolons": true
      },
      "documentation": {
        "language": "日本語",
        "requireJSDoc": true,
        "requireFileHeader": true
      },
      "errorHandling": {
        "requireTryCatch": true,
        "requireErrorLogging": true
      }
    }
  }
}
```

### .clinerules ファイルの使用

プロジェクトのルートディレクトリに.clinerules ファイルを作成し、プロジェクト固有のガイドラインを追加することで、Clineの動作をカスタマイズできます。

以下は、.clinerules/config.jsonの例です：

```json
{
  "general": {
    "indentStyle": "space",
    "indentSize": 2,
    "tabWidth": 2,
    "lineEnding": "LF",
    "encoding": "UTF-8",
    "maxLineLength": 120
  },
  "frontend": {
    "language": ["JavaScript", "HTML", "CSS"],
    "framework": "None (VanillaJS)",
    "packageManager": "npm",
    "lintingTool": "ESLint",
    "formattingTool": "Prettier"
  },
  "backend": {
    "language": "JavaScript (Node.js)",
    "runtime": "AWS Lambda",
    "packageManager": "npm",
    "iac": "AWS CloudFormation (or SAM)"
  },
  "docker": {
    "composeVersion": "3.8",
    "baseImage": "node:18",
    "dockerfileLintingTool": "hadolint"
  },
  "git": {
    "branchNamingConvention": "feature/issue-{id}-{short-description}",
    "commitMessageConvention": "type(scope): description",
    "ignoreFiles": [
      "node_modules/",
      ".env",
      ".vscode/"
    ]
  },
  "cicd": {
    "ci": "GitHub Actions",
    "testFramework": "Jest",
    "codeCoverageTool": "nyc",
    "buildAutomationTool": "npm scripts"
  },
  "cline": {
    "autoApprove": false,
    "customInstructions": {
      "language": "日本語",
      "codingStandards": {
        "indentation": "2 spaces",
        "maxLineLength": 120,
        "quotes": "single",
        "semicolons": true
      },
      "documentation": {
        "language": "日本語",
        "requireJSDoc": true,
        "requireFileHeader": true
      },
      "errorHandling": {
        "requireTryCatch": true,
        "requireErrorLogging": true
      }
    }
  }
}
```

## 課題と解決策

### 課題1: 無料で利用可能なLLMモデルの選択
- **問題点**: DeepSeek-r1はAPIエラーが頻発し、DeepSeek-r1-zeroは開発テーマを勝手に決めるなど使用感が良くない
- **解決策**: 
  1. Google Gemini 2.0 Flashは無料だが、レート制限に頻繁に達する可能性がある
  2. Claude 3.5-Sonnetはコーディングに最適だが有料
  3. DeepSeekはコスト効率が良いが、大規模プロジェクトには不向き

### 課題2: Cline拡張機能の設定最適化
- **問題点**: デフォルト設定では最適なパフォーマンスが得られない場合がある
- **解決策**:
  1. Auto Approve機能を無効化してリソース消費を抑制
  2. カスタム指示を設定して特定のコーディング標準を適用
  3. .clinerules ファイルを使用してプロジェクト固有のガイドラインを設定

## まとめ

Cline拡張機能の設定最適化と無料利用可能なLLMモデルの選択について調査しました。無料モデルとしてはGoogle Gemini 2.0 Flashが利用可能ですが、レート制限の問題があります。DeepSeekモデルはコスト効率が良いものの、大規模プロジェクトには不向きです。

最適なパフォーマンスを得るためには、Auto Approve機能の無効化、カスタム指示の設定、.clinerules ファイルの使用などの設定最適化が重要です。今後は選択したLLMモデルの実際のパフォーマンス評価と、Clineの設定のさらなる最適化を進めていく必要があります。

Clineを活用して、より効率的な開発環境を構築しましょう！ 