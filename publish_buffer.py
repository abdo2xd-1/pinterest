import os
import requests

def post_to_buffer():
    access_token = os.getenv('BUFFER_ACCESS_TOKEN')
    profile_id = os.getenv('BUFFER_PINTEREST_ID')
    
    url = "https://api.bufferapp.com/1/updates/create.json"
    
    payload = {
        "access_token": access_token,
        "profile_ids[]": profile_id,
        "text": "منشور تلقائي عبر GitHub Actions و Buffer API 🚀",
        "media[link]": "https://github.com/yourusername/yourrepo", 
        "media[picture]": "https://example.com/your-image.jpg" 
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        print("✅ تم إرسال المنشور إلى طابور بافر بنجاح!")
        print(response.json())
    else:
        print("❌ فشل النشر:", response.status_code)
        print(response.text)
        exit(1)

if __name__ == "__main__":
    post_to_buffer()
