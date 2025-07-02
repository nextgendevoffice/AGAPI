from flask import Flask, request, jsonify
from flask_cors import CORS 
import requests
import logging
import json
app = Flask(__name__)
CORS(app)

# URL ของ API
LOGIN_URL = "https://ag.googletran.link/a/m/authen"
CLIENT_SIGNATURE_URL = "https://ag.googletran.link/a/m/clientSignature"
DATA_URL = "https://ag.googletran.link/a/rep/winLoseProviderEs"
PROFILE_URL = "https://ag.googletran.link/a/m/getProfile"
MEMBER_LIST_URL = "https://ag.googletran.link/a/p/memberList"
DEPOSIT_URL = "https://ag.googletran.link/a/p/deposit"

# ตั้งค่าการบันทึกข้อมูล
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return "Hello, World2!"

@app.route('/login', methods=['POST'])
def login():
    # ดึง client signature
    baseUrl = request.json.get('baseUrl')
    response = requests.get(baseUrl + "/a/m/clientSignature" if baseUrl else CLIENT_SIGNATURE_URL)
    client_signature = response.json()['result']['uuid']

    # ข้อมูล payload สำหรับการ login
    login_payload = {
        "username": request.json.get('username'),
        "password": request.json.get('password'),
        "captcha": "",
        "clientSignature": client_signature
    }

    # Headers ที่จำเป็นสำหรับการ login
    login_headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    # ส่งคำขอ login
    response = requests.post(baseUrl + "/a/m/authen" if baseUrl else LOGIN_URL, json=login_payload, headers=login_headers)

    # ตรวจสอบผลลัพธ์การ login
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 0:
            return jsonify({"message": "Login successful!", "token": data['data']['token']})
        else:
            return jsonify({"message": "Login failed", "error": data['msg']}), 401
    else:
        return jsonify({"message": "Request failed", "status_code": response.status_code}), 500

@app.route('/get-data', methods=['POST'])
def get_data():
    token = request.json.get('token')
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')
    currency = request.json.get('cur')
    baseUrl = request.json.get('baseUrl')
    # Headers สำหรับการดึงข้อมูล
    data_headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    # Payload สำหรับการดึงข้อมูล
    data_payload = {
        "startDate": start_date,
        "endDate": end_date,
        "cur": currency
    }

    # ส่งคำขอดึงข้อมูล
    data_response = requests.post(baseUrl + "/a/rep/winLoseProviderEs" if baseUrl else DATA_URL, json=data_payload, headers=data_headers)

    # ตรวจสอบผลลัพธ์การดึงข้อมูล
    if data_response.status_code == 200:
        return jsonify(data_response.json())
    else:
        return jsonify({"message": "Failed to retrieve data", "status_code": data_response.status_code}), 500

@app.route('/get-profile', methods=['POST'])
def get_profile():
    token = request.json.get('token')
    baseUrl = request.json.get('baseUrl')
    # Headers สำหรับการดึงข้อมูลโปรไฟล์
    profile_headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    # ส่งคำขอดึงข้อมูลโปรไฟล์
    profile_response = requests.get(baseUrl + "/a/m/getProfile" if baseUrl else PROFILE_URL, headers=profile_headers)

    # ตรวจสอบผลลัพธ์การดึงข้อมูลโปรไฟล์
    if profile_response.status_code == 200:
        return jsonify(profile_response.json())
    else:
        return jsonify({"message": "Failed to retrieve profile", "status_code": profile_response.status_code}), 500

@app.route('/deposit', methods=['POST'])
def deposit():
    token = request.json.get('token')
    username = request.json.get('username')  # เปลี่ยนจาก userId เป็น username
    amount = request.json.get('amount')
    currency = request.json.get('cur')
    passcode = request.json.get('passcode')

    # Headers สำหรับการดึงข้อมูลสมาชิก
    member_headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    # Payload สำหรับการดึงข้อมูลสมาชิก
    member_payload = {
        "page": 1,
        "limit": 100
    }

    # ส่งคำขอดึงข้อมูลสมาชิก
    member_response = requests.post(MEMBER_LIST_URL, json=member_payload, headers=member_headers)

    if member_response.status_code == 200:
        members = member_response.json().get('data', {}).get('docs', [])
        user_id = None

        # ค้นหา _id ของ username ที่ต้องการ
        for member in members:
            if member['username'] == username:
                user_id = member['_id']
                break

        if user_id is None:
            return jsonify({"message": "Username not found"}), 404

        # Headers สำหรับการฝากเงิน
        deposit_headers = {
            "accept": "application/json, text/plain, */*",
            "authorization": token,
            "content-type": "application/json",
            "origin": "https://ag.ambkub.com",
            "referer": "https://ag.ambkub.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
        }

        # Payload สำหรับการฝากเงิน
        deposit_payload = {
            "userId": user_id,  # ใช้ _id ที่ค้นหาได้
            "cur": currency,
            "amount": amount,
            "passcode": passcode
        }

        # บันทึกข้อมูลคำขอที่กำลังจะส่งออกไป
        logging.info(f"Sending deposit request: {deposit_payload}")

        # ส่งคำขอฝากเงิน
        deposit_response = requests.post(DEPOSIT_URL, json=deposit_payload, headers=deposit_headers)

        if deposit_response.status_code == 200:
            return jsonify(deposit_response.json())
        else:
            return jsonify({"message": "Failed to deposit", "status_code": deposit_response.status_code}), 500
    else:
        return jsonify({"message": "Failed to retrieve member list", "status_code": member_response.status_code}), 500

@app.route('/getwlagent', methods=['POST'])
def get_wlagent():
    token = request.json.get('token')
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')
    baseUrl = request.json.get('baseUrl', 'https://ag.googletran.link')

    # Headers สำหรับการดึงข้อมูล (ปรับปรุงตาม curl ล่าสุด)
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "priority": "u=1, i",
        "referer": "https://ag.ambkub.com/",
        "sec-ch-ua": '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
    }

    # ดึง underId จาก member_response
    member_headers = headers.copy()

    member_payload = {
        "page": 1,
        "limit": 100
    }

    member_response = requests.post(baseUrl + "/a/p/memberList" if baseUrl else MEMBER_LIST_URL, json=member_payload, headers=member_headers)

    # บันทึกข้อมูล response ในรูปแบบ JSON ที่อ่านง่าย
    logging.info("Member response: %s", json.dumps(member_response.json(), indent=4))

    if member_response.status_code == 200:
        response_data = member_response.json()
        docs = response_data.get('data', {}).get('docs', [])
        under_id = None

        if docs:
            under_id = docs[0].get('parent')

        # บันทึกข้อมูล under_id
        logging.info(f"UnderId: {under_id}")

        if under_id is None:
            return jsonify({"message": "UnderId not found"}), 404

        # Payload สำหรับการดึงข้อมูล win/lose (เพิ่ม betType ใหม่)
        payload = {
            "underId": under_id,
            "startDate": start_date,
            "endDate": end_date,
            "betType": ["normal", "comboStep", "step", "Casino", "Slot", "Lotto", "Keno", "Trade", "Card", "Poker", "m2", "Esport", "Cock", "Sbo", "Saba", "Plb", "Vsb", "Fbs", "Umb", "Afb", "Lali", "Wss", "Dbs", "M8", "Ufa"],
            "cur": "THB",
            "skip": 0,
            "limit": 100,
            "page": 1
        }

        # บันทึกข้อมูล payload ในรูปแบบ JSON ที่อ่านง่าย
        logging.info("Payload: %s", json.dumps(payload, indent=4))

        # เรียก API สำหรับข้อมูล win/lose (ใช้ URL ใหม่ที่มี New ต่อท้าย)
        winlose_url = baseUrl + "/a/rep/winloseEsNew"
        winlose_response = requests.post(winlose_url, json=payload, headers=headers)

        # เรียก API สำหรับข้อมูลสรุปผลลัพธ์ (อาจต้องใช้ URL ใหม่เช่นกัน)
        footer_url = baseUrl + "/a/rep/winloseFooterEsNew"
        footer_response = requests.post(footer_url, json=payload, headers=headers)

        if winlose_response.status_code == 200 and footer_response.status_code == 200:
            winlose_data = winlose_response.json()
            footer_data = footer_response.json()
            return jsonify({
                "winlose": winlose_data,
                "footer": footer_data
            })
        else:
            return jsonify({"message": "Failed to retrieve data", "status_code": winlose_response.status_code}), 500
    else:
        return jsonify({"message": "Failed to retrieve member list", "status_code": member_response.status_code}), 500

@app.route('/creditag', methods=['POST'])
def get_creditag():
    token = request.json.get('token')
    
    # Headers สำหรับการดึงข้อมูล credit
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }

    # Payload สำหรับการดึงข้อมูล
    payload = {
        "page": 1,
        "limit": 100
    }

    # ส่งคำขอดึงข้อมูล credit
    response = requests.post("https://ag.googletran.link/a/p/memberList", json=payload, headers=headers)

    # ตรวจสอบผลลัพธ์การดึงข้อมูล
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 0 and data.get('data') and data['data'].get('docs'):
            # ดึงข้อมูล credit จาก response
            credit_info = []
            for member in data['data']['docs']:
                thb_balance = member.get('balance', {}).get('THB', {}).get('balance', {}).get('$numberDecimal', '0')
                credit_info.append({
                    'username': member.get('username'),
                    'name': member.get('name'),
                    'credit': float(thb_balance),
                    'lastLogin': member.get('lastLogin')
                })
            return jsonify({
                "status": "success",
                "data": credit_info
            })
        else:
            return jsonify({"message": "No credit data found"}), 404
    else:
        return jsonify({
            "message": "Failed to retrieve credit information", 
            "status_code": response.status_code
        }), 500

@app.route('/top10product', methods=['POST'])
def get_top10product():
    token = request.json.get('token')
    agent_id = request.json.get('agentId')
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')
    prefix = request.json.get('prefix', 'AMBK')
    currency = request.json.get('currency', '')
    baseUrl = request.json.get('baseUrl', 'https://ag.googletran.link')

    # Headers สำหรับการดึงข้อมูล
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }

    # Payload สำหรับการดึงข้อมูล
    payload = {
        "agentId": agent_id,
        "startDate": start_date,
        "endDate": end_date,
        "prefix": prefix,
        "currency": currency
    }

    # ส่งคำขอดึงข้อมูล
    url = f"{baseUrl}/a/dashboard/top10Product"
    response = requests.post(url, json=payload, headers=headers)

    # ตรวจสอบผลลัพธ์การดึงข้อมูล
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({
            "message": "Failed to retrieve top 10 products", 
            "status_code": response.status_code,
            "url": url
        }), 500

@app.route('/top10gamelose', methods=['POST'])
def get_top10gamelose():
    token = request.json.get('token')
    agent_id = request.json.get('agentId')
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')
    prefix = request.json.get('prefix', 'AMBK')
    currency = request.json.get('currency', '')
    baseUrl = request.json.get('baseUrl', 'https://ag.googletran.link')

    # Headers สำหรับการดึงข้อมูล
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }

    # Payload สำหรับการดึงข้อมูล
    payload = {
        "agentId": agent_id,
        "startDate": start_date,
        "endDate": end_date,
        "prefix": prefix,
        "currency": currency
    }

    # ส่งคำขอดึงข้อมูล
    url = f"{baseUrl}/a/dashboard/top10GameLose"
    response = requests.post(url, json=payload, headers=headers)

    # ตรวจสอบผลลัพธ์การดึงข้อมูล
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({
            "message": "Failed to retrieve top 10 game lose data", 
            "status_code": response.status_code,
            "url": url
        }), 500

@app.route('/top10gamewin', methods=['POST'])
def get_top10gamewin():
    token = request.json.get('token')
    agent_id = request.json.get('agentId')
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')
    prefix = request.json.get('prefix', 'AMBK')
    currency = request.json.get('currency', '')
    baseUrl = request.json.get('baseUrl', 'https://ag.googletran.link')

    # Headers สำหรับการดึงข้อมูล
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }

    # Payload สำหรับการดึงข้อมูล
    payload = {
        "agentId": agent_id,
        "startDate": start_date,
        "endDate": end_date,
        "prefix": prefix,
        "currency": currency
    }

    # ส่งคำขอดึงข้อมูล
    url = f"{baseUrl}/a/dashboard/top10GameWin"
    response = requests.post(url, json=payload, headers=headers)

    # ตรวจสอบผลลัพธ์การดึงข้อมูล
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({
            "message": "Failed to retrieve top 10 game win data", 
            "status_code": response.status_code,
            "url": url
        }), 500

@app.route('/winlose_member', methods=['POST'])
def winlose_member():
    token = request.json.get('token')
    under_id = request.json.get('underId')
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')
    bet_type = request.json.get('betType', ["normal", "comboStep", "step", "Casino", "Slot", "Lotto", "Keno", "Trade", "Card", "Poker", "m2", "Esport", "Cock", "Sbo", "Saba", "Plb", "Vsb", "Fbs", "Umb", "Afb", "Lali", "Wss", "Dbs", "M8", "Ufa"])
    currency = request.json.get('cur', 'THB')
    skip = request.json.get('skip', 0)
    limit = request.json.get('limit', 100)
    page = request.json.get('page', 1)
    baseUrl = request.json.get('baseUrl', 'https://ag.googletran.link')

    # Headers สำหรับการดึงข้อมูล
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "priority": "u=1, i",
        "referer": "https://ag.ambkub.com/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    }

    # Payload สำหรับการดึงข้อมูล win/lose
    payload = {
        "underId": under_id,
        "startDate": start_date,
        "endDate": end_date,
        "betType": bet_type,
        "cur": currency,
        "skip": skip,
        "limit": limit,
        "page": page
    }

    # บันทึกข้อมูล payload
    logging.info("Winlose member payload: %s", json.dumps(payload, indent=4))

    # เรียก API สำหรับข้อมูล win/lose
    winlose_url = baseUrl + "/a/rep/winloseEsNew"
    winlose_response = requests.post(winlose_url, json=payload, headers=headers)

    # เรียก API สำหรับข้อมูลสรุปผลลัพธ์
    footer_url = baseUrl + "/a/rep/winloseFooterEsNew"
    footer_response = requests.post(footer_url, json=payload, headers=headers)

    if winlose_response.status_code == 200 and footer_response.status_code == 200:
        winlose_data = winlose_response.json()
        footer_data = footer_response.json()
        return jsonify({
            "winlose": winlose_data,
            "footer": footer_data
        })
    else:
        error_message = "Failed to retrieve data"
        error_details = {
            "message": error_message,
            "winlose_status": winlose_response.status_code,
            "footer_status": footer_response.status_code
        }
        
        # เพิ่มข้อมูล response body ถ้ามี error
        if winlose_response.status_code != 200:
            try:
                error_details["winlose_error"] = winlose_response.json()
            except:
                error_details["winlose_error"] = winlose_response.text
                
        if footer_response.status_code != 200:
            try:
                error_details["footer_error"] = footer_response.json()
            except:
                error_details["footer_error"] = footer_response.text
                
        return jsonify(error_details), 500

@app.route('/winlose_member_detail', methods=['POST'])
def winlose_member_detail():
    token = request.json.get('token')
    under_id = request.json.get('underId')
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')
    bet_type = request.json.get('betType', ["normal", "comboStep", "step", "Casino", "Slot", "Lotto", "Keno", "Trade", "Card", "Poker", "m2", "Esport", "Cock", "Sbo", "Saba", "Plb", "Vsb", "Fbs", "Umb", "Afb", "Lali", "Wss", "Dbs", "M8", "Ufa"])
    currency = request.json.get('cur', ['THB'])  # เป็น array
    skip = request.json.get('skip', 0)
    limit = request.json.get('limit', 100)
    page = request.json.get('page', 1)
    baseUrl = request.json.get('baseUrl', 'https://ag.googletran.link')

    # Headers สำหรับการดึงข้อมูล
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "priority": "u=1, i",
        "referer": "https://ag.ambkub.com/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    }

    # ตรวจสอบว่า currency เป็น string หรือ array
    if isinstance(currency, str):
        currency = [currency]

    # Payload สำหรับการดึงข้อมูล win/lose detail
    payload = {
        "underId": under_id,
        "startDate": start_date,
        "endDate": end_date,
        "betType": bet_type,
        "cur": currency,  # ส่งเป็น array
        "skip": skip,
        "limit": limit,
        "page": page
    }

    # บันทึกข้อมูล payload
    logging.info("Winlose member detail payload: %s", json.dumps(payload, indent=4))

    # เรียก API สำหรับข้อมูล win/lose detail
    detail_url = baseUrl + "/a/rep/winLoseDetail"
    detail_response = requests.post(detail_url, json=payload, headers=headers)

    if detail_response.status_code == 200:
        detail_data = detail_response.json()
        return jsonify(detail_data)
    else:
        error_message = "Failed to retrieve win/lose detail"
        error_details = {
            "message": error_message,
            "status_code": detail_response.status_code
        }
        
        # เพิ่มข้อมูล response body ถ้ามี error
        try:
            error_details["error"] = detail_response.json()
        except:
            error_details["error"] = detail_response.text
                
        return jsonify(error_details), 500

@app.route('/winlose_find_by_precalid', methods=['POST'])
def winlose_find_by_precalid():
    token = request.json.get('token')
    precal_id = request.json.get('id')
    limit = request.json.get('limit', 100)
    page = request.json.get('page', 1)
    baseUrl = request.json.get('baseUrl', 'https://ag.googletran.link')

    # Headers สำหรับการดึงข้อมูล
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "priority": "u=1, i",
        "referer": "https://ag.ambkub.com/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    }

    # Payload สำหรับการค้นหาด้วย preCalId
    payload = {
        "id": precal_id,
        "limit": limit,
        "page": page
    }

    # บันทึกข้อมูล payload
    logging.info("WinLose find by preCalId payload: %s", json.dumps(payload, indent=4))

    # เรียก API สำหรับค้นหาข้อมูล win/lose ด้วย preCalId
    find_url = baseUrl + "/a/rep/winLoseFindByPreCalId"
    find_response = requests.post(find_url, json=payload, headers=headers)

    if find_response.status_code == 200:
        find_data = find_response.json()
        return jsonify(find_data)
    else:
        error_message = "Failed to find win/lose by preCalId"
        error_details = {
            "message": error_message,
            "status_code": find_response.status_code,
            "precal_id": precal_id
        }
        
        # เพิ่มข้อมูล response body ถ้ามี error
        try:
            error_details["error"] = find_response.json()
        except:
            error_details["error"] = find_response.text
                
        return jsonify(error_details), 500

@app.route('/bet_detail_member', methods=['POST'])
def bet_detail_member():
    token = request.json.get('token')
    game_id = request.json.get('gameId')
    ref1 = request.json.get('ref1')
    ref2 = request.json.get('ref2')
    ref3 = request.json.get('ref3')
    bet_time = request.json.get('betTime')
    username = request.json.get('username')
    baseUrl = request.json.get('baseUrl', 'https://ag.googletran.link')

    # Headers สำหรับการดึงข้อมูล
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "priority": "u=1, i",
        "referer": "https://ag.ambkub.com/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    }

    # Payload สำหรับการดึงรายละเอียดการเดิมพัน
    payload = {
        "gameId": game_id,
        "ref1": ref1,
        "ref2": ref2,
        "ref3": ref3,
        "betTime": bet_time,
        "username": username
    }

    # บันทึกข้อมูล payload
    logging.info("Bet detail member payload: %s", json.dumps(payload, indent=4))

    # เรียก API สำหรับดูรายละเอียดการเดิมพัน
    detail_url = baseUrl + "/a/rep/gameDetail"
    detail_response = requests.post(detail_url, json=payload, headers=headers)

    if detail_response.status_code == 200:
        detail_data = detail_response.json()
        return jsonify(detail_data)
    else:
        error_message = "Failed to retrieve bet detail"
        error_details = {
            "message": error_message,
            "status_code": detail_response.status_code,
            "game_id": game_id,
            "username": username
        }
        
        # เพิ่มข้อมูล response body ถ้ามี error
        try:
            error_details["error"] = detail_response.json()
        except:
            error_details["error"] = detail_response.text
                
        return jsonify(error_details), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
