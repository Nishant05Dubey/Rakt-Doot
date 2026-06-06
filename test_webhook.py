import urllib.request
import urllib.parse
data = urllib.parse.urlencode({'Body': 'hospital kaha hai', 'From': 'whatsapp:+919340766550'}).encode('utf-8')
req = urllib.request.Request('https://g5tsqk93w9.execute-api.ap-south-1.amazonaws.com/donor/respond', data=data)
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
try:
    res = urllib.request.urlopen(req)
    print("hospital kaha hai ->", res.read().decode())
except Exception as e:
    print('Error:', e)
    
data = urllib.parse.urlencode({'Body': 'yess', 'From': 'whatsapp:+919340766550'}).encode('utf-8')
req = urllib.request.Request('https://g5tsqk93w9.execute-api.ap-south-1.amazonaws.com/donor/respond', data=data)
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
try:
    res = urllib.request.urlopen(req)
    print("yess ->", res.read().decode())
except Exception as e:
    print('Error:', e)
