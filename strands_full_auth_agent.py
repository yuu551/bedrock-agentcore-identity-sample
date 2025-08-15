import os
from bedrock_agentcore.identity.auth import requires_api_key
from strands import Agent, tool
from strands_tools import calculator
from strands.models.litellm import LiteLLMModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# グローバル変数でAPIキーを管理
AZURE_API_KEY_FROM_CREDS_PROVIDER = ""

# Outbound Auth: APIキー取得用のデコレーター付き関数
@requires_api_key(
    provider_name="azure-openai-key"
)
async def need_api_key(*, api_key: str):
    global AZURE_API_KEY_FROM_CREDS_PROVIDER
    print(f'✅ Credential ProviderからAPIキー取得: {api_key[:10]}...')
    AZURE_API_KEY_FROM_CREDS_PROVIDER = api_key

app = BedrockAgentCoreApp()

# Azure OpenAI設定（環境変数から読み込み）
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_API_BASE", "")
os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv("AZURE_API_VERSION", "2024-02-01")

# カスタムツールの定義（天気情報を返す簡単なツール）
@tool
def weather():
    """現在の天気を取得します"""
    return "晴れ時々くもり、気温は22度です。過ごしやすい天気ですね！"

# グローバルエージェント変数
agent = None

@app.entrypoint
async def full_auth_agent(payload):
    """
    Inbound Auth（Cognito認証）とOutbound Auth（Azure OpenAI）を
    両方使用するエージェント
    """
    global AZURE_API_KEY_FROM_CREDS_PROVIDER, agent
    
    # このエントリーポイントが呼ばれる時点で、
    # すでにCognito認証（Inbound Auth）は通過している
    print("✅ Cognito認証済みリクエストを受信")
    print(f"受信したペイロード: {payload}")
    
    # Outbound Auth: APIキーが未取得の場合は取得
    if not AZURE_API_KEY_FROM_CREDS_PROVIDER:
        print("Outbound Auth: Credential ProviderからAzure APIキーを取得中...")
        try:
            await need_api_key(api_key="")  # デコレーターが自動でキーを注入
            os.environ["AZURE_OPENAI_API_KEY"] = AZURE_API_KEY_FROM_CREDS_PROVIDER
            print("✅ Azure APIキーの設定完了！")
        except Exception as e:
            print(f"❌ APIキー取得エラー: {e}")
            raise
    
    # エージェントの初期化（初回のみ）
    if agent is None:
        print("Azure OpenAIモデルでエージェントを初期化中...")
        deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME", "gpt-4o-mini")
        model = f"azure/{deployment_name}"
        print(f"使用するモデル: {model}")
        litellm_model = LiteLLMModel(
            model_id=model, 
            params={"max_tokens": 4096, "temperature": 0.7}
        )
        
        agent = Agent(
            model=litellm_model,
            tools=[calculator, weather],  # 計算と天気のツールを追加
            system_prompt="あなたは親切なアシスタントです。計算と天気の情報を提供できます。"
        )
        print("✅ エージェント初期化完了！")
    
    user_input = payload.get("prompt", "こんにちは")
    print(f"ユーザー入力: {user_input}")
    
    try:
        # Azure OpenAIを使って応答を生成
        response = agent(user_input)
        result = response.message['content'][0]['text']
        print(f"エージェント応答: {result}")
        return result
    except Exception as e:
        print(f"❌ エージェント処理エラー: {e}")
        return f"エラーが発生しました: {str(e)}"

if __name__ == "__main__":
    app.run()