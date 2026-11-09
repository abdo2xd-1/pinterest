import os
import requests
import json
import random
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
    
    # استخدام الموديل الأحدث لتوليد المحتوى بناءً على رسالة الخطأ
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt
    )
    
    # تنظيف النص لضمان استخراج صيغة JSON صحيحة
    cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
    content = json.loads(cleaned_text)
    return content['title'], content['description'], content['image_prompt']

def generate_image(image_prompt):
    print("3. جاري تصميم صورة المشروع عبر Hugging Face...")
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    final_prompt = f"{image_prompt}, cyberpunk workbench aesthetic, macro photography of electronic circuit, glowing LEDs, high quality digital 3D render, vertical 2:3 aspect ratio, pinterest aesthetic, NO text, NO watermarks"
    payload = {"inputs": final_prompt}
    
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        image_path = "temp_pin.png"
        with open(image_path, 'wb') as file:
            file.write(response.content)
        print("تم تصميم الصورة وحفظها بنجاح.")
        return image_path
    else:
        print("فشل توليد الصورة:", response.text)
        exit(1)

def post_to_buffer(title, description, image_path, affiliate_url):
    print("4. جاري النشر إلى بنترست عبر Buffer...")
    url = "https://api.bufferapp.com/1/updates/create.json"
    
    payload = {
        "profile_ids[]": BUFFER_PROFILE_ID,
        "text": f"{title}\n\n{description}",
        "media[link]": affiliate_url
    }
    
    with open(image_path, "rb") as f:
        files = {'media[photo]': ('temp_pin.png', f.read(), 'image/png')}
        headers = {"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"}
        response = requests.post(url, headers=headers, data=payload, files=files)
    
    if response.status_code == 200:
        print("✅ تمت جدولة الدبوس بنجاح في Buffer!")
        os.remove(image_path)
    else:
        print("❌ فشل النشر:", response.text)

if __name__ == "__main__":
    try:
        prod_name, aff_link = get_electronic_product()
        title, desc, img_prompt = generate_content(prod_name)
        img_path = generate_image(img_prompt)
        post_to_buffer(title, desc, img_path, aff_link)
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {str(e)}")
