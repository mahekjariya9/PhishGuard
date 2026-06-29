# generate_dataset.py
#
# Builds urls_raw.csv -- a labeled set of phishing (1) and legitimate (0) URLs.
#
# I'm using a synthetic generator here instead of pulling live data because
# PhishTank's feed and the Tranco top-sites list both need a live download,
# and I wanted something reproducible I could commit alongside the code.
# Swap data/urls_raw.csv with a real PhishTank/Tranco export later -- nothing
# else in the pipeline needs to change.

from pathlib import Path
import pandas as pd
import random
import string

random.seed(42)

LEGIT_DOMAINS = [
    "google.com", "github.com", "wikipedia.org", "amazon.com", "microsoft.com",
    "apple.com", "linkedin.com", "stackoverflow.com", "reddit.com", "nytimes.com",
    "uga.edu", "irs.gov", "chase.com", "paypal.com", "spotify.com", "netflix.com",
    "dropbox.com", "salesforce.com", "adobe.com", "indeed.com", "ups.com",
    "fedex.com", "bankofamerica.com", "wellsfargo.com", "usps.com", "ebay.com"
]

SUSPICIOUS_TLDS = [".xyz", ".top", ".club", ".info", ".online", ".live", ".click", ".tk"]
BRAND_TARGETS = ["paypal", "amazon", "apple", "microsoft", "bankofamerica", "chase",
                  "netflix", "irs", "usps", "fedex", "wellsfargo", "google"]
PHISH_KEYWORDS = ["secure", "verify", "account", "update", "confirm", "login",
                   "signin", "alert", "suspended", "billing", "support"]


def random_string(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))


def make_legit_url():
    domain = random.choice(LEGIT_DOMAINS)
    path_depth = random.choice([0, 1, 1, 2, 3])
    path = "/".join(random_string(random.randint(3, 10)) for _ in range(path_depth))
    scheme = "https" if random.random() < 0.93 else "http"  # most real sites use https now, not all
    sub = random.choice(["www", "www", "shop", "support", "id", "account"])
    url = f"{scheme}://{sub}.{domain}/{path}" if path else f"{scheme}://{sub}.{domain}"
    if random.random() < 0.15:
        url += f"?ref={random_string(4)}&id={random.randint(100,999)}"
    if random.random() < 0.08:  # some legit marketing domains use hyphens too
        url = url.replace(domain, domain.replace(".", f"-{random_string(3)}."))
    return url


def make_phish_url():
    style = random.choice(["typosquat", "subdomain_stuffing", "ip_based",
                            "long_random", "convincing_https"])
    brand = random.choice(BRAND_TARGETS)
    keyword = random.choice(PHISH_KEYWORDS)
    tld = random.choice(SUSPICIOUS_TLDS)
    scheme = "https" if random.random() < 0.55 else "http"  # free certs mean phishing sites use https too now

    if style == "typosquat":
        misspelled = brand[:-1] + random.choice(string.ascii_lowercase)
        url = f"{scheme}://{misspelled}-{keyword}{tld}/{random_string(6)}"
    elif style == "subdomain_stuffing":
        fake_subs = ".".join(random_string(5) for _ in range(random.randint(2, 4)))
        url = f"{scheme}://{brand}.{fake_subs}{tld}/{keyword}"
    elif style == "ip_based":
        ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        url = f"{scheme}://{ip}/{brand}/{keyword}.php"
    elif style == "convincing_https":
        # harder case -- clean https domain, no ip, no sketchy tld, just an off brand name
        url = f"{scheme}://{brand}-{keyword}.com/{random_string(8)}"
    else:  # long_random
        url = f"{scheme}://{random_string(10)}-{keyword}-{brand}{tld}/{random_string(15)}"

    return url


N_PER_CLASS = 5000
rows = []
for _ in range(N_PER_CLASS):
    rows.append({"url": make_legit_url(), "label": 0})
for _ in range(N_PER_CLASS):
    rows.append({"url": make_phish_url(), "label": 1})

df = pd.DataFrame(rows).drop_duplicates(subset="url").sample(frac=1, random_state=42).reset_index(drop=True)

# flip a small % of labels -- real labeling is never 100% clean (reports come in
# late, sites get taken down/repurposed, some urls are genuinely borderline) and
# without any noise the dataset is too easy, which would make the accuracy number
# meaningless
flip_mask = df.sample(frac=0.03, random_state=7).index
df.loc[flip_mask, "label"] = 1 - df.loc[flip_mask, "label"]

BASE_DIR = Path(__file__).resolve().parent
df.to_csv(BASE_DIR / "urls_raw.csv", index=False)

print(f"Generated {len(df)} unique URLs")
print(df["label"].value_counts().rename({0: "legitimate", 1: "phishing"}))
print("\nSample rows:")
print(df.head(8).to_string(index=False))
