from config_api import get_openai_api_key

try:
    key = get_openai_api_key()
    print("API Key loaded successfully:", key[:6] + "******")
except Exception as e:
    print("Error:", e)
