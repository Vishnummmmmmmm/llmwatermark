import urllib.request
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

cases = {
    'Claude AI Text': 'It is important to note that artificial intelligence models utilize multifaceted architectures to facilitate complex responses.',
    'Health / Medical Text': 'The patient presented with acute symptoms and the clinical diagnosis required immediate therapeutic intervention.',
    'Random Letters / Gibberish': 'asdfghjk qwertyuiop zxcvbnm lkjhgfdsa poiuytrewq',
    'Invisible Steganography': 'Artificial\u200B intelligence\u200C language\u200D models\uFEFF produce\u200E responses\u200F with homoglyph\u0430 markers.'
}

print("=" * 60)
print("TESTING /api/process/auto (Universal Endpoint)")
print("=" * 60)

for name, text in cases.items():
    print(f"\n>>> [{name}]")
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = f'--{boundary}\r\nContent-Disposition: form-data; name="text"\r\n\r\n{text}\r\n--{boundary}--\r\n'.encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:3000/api/process/auto',
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    try:
        res = urllib.request.urlopen(req)
        json_resp = json.loads(res.read().decode())
        result = json_resp.get('result', {})
        print(f"Domain:       {result.get('domain_label')}")
        print(f"Risk Shift:   {result.get('initial_risk_percentage')}% ➔ {result.get('final_risk_percentage')}%")
        print(f"Summary:      {result.get('removal_summary')}")
        print(f"Cleaned Text: {result.get('cleaned_text')}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 60)
print("ALL NEXT.JS AUTO TESTS COMPLETED")
print("=" * 60)
