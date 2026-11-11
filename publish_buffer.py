import os
import requests

def post_to_buffer():
    access_token = os.getenv('BUFFER_ACCESS_TOKEN')
    channel_id = os.getenv('BUFFER_PINTEREST_ID') # Profile ID هو نفسه Channel ID في GraphQL
    
    url = "https://api.bufferapp.com/graphql"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # استعلام GraphQL لإنشاء منشور (Draft) في بافر
    query = """
    mutation draftCreate($channelId: String!, $text: String!) {
        draftCreate(
            channelId: $channelId, 
            text: $text
        ) {
            draft {
                id
                text
            }
        }
    }
    """
    
    # المتغيرات التي سيتم إرسالها (النص يحتوي على الرابط)
    variables = {
        "channelId": channel_id,
        "text": "منشور تلقائي عبر GitHub Actions و Buffer GraphQL API 🚀\nhttps://github.com/yourusername/yourrepo"
    }
    
    payload = {
        "query": query,
        "variables": variables
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200 and "errors" not in response.json():
        print("✅ تم إرسال المنشور إلى طابور بافر بنجاح عبر GraphQL!")
        print(response.json())
    else:
        print("❌ فشل النشر:")
        print(response.text)
        exit(1)

if __name__ == "__main__":
    post_to_buffer()
