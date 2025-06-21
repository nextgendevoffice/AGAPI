from flask import Flask, request, jsonify
from flask_cors import CORS 
import requests
import logging
import json
app = Flask(__name__)
CORS(app)

# URL ของ API
LOGIN_URL = "https://ag.ambkingapi.com/a/m/authen"
CLIENT_SIGNATURE_URL = "https://ag.ambkingapi.com/a/m/clientSignature"
DATA_URL = "https://ag.ambkingapi.com/a/rep/winLoseProviderEs"
PROFILE_URL = "https://ag.ambkingapi.com/a/m/getProfile"
MEMBER_LIST_URL = "https://ag.ambkingapi.com/a/p/memberList"
DEPOSIT_URL = "https://ag.ambkingapi.com/a/p/deposit"

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
    baseUrl = request.json.get('baseUrl')

    # Headers สำหรับการดึงข้อมูล
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
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

        # Payload สำหรับการดึงข้อมูล win/lose
        payload = {
            "underId": under_id,
            "startDate": start_date,
            "endDate": end_date,
            "betType": ["normal", "comboStep", "step", "Casino", "Slot", "Lotto", "Keno", "Trade", "Card", "Poker", "m2", "Esport", "Cock", "Sbo", "Saba", "Plb", "Vsb", "Fbs", "Umb", "Afb", "Lali", "Wss"],
            "cur": "THB",
            "skip": 0,
            "limit": 100,
            "page": 1
        }

        # บันทึกข้อมูล payload ในรูปแบบ JSON ที่อ่านง่าย
        logging.info("Payload: %s", json.dumps(payload, indent=4))

        # เรียก API สำหรับข้อมูล win/lose
        winlose_response = requests.post(baseUrl + "/a/rep/winloseEs" if baseUrl else "https://ag.ambkingapi.com/a/rep/winloseEs", json=payload, headers=headers)

        # เรียก API สำหรับข้อมูลสรุปผลลัพธ์
        footer_response = requests.post(baseUrl + "/a/rep/winloseFooterEs" if baseUrl else "https://ag.ambkingapi.com/a/rep/winloseFooterEs", json=payload, headers=headers)

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

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
