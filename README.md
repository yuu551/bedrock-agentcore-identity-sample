# Amazon Bedrock AgentCore Identity ハンズオン

Amazon Bedrock AgentCore IdentityでCognito認証とAzure OpenAI連携を同時に実現するセキュアなエージェントのサンプル実装です。

## 概要

このプロジェクトは、Amazon Bedrock AgentCore Identityの2つの認証機能を活用するエージェントを実装しています：

- **Inbound Auth（インバウンド認証）**: Amazon Cognitoで認証されたユーザーのみがエージェントにアクセス可能
- **Outbound Auth（アウトバウンド認証）**: エージェントがAzure OpenAI APIに安全にアクセス

## アーキテクチャ

```
[クライアント] --Cognito認証--> [AgentCore Identity] --安全な認証--> [Azure OpenAI]
                                        |
                                   [エージェント]
```

1. **クライアントからの認証付きリクエスト**: Cognitoアクセストークン付きでリクエスト送信
2. **Inbound Auth**: Cognitoトークンを検証し、認証されたリクエストのみ通過
3. **エージェント起動**: 認証を通過したリクエストでエージェントが動作
4. **Outbound Auth**: AWS Secrets Manager経由でAzure OpenAI APIキーを安全に取得
5. **Azure OpenAIアクセス**: 取得したAPIキーでAzure OpenAIにリクエスト

## 前提条件

### 必要な環境

- AWS CLI 2.28.8+
- Python 3.12.6+
- AWSアカウント（us-west-2リージョン使用）
- Azureアカウント（gpt-4o-miniまたは任意のモデルをデプロイ）

### Azure OpenAI側の準備

1. Azure AI Foundryでモデルをデプロイ（例：gpt-4o-mini）
2. 以下の情報を控えておく：
   - デプロイメント名
   - エンドポイントURL
   - APIキー

## セットアップ手順

### 1. Python環境のセットアップ

```bash
# 仮想環境の作成と有効化
python3 -m venv agentcore-env
source agentcore-env/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.sample`をコピーして`.env`ファイルを作成し、適切な値を設定してください：

```bash
cp .env.sample .env
# .envファイルを編集して実際の値を設定
```

### 3. Cognitoユーザープールの作成

```bash
chmod +x setup_cognito.sh
./setup_cognito.sh
```

出力された設定値を`.env`ファイルに転記してください。

### 4. IAMロールの作成

```bash
chmod +x create_iam_role.sh
./create_iam_role.sh
```

出力されたロールARNを`.env`ファイルに設定してください。

### 5. Azure OpenAI APIキーの登録

1. Bedrock AgentCoreコンソールの「Identity」セクションに移動
2. 「Add OAuth Client / API key」をクリック
3. Provider typeで「API Key」を選択
4. Nameに「azure-openai-key」と入力
5. Azure OpenAIのAPIキーを貼り付け
6. 作成後、Provider ARNを控える

### 6. エージェントのデプロイ

```bash
python deploy_agent.py
```

デプロイが完了すると、Agent ARNが表示されます。

## 動作確認

### 1. トークンの取得

```bash
python get_token.py && source .token_env
```

### 2. エージェントの呼び出し

ARNをURLエンコードして以下のようにアクセス：

```bash
curl -X POST "https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/[ENCODED_ARN]/invocations?qualifier=DEFAULT" \
  -H "Authorization: Bearer ${BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "こんにちは、計算機能はありますか？"}'
```

### 3. 認証なしでのアクセス（エラー確認）

```bash
curl -X POST "https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/[ENCODED_ARN]/invocations?qualifier=DEFAULT" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "こんにちは"}'
```

期待される応答：`{"message":"Missing Authentication Token"}`

## ファイル構成

```
├── README.md                     # このファイル
├── .env.sample                   # 環境変数サンプル
├── requirements.txt              # Python依存関係
├── strands_full_auth_agent.py    # メインエージェント実装
├── deploy_agent.py               # デプロイスクリプト
├── get_token.py                  # Cognitoトークン取得
├── setup_cognito.sh              # Cognitoセットアップ
├── create_iam_role.sh            # IAMロール作成
├── trust-policy.json             # IAMトラストポリシー
├── execution-policy.json         # IAM実行ポリシー
└── blog.md                       # 詳細な技術解説
```
## 注意事項

- 本番環境では最小権限の原則に従ってIAM権限を設定してください