#!/bin/bash

# Cognito User Pool作成スクリプト
REGION="us-west-2"

# User Poolの作成
echo "Cognito User Poolを作成中..."
POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name "MyUserPool" \
  --policies '{"PasswordPolicy":{"MinimumLength":8}}' \
  --region $REGION | jq -r '.UserPool.Id')

# App Clientの作成（重要：USER_PASSWORD_AUTHフローを有効化）
echo "App Clientを作成中..."
CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $POOL_ID \
  --client-name "MyClient" \
  --no-generate-secret \
  --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
  --region $REGION | jq -r '.UserPoolClient.ClientId')

# テストユーザーの作成
echo "テストユーザーを作成中..."
aws cognito-idp admin-create-user \
  --user-pool-id $POOL_ID \
  --username "testuser" \
  --temporary-password "TempPass123!" \
  --region $REGION \
  --message-action SUPPRESS > /dev/null

# 恒久パスワードの設定
aws cognito-idp admin-set-user-password \
  --user-pool-id $POOL_ID \
  --username "testuser" \
  --password "Testpass123!" \
  --region $REGION \
  --permanent > /dev/null

# 設定値の出力
echo "===== Cognito設定完了 ====="
echo "Pool ID: $POOL_ID"
echo "Discovery URL: https://cognito-idp.us-west-2.amazonaws.com/$POOL_ID/.well-known/openid-configuration"
echo "Client ID: $CLIENT_ID"
echo "Username: testuser"
echo "Password: Testpass123!"