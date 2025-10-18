# 🔑 ZombieCoder Authentication Setup

## HuggingFace Token Configuration

### ১. টোকেন পাওয়া

1. **HuggingFace Hub এ যান:** https://huggingface.co/settings/tokens
2. **নতুন টোকেন তৈরি করুন:** "New token" বাটনে ক্লিক করুন
3. **টোকেন কপি করুন:** `hf_xxxxx` ফরম্যাটে

### ২. টোকেন সেট করা

#### **UI থেকে (সবচেয়ে সহজ):**
1. সার্ভার চালু করুন: `.\start_server.ps1`
2. ব্রাউজারে যান: `http://127.0.0.1:8155/static/allindex.html`
3. "HuggingFace Login" সেকশনে টোকেন দিন
4. "Save Token" বাটনে ক্লিক করুন

#### **API থেকে:**
```bash
curl -X POST http://127.0.0.1:8155/auth/hf_token \
  -H "Content-Type: application/json" \
  -d '{"token":"hf_YOUR_ACTUAL_TOKEN"}'
```

#### **Python থেকে:**
```python
import requests

token = "hf_YOUR_ACTUAL_TOKEN"
response = requests.post("http://127.0.0.1:8155/auth/hf_token", 
                        json={"token": token})
print(response.json())
```

### ৩. টোকেন যাচাই

```bash
# Auth status check
curl http://127.0.0.1:8155/auth/status

# User info
curl http://127.0.0.1:8155/auth/whoami
```

### ৪. ফাইল আপডেট

**লোকাল ব্যবহারের জন্য ফাইলগুলো আপডেট করুন:**

#### `static/allindex.html`:
```html
<input id="hfToken" type="password" placeholder="hf_xxx token" 
       style="min-width:340px" value="hf_YOUR_ACTUAL_TOKEN" />
```

#### `test_complete_flow.py`:
```python
token = "hf_YOUR_ACTUAL_TOKEN"
```

#### `test_with_auth.py`:
```python
HF_TOKEN = "hf_YOUR_ACTUAL_TOKEN"
```

### ৫. টেস্ট

```bash
# Authentication test
python test_with_auth.py

# Complete flow test
python test_complete_flow.py
```

## 🔒 Security Notes

- **GitHub Push Protection:** রিয়েল টোকেন GitHub এ push করবেন না
- **Environment Variables:** Production এ environment variable ব্যবহার করুন
- **Token Rotation:** নিয়মিত টোকেন পরিবর্তন করুন

## 📋 Troubleshooting

### সমস্যা: 401 Unauthorized
**সমাধান:** টোকেন সঠিকভাবে সেট করা হয়েছে কিনা চেক করুন

### সমস্যা: Token not set
**সমাধান:** `/auth/status` এন্ডপয়েন্ট চেক করুন

### সমস্যা: Download failed
**সমাধান:** টোকেনের permission চেক করুন (read access প্রয়োজন)

---

**নোট:** এই ফাইলটি লোকাল ব্যবহারের জন্য। GitHub এ push করার আগে টোকেন সরিয়ে দিন।
