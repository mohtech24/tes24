import os
import json
import requests
from flask import Flask, request

# Initialize the Flask application
app = Flask(__name__)

# --- Environment Variables (Secrets) ---
# These variables MUST be set in your hosting environment (Replit Secrets or Netlify Environment Variables).
# VERIFY_TOKEN: A secret string you choose for webhook verification (e.g., "YOUR_VERIFY_TOKEN_HERE").
# PAGE_ACCESS_TOKEN: The Page Access Token obtained from Facebook for Developers (starts with "EA...").
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')

# --- Public Mobily USSD Codes Database (Enhanced) ---
# This dictionary stores common Mobily USSD codes and their descriptions.
# You can easily add, modify, or remove entries here.
# Keywords are in lowercase for easier matching.
MOBILY_CODES = {
    "رصيد": {
        "text": "لمعرفة رصيدك، اتصل بالرمز: *222#",
        "code": "*222#"
    },
    "معرفة الرقم": {
        "text": "لمعرفة رقم هاتفك، اتصل بالرمز: *101#",
        "code": "*101#"
    },
    "تعبئة الرصيد": {
        "text": "لتعبئة رصيدك، اتصل بالرمز: *111*رمز_التعبئة#",
        "code": "*111*CODE#"
    },
    "خدمة العملاء": {
        "text": "للتحدث مع خدمة العملاء، اتصل على: 700",
        "code": "700"
    },
    "كلمني": {
        "text": "لتفعيل خدمة كلمني (اتصل بي)، اتصل بالرمز: *606*رقم_المستقبل#",
        "code": "*606*NUMBER#"
    },
    "تحويل رصيد": {
        "text": "لتحويل الرصيد، اتصل بالرمز: *610*رقم_المستقبل*المبلغ*الرقم_السري# (الرقم السري الافتراضي غالباً 0000)",
        "code": "*610*NUMBER*AMOUNT*PIN#"
    },
    "باقات انترنت": {
        "text": "لاستكشاف باقات الإنترنت، يمكنك الاتصال بالرمز *600# أو زيارة موقع موبيليس الرسمي للحصول على تفاصيل أكثر.",
        "code": "*600#"
    },
    "عروض": {
        "text": "لاستكشاف العروض المتاحة (إنترنت، مكالمات، رسائل)، اتصل بالرمز *600# أو قم بزيارة تطبيق MobiSpace.",
        "code": "*600#"
    },
    "الخضرة": {
        "text": "لمعرفة باقات وعروض الخضرة، اتصل بالرمز: *223#",
        "code": "*223#"
    },
    "مكالمات فائتة": {
        "text": "لتفعيل خدمة المكالمات الفائتة (644)، اتصل بالرمز: **62*644#",
        "code": "**62*644#"
    },
    "إلغاء مكالمات فائتة": {
        "text": "لإلغاء خدمة المكالمات الفائتة (644)، اتصل بالرمز: ##62#",
        "code": "##62#"
    },
    "خدمات موبيليس": {
        "text": "للوصول إلى قائمة خدمات موبيليس الرئيسية، اتصل بالرمز: *1100#",
        "code": "*1100#"
    },
    "فوائد الباقة": {
        "text": "لمعرفة فوائد باقتك الحالية، اتصل بالرمز: *1411#",
        "code": "*1411#"
    },
    "سلفني": {
        "text": "لطلب سلفة رصيد (خدمة سلفني)، اتصل بالرمز: *600# ثم اختر الخيار المناسب.",
        "code": "*600#"
    },
    "تفعيل 4G": {
        "text": "لتفعيل خدمة 4G، يرجى زيارة أقرب وكالة موبيليس أو الاتصال بخدمة العملاء 700.",
        "code": "N/A" # No direct USSD code for activation, usually via agency or customer service
    },
    "تجديد الباقة": {
        "text": "لتجديد باقتك، يمكنك استخدام الرمز الخاص بالباقة أو زيارة تطبيق MobiSpace.",
        "code": "N/A"
    }
}

# --- Function to Send Messages to Messenger ---
def send_message(recipient_id, message_text):
    """
    Sends a text message back to the Messenger recipient using the Facebook Graph API.
    """
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    }
    try:
        # Using v19.0 of the Graph API. Ensure this version is current or update as needed.
        response = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Message sent to {recipient_id}. Status: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to {recipient_id}: {e}")
        # In a real application, you might log this error or notify an administrator

# --- Function to Process User Messages ---
def process_user_message(message_text):
    """
    Processes the user's incoming message and returns a relevant Mobily USSD code or a default response.
    This function performs simple keyword matching. For more advanced bots, consider NLU.
    """
    message_text_lower = message_text.lower().strip()

    # Check for direct matches or strong keyword presence
    for keyword, details in MOBILY_CODES.items():
        if keyword in message_text_lower:
            return details["text"]

    # More flexible keyword matching for common queries
    if "رصيد" in message_text_lower or "كم بقي" in message_text_lower or "الرصيد" in message_text_lower or "حسابي" in message_text_lower:
        return MOBILY_CODES["رصيد"]["text"]
    elif "رقم" in message_text_lower and ("هاتفي" in message_text_lower or "خاص بي" in message_text_lower or "معرفة" in message_text_lower):
        return MOBILY_CODES["معرفة الرقم"]["text"]
    elif "تعبئة" in message_text_lower or "شحن" in message_text_lower or "كارت" in message_text_lower or "فليكسي" in message_text_lower:
        return MOBILY_CODES["تعبئة الرصيد"]["text"]
    elif "خدمة عملاء" in message_text_lower or "مساعدة" in message_text_lower or "تواصل" in message_text_lower or "مشكلة" in message_text_lower:
        return MOBILY_CODES["خدمة العملاء"]["text"]
    elif "كلمني" in message_text_lower or "اتصل بي" in message_text_lower or "رنلي" in message_text_lower:
        return MOBILY_CODES["كلمني"]["text"]
    elif "تحويل" in message_text_lower and "رصيد" in message_text_lower:
        return MOBILY_CODES["تحويل رصيد"]["text"]
    elif "باقات" in message_text_lower or "انترنت" in message_text_lower or "عروض" in message_text_lower or "اشتراك" in message_text_lower or "جيجا" in message_text_lower:
        return MOBILY_CODES["باقات انترنت"]["text"]
    elif "الخضرة" in message_text_lower:
        return MOBILY_CODES["الخضرة"]["text"]
    elif "مكالمات فائتة" in message_text_lower or "من اتصل" in message_text_lower or "تنبيه" in message_text_lower or "غياب" in message_text_lower:
        return MOBILY_CODES["مكالمات فائتة"]["text"]
    elif "إلغاء مكالمات فائتة" in message_text_lower or "إيقاف 644" in message_text_lower or "الغاء" in message_text_lower:
        return MOBILY_CODES["إلغاء مكالمات فائتة"]["text"]
    elif "خدمات" in message_text_lower or "قائمة" in message_text_lower or "خيارات" in message_text_lower:
        return MOBILY_CODES["خدمات موبيليس"]["text"]
    elif "فوائد" in message_text_lower or "باقة" in message_text_lower and "معلومات" in message_text_lower:
        return MOBILY_CODES["فوائد الباقة"]["text"]
    elif "سلفني" in message_text_lower or "سلفة" in message_text_lower:
        return MOBILY_CODES["سلفني"]["text"]
    elif "تفعيل 4g" in message_text_lower or "تفعيل فور جي" in message_text_lower:
        return MOBILY_CODES["تفعيل 4G"]["text"]
    elif "تجديد باقة" in message_text_lower or "تجديد الاشتراك" in message_text_lower:
        return MOBILY_CODES["تجديد الباقة"]["text"]
    
    # Default response if no specific match is found
    return "عذراً، لم أفهم طلبك. يمكنك أن تسأل عن 'الرصيد'، 'رقمي'، 'تعبئة'، 'خدمة العملاء'، 'باقات انترنت' أو 'تحويل رصيد'. للحصول على قائمة بالخدمات العامة، اسأل عن 'خدمات'."

# --- Main Webhook Route for Facebook Messenger ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    Handles incoming webhook requests from Facebook Messenger.
    GET requests are for webhook verification.
    POST requests contain message events.
    """
    if request.method == 'GET':
        # Webhook verification logic (Facebook sends a GET request to verify the URL)
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print("WEBHOOK_VERIFIED: Successfully verified Facebook webhook.")
                return challenge, 200 # Return the challenge string to Facebook
            else:
                print("WEBHOOK_VERIFICATION_FAILED: Token mismatch or incorrect mode.")
                return "Verification token mismatch or incorrect mode", 403
        print("WEBHOOK_VERIFICATION_FAILED: Missing parameters for GET request.")
        return "Missing parameters", 400

    elif request.method == 'POST':
        # Handle incoming message events from Facebook
        data = request.json
        # print(f"Received webhook data (POST): {json.dumps(data, indent=2, ensure_ascii=False)}") # Uncomment for detailed logging

        # Ensure the event is a page event
        if data.get('object') == 'page':
            for entry in data['entry']:
                for messaging_event in entry['messaging']:
                    # Check if the event is a message and contains text
                    if messaging_event.get('message') and messaging_event['message'].get('text'):
                        sender_id = messaging_event['sender']['id'] # The ID of the user sending the message
                        message_text = messaging_event['message']['text'] # The text of the message
                        
                        print(f"Processing message from {sender_id}: '{message_text}'")
                        
                        # Process the user's message and get the appropriate response
                        response_text = process_user_message(message_text)
                        
                        # Send the generated response back to the user
                        send_message(sender_id, response_text)
        return "EVENT_RECEIVED", 200 # Always return 200 OK to Facebook

# --- Application Entry Point ---
if __name__ == '__main__':
    # Get the port from environment variables (e.g., set by Replit or Netlify)
    # Default to 8080 if PORT is not set.
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Flask app on port {port}...")
    app.run(host='0.0.0.0', port=port)

