import os
import requests

def create_pin():
    # استدعاء المتغيرات السرية من جيت هاب
    access_token = os.getenv('PINTEREST_ACCESS_TOKEN')
    board_id = os.getenv('PINTEREST_BOARD_ID')
    
    url = "https://api.pinterest.com/v5/pins"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # بيانات المنشور (تأكد من تعديل الروابط لتناسب مشروعك)
    payload = {
        "board_id": board_id,
        "title": "منشور تلقائي من GitHub Actions 🚀",
        "description": "تم النشر برمجياً بنجاح باستخدام Pinterest API.",
        "link": "https://github.com/yourusername/yourrepo", # الرابط الذي سيفتح عند النقر
        "media_source": {
            "source_type": "image_url",
            "url": "https://example.com/your-image.jpg" # رابط الصورة (يجب أن يكون رابطاً مباشراً لصورة)
        }
    }
    
    print("جاري إرسال الطلب إلى بانتريست...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("✅ تم النشر بنجاح!")
        print("رابط المنشور:", f"https://pinterest.com/pin/{response.json().get('id')}")
    else:
        print("❌ فشل النشر:")
        print(f"رمز الخطأ: {response.status_code}")
        print("التفاصيل:", response.text)
        exit(1)

if __name__ == "__main__":
    create_pin()
