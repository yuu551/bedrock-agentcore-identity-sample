#!/bin/bash

# アカウントIDとリージョンを取得
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-west-2"
AGENT_NAME="strands_full_auth_agent_test"

# JSONファイルのプレースホルダーを置換
sed -i.bak "s/123456789012/$ACCOUNT_ID/g" trust-policy.json
sed -i.bak "s/123456789012/$ACCOUNT_ID/g" execution-policy.json

# IAMロールの作成
ROLE_NAME="AgentCoreExecutionRole-$(date +%s)"

aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json

# ポリシーの作成とアタッチ
aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name AgentCoreExecutionPolicy \
    --policy-document file://execution-policy.json

# ロールARNを取得
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "✅ IAM Role created: $ROLE_ARN"
export ROLE_ARN

# 環境変数をファイルに保存
echo "export ROLE_ARN=\"$ROLE_ARN\"" > role_vars.sh
echo "IAM Role ARN has been saved to role_vars.sh"