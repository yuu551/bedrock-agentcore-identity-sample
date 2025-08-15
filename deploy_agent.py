from bedrock_agentcore_starter_toolkit import Runtime
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

def prepare_environment_variables():
    """Prepare all environment variables for the agent"""
    print("⚙️  環境変数を準備中...")
    
    # Prepare environment variables for the agent container
    env_vars = {
        # Azure OpenAI settings
        "AZURE_API_BASE": os.environ.get('AZURE_API_BASE', ''),
        "AZURE_API_VERSION": os.environ.get('AZURE_API_VERSION', '2025-01-01-preview'),
        "AZURE_DEPLOYMENT_NAME": os.environ.get('AZURE_DEPLOYMENT_NAME', 'gpt-4o-mini'),
    }
    
    # Filter out empty values
    env_vars = {k: v for k, v in env_vars.items() if v}
    
    print(f"✅ 環境変数準備完了: {list(env_vars.keys())}")
    return env_vars

def deploy_agent():
    """Deploy agent with integrated environment variable management"""
    print("🚀 統合デプロイスクリプトを開始...")
    
    # Load .env file using python-dotenv
    print("📋 .envファイルを読み込み中...")
    if not load_dotenv():
        print("❌ .envファイルが見つかりません")
        return
    
    # Get required environment variables
    try:
        discovery_url = os.environ['DISCOVERY_URL']
        client_id = os.environ['CLIENT_ID']
        role_arn = os.environ['ROLE_ARN']
    except KeyError as e:
        print(f"❌ 必要な環境変数が設定されていません: {e}")
        return
    
    # Prepare environment variables for agent container
    env_vars = prepare_environment_variables()
    
    print("🔧 AgentCore Runtimeの設定中...")
    
    # AgentCore Runtimeの設定
    agentcore_runtime = Runtime()
    
    response = agentcore_runtime.configure(
        entrypoint="strands_full_auth_agent.py",
        execution_role=role_arn,
        auto_create_ecr=True,  # ECRリポジトリを自動作成
        requirements_file="requirements.txt",
        region="us-west-2",
        # エージェント名にハイフンは使えない！アンダースコアを使う
        agent_name="strands_full_auth_agent_test",
        # Inbound Auth: Cognito認証の設定
        authorizer_configuration={
            "customJWTAuthorizer": {
                "discoveryUrl": discovery_url,
                "allowedClients": [client_id]
            }
        }
    )
    
    print("✅ 設定完了！デプロイ中...")
    
    # デプロイ実行（環境変数を注入）
    launch_result = agentcore_runtime.launch(env_vars=env_vars)
    
    print(f"✅ デプロイ完了！")
    print(f"   Agent ARN: {launch_result.agent_arn}")
    
    return agentcore_runtime

if __name__ == "__main__":
    deploy_agent()