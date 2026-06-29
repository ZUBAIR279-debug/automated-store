import requests
import base64
import json

# 1. Jo image aap ke paas pehle se folder mein padi hai, uska naam yahan likhein
# (Khatir jama rakhein, hum bas dummy check kar rahe hain)
IMAGE_PATH = 'image_13ea9f.png'  # Ya aap ke folder mein jo bhi image mojud hai

try:
    with open(IMAGE_PATH, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
except FileNotFoundError:
    # Agar woh file nahi milti toh test ke liye aik dummy blank base64 bhej dete hain
    encoded_string = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# 2. Request Data (Yahan hum Order ID 14 bhej rahe hain)
payload = {
    'order_id': 1,  # <--- Aap ka naya Order ID
    'image_base64': encoded_string
}

print("Accountant Agent ko request bheji ja raha hai... Please wait...")

# 3. Request send karna
url = 'http://127.0.0.1:5000/admin/agent/accountant/verify'
try:
    response = requests.post(url, json=payload)
    print("\n=== ACCOUNTANT AGENT KA RESPONSE ===")
    print(json.dumps(response.json(), indent=4))
except Exception as e:
    print(f"Error connecting to server: {e}")