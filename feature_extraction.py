# feature_extraction.py
#
# Turns a raw URL string into a numeric feature vector for the model.
#
# Note: a domain-age feature (via WHOIS) would probably help accuracy, but
# WHOIS needs a live lookup per URL which adds latency and a hard
# dependency on an external service being up. Skipping it for now and
# sticking to features I can pull straight from the URL string.

import re
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    "secure", "verify", "account", "update", "confirm", "login", "signin",
    "alert", "suspended", "billing", "support", "webscr", "ebayisapi"
]
SUSPICIOUS_TLDS = {".xyz", ".top", ".club", ".info", ".online", ".live", ".click", ".tk"}


def has_ip_address(domain: str) -> int:
    return 1 if re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", domain) else 0


def count_suspicious_keywords(url: str) -> int:
    url_lower = url.lower()
    return sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)


def extract_features(url: str) -> dict:
    parsed = urlparse(url if "://" in url else f"http://{url}")
    domain = parsed.netloc.split(":")[0]
    path = parsed.path or ""

    subdomain_parts = domain.split(".")
    tld = "." + subdomain_parts[-1] if len(subdomain_parts) > 1 else ""

    features = {
        "url_length": len(url),
        "domain_length": len(domain),
        "path_length": len(path),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_digits": sum(c.isdigit() for c in url),
        "num_subdomains": max(len(subdomain_parts) - 2, 0),
        "has_https": 1 if parsed.scheme == "https" else 0,
        "has_ip_address": has_ip_address(domain),
        "has_at_symbol": 1 if "@" in url else 0,
        "suspicious_tld": 1 if tld in SUSPICIOUS_TLDS else 0,
        "suspicious_keyword_count": count_suspicious_keywords(url),
        "num_special_chars": len(re.findall(r"[!$%^&*()_+|~=`{}\[\]:;\"'<>?,]", url)),
        "path_depth": path.count("/"),
    }
    return features


FEATURE_NAMES = list(extract_features("http://example.com/path").keys())


if __name__ == "__main__":
    test_urls = [
        "https://www.google.com/search",
        "http://paypal-secure-login.xyz/verify/account",
        "http://192.168.1.1/irs/confirm.php",
    ]
    for u in test_urls:
        print(u)
        print(extract_features(u))
        print()
