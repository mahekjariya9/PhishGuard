# test_predictions.py
#
# Quick sanity check against the model with a few URLs I picked by hand,
# including known brands and a couple of phishing patterns.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app import predict_url

test_cases = [
    ("https://www.google.com/search?q=test", "legitimate"),
    ("https://github.com/mahekjariya/phishguard", "legitimate"),
    ("http://paypal-secure-login.xyz/verify/account", "phishing"),
    ("http://192.168.45.12/irs/refund.php", "phishing"),
    ("https://amazon-billing.online/wp/zk3hqp1rmf", "phishing"),
    ("https://www.linkedin.com/in/mahek-jariya", "legitimate"),
    ("http://chase.s9j2k.l0pqw.click/account/confirm", "phishing"),
]

print(f"{'URL':<55} {'Predicted':<12} {'Confidence':<12} {'Expected':<12} {'Match'}")
print("-" * 105)
correct = 0
for url, expected in test_cases:
    result = predict_url(url)
    match = "✓" if result["label"] == expected else "✗"
    correct += (result["label"] == expected)
    print(f"{url[:53]:<55} {result['label']:<12} {result['confidence']:<12} {expected:<12} {match}")

print(f"\n{correct}/{len(test_cases)} correct on hand-picked spot checks")
