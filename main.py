import os
import requests
import json
import random
import time
import urllib.parse
from google import genai

# 1. استدعاء المفاتيح من إعدادات الأمان في جيت هاب
BUFFER_ACCESS_TOKEN = os.environ.get("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILE_ID = os.environ.get("BUFFER_PROFILE_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

# إعداد واجهة Gemini الجديدة مع تحديد إصدار v1beta
client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1beta'})

def get_electronic_product():
    print("1. جاري اختيار مكون إلكتروني...")
    diy_components = [
        {"name": "Arduino Nano v3.0 Board", "url": "https://aliexpress.com/"},
        {"name": "Digital Soldering Iron Kit", "url": "https://aliexpress.com/"},
        {"name": "Supercapacitors 500F for DIY Spot Welder", "url": "https://aliexpress.com/"},
        {"name": "Bluetooth 5.0 Audio Receiver Board", "url": "https://aliexpress.com/"},
        {"name": "ESP32 WiFi Bluetooth Module", "url": "https://aliexpress.com/"}
    ]
    
    product = random.choice(diy_components)
    print(f"تم اختيار: {product['name']}")
    return product['name'], product['url']

def generate_content(product_name):
    print("2. جاري كتابة فكرة المشروع باستخدام Gemini...")
    prompt = (
        f"تخيل أنك مهندس إلكترونيات وصانع محتوى (DIY). "
        f"اكتب فكرة مشروع إلكتروني مبتكر ومفيد يمكن تنفيذه باستخدام هذه القطعة: '{product_name}'. "
        "أرجع النتيجة بصيغة JSON فقط تحتوي على المفاتيح التالية: "
        "'title' (عنوان جذاب وقصير لفكرة المشروع)، "
        "'description' (شرح مبسط وجذاب لكيفية استخدام القطعة في هذا المشروع مع هاشتاجات قوية مثل #DIY #Electronics #Maker)، "
        "'image_prompt' (وصف تفصيلي بالإنجليزية لصورة 3D لورشة عمل إلكترونيات أو دائرة مضيئة تناسب هذا المشروع لتوليدها بالذكاء الاصطناعي)."
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            
            cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
            content = json.loads(cleaned_text)
            return content['title'], content['description'], content['image_prompt']
            
        except Exception as e:
            print(f"عطل مؤقت في سيرفرات Gemini (المحاولة {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                print("فشلت كل المحاولات للاتصال بـ Gemini. السيرفرات مشغولة جداً.")
                exit(1)
            print("الانتظار 10 ثواني قبل إعادة المحاولة...")
            time.sleep(10)

def generate_image(image_prompt):
    print("3. جاري تصميم صورة المشروع عبر Hugging Face...")
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    final_prompt = f"{image_prompt}, cyberpunk workbench aesthetic, macro photography of electronic circuit, glowing LEDs, high quality digital 3D render, vertical 2:3 aspect ratio, pinterest aesthetic, NO text, NO watermarks"
    payload = {"inputs": final_prompt}
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                image_path = "temp_pin.png"
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                print("تم تصميم الصورة وحفظها بنجاح عبر Hugging Face.")
                return image_path
            else:
                print(f"فشل توليد الصورة من Hugging Face (المحاولة {attempt + 1}):", response.text)
        except requests.exceptions.RequestException as e:
            print(f"عطل في الشبكة مع Hugging Face (المحاولة {attempt + 1}): {str(e)}")
        
        if attempt < max_retries - 1:
            print("الانتظار 15 ثانية قبل إعادة المحاولة...")
            time.sleep(15)
            
    # الخطة البديلة (Fallback) في حالة فشل Hugging Face تماماً
    print("فشلت سيرفرات Hugging Face. جاري استخدام السيرفر البديل (Pollinations AI)...")
    try:
        encoded_prompt = urllib.parse.quote(final_prompt)
        fallback_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1152&nologo=true"
        response = requests.get(fallback_url, timeout=60)
        
        if response.status_code == 200:
            image_path = "temp_pin.png"
            with open(image_path, 'wb') as file:
                file.write(response.content)
            print("تم تصميم الصورة بالسيرفر البديل وحفظها بنجاح.")
            return image_path
        else:
            print("فشل السيرفر البديل أيضاً.")
            exit(1)
    except Exception as e:
        print(f"حدث خطأ في السيرفر البديل: {str(e)}")
        exit(1)

def post_to_buffer(title, description, image_path, affiliate_url):
    print("4. جاري النشر إلى بنترست عبر واجهة Buffer GraphQL الجديدة...")
    
    # واجهة GraphQL تتطلب رابط عام للصورة، سنقوم برفعها مؤقتاً
    print("جاري رفع الصورة للحصول على رابط عام...")
    try:
        with open(image_path, "rb") as f:
            catbox_resp = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f})
        public_image_url = catbox_resp.text.strip()
        print(f"تم الرفع بنجاح: {public_image_url}")
    except Exception as e:
        print("فشل رفع الصورة:", str(e))
        exit(1)

    url = "https://api.buffer.com"
    full_text = f"{title}\n\n{description}\n\nرابط المشروع والمكونات: {affiliate_url}"
    
    query = """
    mutation CreatePost($channelId: String!, $text: String!, $imageUrl: String!) {
      createPost(
        input: {
          channelId: $channelId
          text: $text
          schedulingType: automatic
          mode: addToQueue
          assets: [
            {
              image: {
                url: $imageUrl
              }
            }
          ]
        }
      ) {
        ... on PostActionSuccess {
          post {
            id
          }
        }
        ... on MutationError {
          message
        }
      }
    }
    """
    
    payload = {
        "query": query,
        "variables": {
            "channelId": BUFFER_PROFILE_ID,
            "text": full_text,
            "imageUrl": public_image_url
        }
    }
    
    headers = {
        "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        # التحقق من نجاح عملية GraphQL
        if "data" in data and data["data"].get("createPost", {}).get("post"):
            print("✅ تمت جدولة الدبوس بنجاح في Buffer!")
            os.remove(image_path)
        else:
            print("❌ فشل النشر من داخل Buffer:", json.dumps(data, ensure_ascii=False))
            exit(1)
    else:
        print("❌ فشل الاتصال بواجهة Buffer:", response.text)
        exit(1)

if __name__ == "__main__":
    try:
        prod_name, aff_link = get_electronic_product()
        title, desc, img_prompt = generate_content(prod_name)
        img_path = generate_image(img_prompt)
        post_to_buffer(title, desc, img_path, aff_link)
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {str(e)}")
