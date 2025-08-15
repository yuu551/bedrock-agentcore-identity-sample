#!/usr/bin/env python3
"""
Cognito Bearer Token取得スクリプト（Python版）

従来のget_token.shではサブシェルの問題で環境変数が正しく設定されませんでした。
このPythonスクリプトは.envファイルから設定を読み込み、
トークンを.token_envファイルに保存することで問題を解決します。

使用方法:
    python get_token.py && source .token_env
"""

import os
import boto3
import sys
from dotenv import load_dotenv

def get_cognito_bearer_token():
    """Get Cognito Bearer Token using boto3"""
    try:
        print("🔐 Cognito Bearer Token取得中...")
        
        # 環境変数から設定を取得（USER_POOL_IDは不要！）
        required_vars = ['CLIENT_ID', 'USERNAME', 'PASSWORD']
        missing_vars = [var for var in required_vars if var not in os.environ]
        
        if missing_vars:
            print(f"❌ 必要な環境変数が設定されていません: {', '.join(missing_vars)}")
            print("   .envファイルに以下の設定が必要です:")
            for var in missing_vars:
                print(f"   {var}=your_value_here")
            return None
        
        client_id = os.environ['CLIENT_ID']
        username = os.environ['USERNAME']
        password = os.environ['PASSWORD']
        region = os.environ.get('REGION', 'us-west-2')
        
        # Cognito Identity Providerクライアントを初期化
        cognito_client = boto3.client('cognito-idp', region_name=region)
        
        # ユーザー認証（AWS CLIコマンドと同等）
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        # アクセストークン取得
        access_token = response['AuthenticationResult']['AccessToken']
        print("✅ Cognito Bearer Token取得成功！")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Cognito認証エラー: {e}")
        print("   以下を確認してください：")
        print("   - .envファイルの設定値が正しいか")
        print("   - AWS認証情報が正しく設定されているか")
        print("   - ネットワーク接続が正常か")
        return None

def save_token_to_file(token):
    """Save token to .token_env file for sourcing"""
    try:
        with open('.token_env', 'w') as f:
            f.write(f'export BEARER_TOKEN="{token}"\n')
        print("💾 トークンを.token_envファイルに保存しました")
        print("   次のコマンドで環境変数に設定してください:")
        print("   source .token_env")
        return True
    except Exception as e:
        print(f"❌ ファイル保存エラー: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Cognito Bearer Token取得スクリプト（Python版）")
    print()
    
    # Load .env file using python-dotenv
    print("📋 .envファイルを読み込み中...")
    if not load_dotenv():
        print("❌ .envファイルが見つかりません")
        print("   Cognito認証に必要な設定が.envファイルに記載されていることを確認してください")
        sys.exit(1)
    
    # Get Cognito token
    token = get_cognito_bearer_token()
    if not token:
        sys.exit(1)
    
    # Save token to file
    if not save_token_to_file(token):
        sys.exit(1)
    
    print()
    print("✅ 完了！以下のコマンドで環境変数を設定してください:")
    print("   source .token_env")
    print()
    print("または、ワンライナーで実行:")
    print("   python get_token.py && source .token_env")

if __name__ == "__main__":
    main()