from flask import Flask, request, jsonify
import requests
import logging
app = Flask(__name__)

# URL ของ API
LOGIN_URL = "https://ag.ambkingapi.com/a/m/authen"
CLIENT_SIGNATURE_URL = "https://ag.ambkingapi.com/a/m/clientSignature"
DATA_URL = "https://ag.ambkingapi.com/a/rep/winLoseProviderEs"
PROFILE_URL = "https://ag.ambkingapi.com/a/m/getProfile"
MEMBER_LIST_URL = "https://ag.ambkingapi.com/a/p/memberList"
DEPOSIT_URL = "https://ag.ambkingapi.com/a/p/deposit"

@app.route('/login', methods=['POST'])
def login():
    # ดึง client signature
    response = requests.get(CLIENT_SIGNATURE_URL)
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
    response = requests.post(LOGIN_URL, json=login_payload, headers=login_headers)

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
    data_response = requests.post(DATA_URL, json=data_payload, headers=data_headers)

    # ตรวจสอบผลลัพธ์การดึงข้อมูล
    if data_response.status_code == 200:
        return jsonify(data_response.json())
    else:
        return jsonify({"message": "Failed to retrieve data", "status_code": data_response.status_code}), 500

@app.route('/get-profile', methods=['POST'])
def get_profile():
    token = request.json.get('token')

    # Headers สำหรับการดึงข้อมูลโปรไฟล์
    profile_headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "origin": "https://ag.ambkub.com",
        "referer": "https://ag.ambkub.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    # ส่งคำขอดึงข้อมูลโปรไฟล์
    profile_response = requests.get(PROFILE_URL, headers=profile_headers)

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

if __name__ == '__main__':
    app.run(debug=True)
