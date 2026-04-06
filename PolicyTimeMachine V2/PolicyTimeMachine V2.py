import os
import re
import csv
import json
import time
from threading import Thread
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkcalendar import Calendar

# Optional: pip install readability-lxml lxml
try:
    from readability import Document  # type: ignore
except Exception:
    Document = None

# ---------------------------------------------------------
# CONSTANTS & GLOBALS
# ---------------------------------------------------------
CDX_API = "https://web.archive.org/cdx/search/cdx"
WAYBACK = "https://web.archive.org/web"
CUSTOM_FILE = "custom_targets.json"

DEFAULT_TARGETS = {
    "Facebook": {"Terms of Service": "https://www.facebook.com/terms.php",
                 "Privacy Policy":"https://mbasic.facebook.com/privacy/policy/printable",
                 "community-guideline":"https://transparency.fb.com/en-gb/policies/community-standards/"
                 },
    "Instagram": {"Terms of Service": "https://help.instagram.com/581066165581870/?helpref=hc_fnav",
                  "community-guideline":"https://help.instagram.com/477434105621119/?helpref=hc_fnav"
                  },
    "TikTok": {
        "Terms of Service": "https://www.tiktok.com/legal/page/us/terms-of-service/en",
        "community-guidelines": "https://www.tiktok.com/community-guidelines/en/overview",
        },
    "Alexa": {"Terms of Service": "https://www.amazon.com/gp/help/customer/display.html?nodeId=201809740",
              "Privacy Policy":"https://www.amazon.com/gp/help/customer/display.html?nodeId=GVP69FUJ48X9DK8V"
              },
    "BlenderBot": {"Terms of Service": "https://geo-not-available.blenderbot.ai/tos",
                   "Privacy Policy": "https://mbasic.facebook.com/privacy/policy/printable"
                   },
    "Character.AI": {"Terms of Service": "https://beta.character.ai/static/js/main.649eb915.js",
                     "Privacy Policy": "https://beta.character.ai/static/js/main.649eb915.js",
                     "Community Guidelines": "https://beta.character.ai/community"
                     },
    "Cortana": {"Privacy Policy": "https://support.microsoft.com/en-us/windows/cortana-and-privacy-47e5856e-3680-d930-22e1-71ec6cdde231"
                },
    "DiDi": {"Driver Terms": "https://img0.didiglobal.com/static/dpubimg/817178249ccdb3de62825ba80bb57bde/index.html"
             },
    "Discord": {"Terms of Service": "https://discord.com/terms",
                "Privacy Policy": "https://discord.com/privacy",
                "Community Guidelines": "https://discord.com/guidelines"
                },
    "Douyin": {"Terms of Service": "https://www.douyin.com/agreements/?id=6773906068725565448",
               "Privacy Policy": "https://www.douyin.com/agreements/?id=6773901168964798477"
               },
    "Ello (not provide service)": {"Terms of Service": "https://ello.co/wtf/policies/terms",
                                    "Privacy Policy": "https://ello.co/wtf/policies/privacy"
                                        },
    "Elsa": {"Terms of Service": "https://elsaspeak.com/en/terms",
             "Privacy Policy": "https://elsaspeak.com/en/privacy"
             },
   # "Facebook": {"Terms of Service": "https://www.facebook.com/legal/terms/plain_text_terms",
   #              "Privacy Policy":"https://mbasic.facebook.com/privacy/policy/printable/#",
   #               "community-guideline":"https://transparency.fb.com/en-gb/policies/community-standards/"
   #            },
    "FindTaxi": {"Terms of Service + Privacy Policy": "https://findtaxi.io/terms_of_service.html"
                },
    "Flickr": {"Terms of Service": "https://www.flickr.com/help/terms",
               "Privacy Policy": "https://www.flickr.com/help/privacy",
               "Community Guidelines": "https://combo.staticflickr.com/ap/build/pdfs/help/en-us/guidelines.pdf"
                },
    "Foodpanda": {"Terms of Service (en)": "https://www.foodpanda.hk/contents/terms-and-conditions.htm",
                  "Privacy Policy (en)": "https://www.foodpanda.hk/contents/privacy.htm",
                  "Terms of Service (zh)": "https://www.foodpanda.hk/zh/contents/terms-and-conditions.htm",
                  "Privacy Policy (zh)": "https://www.foodpanda.hk/zh/contents/privacy.htm"
                  },
    "GoGo Van": {"Terms of Service": "https://www.gogox.com/terms",
                 "Privacy Policy": "https://www.gogox.com/privacy",
                 "Terms of Service (zh)": "https://www.gogox.com/hk/terms",
                 "Privacy Policy (zh)": "https://www.gogox.com/hk/privacy"
                    },
    "Google Assistant": {"Terms of Service": "https://developers.google.com/assistant/community/terms",},
    "Instagram": {
    "Terms of Service(zh)": "https://help.instagram.com/581066165581870/?helpref=hc_fnav",
    "Community Guidelines": "https://help.instagram.com/477434105621119/?helpref=hc_fnav"
},
"Kuaishou": {
    "Terms of Service(en)": "https://www.kwai.com/rest/kibtWwwNode/getTermsService",
    "Privacy Policy(en)": "https://ppg.m.kwai-pro.com/block/n/activity/page/drBgGzPP?hyId=doodle_drBgGzPP&webview=yoda&share_item_type=jimu_drBgGzPP",
    "Community Guidelines(en)": "https://ppg.m.kwai-pro.com/block/n/activity/page/ktCMzneF?hyId=doodle_ktCMzneF&webview=yoda&share_item_type=jimu_ktCMzneF",
    "Terms of Service(zh)": "https://app.m.kuaishou.com/rest/w/cms/detail",
    "Privacy Policy(zh)": "https://app.m.kuaishou.com/rest/w/cms/detail",
    "Community Guidelines(zh)": "https://www.kuaishou.com/norm?tab=community"
},
"Lalamove": {
    "Terms of Service(zh)": "https://www.lalamove.com/zh-hk/terms-and-conditions",
    "Privacy Policy(zh)": "https://www.lalamove.com/zh-hk/privacy-policy",
    "Community Guidelines(zh)": "https://www.lalamove.com/zh-hk/terms-and-conditions",
    "Delivery (zh)": "https://www.lalamove.com/zh-hk/terms-and-conditions",
    "Terms of Service(en)": "https://www.lalamove.com/en-hk/terms-and-conditions",
    "Privacy Policy(en)": "https://www.lalamove.com/en-hk/privacy-policy",
    "Community Guidelines(en)": "https://www.lalamove.com/en-hk/terms-and-conditions",
    "Delivery(en)": "https://www.lalamove.com/en-hk/terms-and-conditions"
},
"Line Taxi": {
    "Privacy Policy": "https://linetaxi.com.tw/privacy-policy",
    "Privacy Policy_driver": "https://linetaxi.com.tw/driver-privacy-policy",
    "Terms_user": "https://linetaxi.com.tw/使用者條款",
    "Privacy Policy_Passagers": "https://linetaxi.com.tw/line-taxi-privacy-policy"
},
"Line": {
    "Terms of Service(en)": "https://terms.line.me/line_terms?lang=en",
    "Privacy Policy(en)": "https://terms.line.me/line_terms?lang=zh-Hant",
    "Terms of Service(zh)": "https://line.me/en/terms/policy/",
    "Privacy Policy(zh)": "https://line.me/zh-hant/terms/policy/"
},
"Linkedin": {
    "User Agreement": "https://www.linkedin.com/legal/user-agreement",
    "Privacy Policy": "https://www.linkedin.com/legal/privacy-policy",
    "Community Guidelines": "https://www.linkedin.com/legal/professional-community-policies"
},
"Meetup": {
    "Terms of Service": "https://help.meetup.com/hc/en-us/articles/360027447252",
    "Privacy Policy": "https://help.meetup.com/hc/en-us/articles/360044422391-Privacy-Policy",
    "Community Guidelines": "https://help.meetup.com/hc/en-us/sections/360000683791-Community-Guidelines"
},
"Meituan": {
    "美团用户服务协议": "https://rules-center.meituan.com/cap-rules-center/api/rules/detail?id=4",
    "美团隐私政策.": "https://rules-center.meituan.com/cap-rules-center/api/rules/detail?id=2"
},
"Mewe": {
    "Terms of Service": "https://mewe.com/terms",
    "Privacy Policy": "https://mewe.com/privacy"
},
"Mycroft": {
    "Terms of Service": "https://mycroft.ai/embed-terms-of-use/",
    "Privacy Policy": "https://mycroft.ai/embed-privacy-policy/"
},
"Myspace": {
    "Terms of Service": "https://myspace.com/pages/terms",
    "Privacy Policy": "https://myspace.com/pages/privacy"
},
"OpenAI": {
    "Terms of Service": "https://openai.com/policies/terms-of-use",
    "Privacy Policy": "https://openai.com/policies/privacy-policy"
},
"Pinterest": {
    "Terms of Service(zh)": "https://policy.pinterest.com/zh-hant/terms-of-service",
    "Privacy Policy(zh)": "https://policy.pinterest.com/zh-hant/privacy-policy",
    "Terms of Service(en)": "https://policy.pinterest.com/en/terms-of-service",
    "Privacy Policy(en)": "https://policy.pinterest.com/en/privacy-policy"
},
"Reddit": {
    "User Agreement": "https://www.redditinc.com/policies/user-agreement",
    "Privacy Policy": "https://www.reddit.com/policies/privacy-policy"
},
"Replika": {
    "Terms of Service": "https://replika.com/legal/terms",
    "Privacy Policy": "https://replika.com/legal/privacy"
},
"Signal": {
    "Terms & Privacy Policy": "https://signal.org/legal/"
},
"Siri": {
    "Privacy": "https://www.apple.com/legal/privacy/data/en/ask-siri-dictation/"
},
"Snapask": {
    "Terms of Service": "https://snapask.com/en-hk/terms",
    "Privacy Policy(zh)": "https://snapask.com/zh-hk/privacy",
    "Privacy Policy(en)": "https://snapask.com/en-hk/privacy",
    "Community Guidelines(tutor)": "https://tutor-handbook.snapask.com/hk/qa#Chapter-0"
},
"Snapchat": {
    "Terms of Service(zh)": "https://snap.com/zh-Hant/terms",
    "Privacy Policy(zh)": "https://values.snap.com/zh-Hant/privacy/privacy-policy",
    "Terms of Service(en)": "https://snap.com/en-US/terms",
    "Privacy Policy(en)": "https://values.snap.com/privacy/privacy-policy?lang=en-US"
},
"Socratic": {
    "Community Guidelines": "https://socratic.org/socratic/the-socratic-model/community-guidelines"
},
"Telegram": {
    "Terms of Service": "https://telegram.org/tos",
    "Privacy Policy": "https://telegram.org/privacy"
},
"Tencent": {
    "Terms of Service(zh)": "https://www.tencent.com/zh-cn/service-agreement.html",
    "Privacy Policy(zh)": "https://www.tencent.com/zh-cn/privacy-policy.html",
    "Terms of Service(en)": "https://www.tencent.com/en-us/service-agreement.html",
    "Privacy Policy(en)": "https://www.tencent.com/en-us/privacy-policy.html"
},
"TikTok": {
    "Terms of Service": "https://www.tiktok.com/legal/page/row/terms-of-service/en",
    "Privacy Policy": "https://www.tiktok.com/legal/page/row/privacy-policy/en",
    "Community Guidelines": "https://www.tiktok.com/community-guidelines/en/",
    "Privacy Policy for Younger Users": "https://www.tiktok.com/legal/page/global/privacy-policy-for-younger-users/en",
    "Cookie Policy": "https://www.tiktok.com/legal/page/global/cookie-policy/en",
    "Copyright Policy": "https://www.tiktok.com/legal/page/global/copyright-policy/en",
    "Law Enforcement": "https://www.tiktok.com/legal/page/global/law-enforcement/en",
    "Open Source": "https://www.tiktok.com/legal/page/global/open-source/en",
    "Virtual Items": "https://www.tiktok.com/legal/page/row/virtual-items/en"
},
"Tumblr": {
    "Terms of Service": "https://www.tumblr.com/policy/en/terms-of-service",
    "Privacy Policy": "https://www.tumblr.com/privacy/en",
    "Community Guidelines": "https://www.tumblr.com/policy/en/community"
},
"Twitch": {
    "Terms of Service": "https://www.twitch.tv/p/en/legal/terms-of-service/",
    "Privacy Policy": "https://www.twitch.tv/p/en/legal/privacy-notice/"
},
"Twitter": {
    "Terms of Service": "https://twitter.com/en/tos",
    "Privacy Policy": "https://twitter.com/en/privacy"
},
"Uber": {
    "Terms of Service(HK zh)": "https://www.uber.com/legal/en/document/?name=general-terms-of-use&country=hong-kong&lang=zh-hk",
    "Privacy Policy(HK zh)": "https://www.uber.com/legal/en/document/?name=privacy-notice&country=hong-kong&lang=zh-hk",
    "Terms of Service(HK en)": "https://www.uber.com/legal/en/document/?name=general-terms-of-use&country=hong-kong&lang=en",
    "Privacy Policy(HK en)": "https://www.uber.com/legal/en/document/?name=privacy-notice&country=hong-kong&lang=en",
    "Terms of Service(US en)": "https://www.uber.com/legal/en/document/?name=general-terms-of-use&country=united-states&lang=en",
    "Privacy Policy(US en)": "https://www.uber.com/legal/en/document/?name=privacy-notice&country=united-states&lang=en"
},
"Vine": {
    "Terms of Service": "https://vine.co/terms",
    "Privacy Policy": "https://vine.co/privacy"
},
"Wechat": {
    "Terms of Service(zh)": "https://www.wechat.com/zh_CN/service_terms.html",
    "Privacy Policy(zh)": "https://www.wechat.com/zh_CN/privacy_policy.html",
    "Acceptable Use Policy(zh)": "https://www.wechat.com/en/acceptable_use_policy.html",
    "Terms of Service(en)": "https://www.wechat.com/en/service_terms.html",
    "Privacy Policy(en)": "https://www.wechat.com/en/privacy_policy.html",
    "Acceptable Use Policy(en)": "https://www.wechat.com/en/acceptable_use_policy.html"
},
"Weixin": {
    "Terms of Service(zh)": "https://weixin.qq.com/cgi-bin/readtemplate?lang=zh_CN&t=weixin_agreement&s=default",
    "Privacy Policy(zh)": "https://weixin.qq.com/cgi-bin/readtemplate?lang=zh_CN&t=weixin_agreement&s=privacy&head=true",
    "Account Usage(zh)": "https://weixin.qq.com/cgi-bin/readtemplate?&t=page/agreement/personal_account&lang=zh_CN",
    "Terms of Service(en)": "https://weixin.qq.com/cgi-bin/readtemplate?lang=en_US&t=weixin_agreement&s=default&cc=CN&head=true",
    "Privacy Policy(en)": "https://weixin.qq.com/cgi-bin/readtemplate?lang=en_US&t=weixin_agreement&s=privacy&cc=CN&head=true",
    "Account Usage(en)": "https://weixin.qq.com/cgi-bin/readtemplate?&t=page/agreement/personal_account&lang=en_US&head=true"
},
"Whatsapp": {
    "Terms of Service(zh)": "https://www.whatsapp.com/legal/terms-of-service/?lang=zh_hk",
    "Privacy Policy(zh)": "https://www.whatsapp.com/legal/terms-of-service?lang=en",
    "Terms of Service(en)": "https://www.whatsapp.com/legal/privacy-policy/?lang=zh_hk",
    "Privacy Policy(en)": "https://www.whatsapp.com/legal/privacy-policy?lang=en"
},
"Writesonic": {
    "Terms of Service": "https://writesonic.com/terms",
    "Privacy Policy": "https://writesonic.com/privacy-policy"
},
"Xiaohongshu": {
    "Terms of Service(zh)": "https://oacontract.xiaohongshu.com/oacontract/v1/contract/findContractContent?id=-1&contractNo=ZXXY20220331001",
    "Privacy Policy(en)": "https://www.xiaohongshu.com/en/privacy_protection",
    "Privacy Policy(zh)": "https://oacontract.xiaohongshu.com/oacontract/v1/contract/findContractContent?id=-1&contractNo=ZXXY20220509001",
    "Community Guidelines(zh)": "https://oacontract.xiaohongshu.com/oacontract/v1/contract/findContractContent?id=-1&contractNo=ZXXY20221213003",
    "Compliant(zh)": "https://oacontract.xiaohongshu.com/oacontract/v1/contract/findContractContent?id=-1&contractNo=ZXXY20230215001",
    "Intellectual Property(en)": "https://www.xiaohongshu.com/en/intellectual_property"
},
"YouChat(anti-spider)": {
    "Terms and conditions": "https://you.com/legal/terms",
    "Privacy Policy": "https://you.com/legal/privacy"
},
"OpenAI": {
    "Terms of Use": "https://openai.com/policies/terms-of-use/",
    "privacy policy": "https://openai.com/policies/privacy-policy/",
    "usage policies": "https://openai.com/policies/usage-policies/",
    "service terms": "https://openai.com/policies/service-terms/"
},
"Gemini": {
    "policy guidelines": "https://gemini.google/policy-guidelines/",
    "terms of service": "https://ai.google.dev/gemini-api/terms"
},
"Claude (anthropic)": {
    "consumer terms": "https://www.anthropic.com/legal/consumer-terms",
    "commercial terms": "https://www.anthropic.com/legal/commercial-terms",
    "usage policy": "https://www.anthropic.com/legal/aup",
    "privacy policy": "https://www.anthropic.com/legal/privacy"
},
"Copilot (Microsoft)": {
    "terms of use": "https://www.microsoft.com/en-us/microsoft-copilot/for-individuals/termsofuse"
},
"DeepSeek": {
    "terms of use": "https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html",
    "privacy policy": "https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html"
},
"perplexity ai": {
    "privacy policy": "https://www.perplexity.ai/hub/legal/privacy-policy",
    "terms of service": "https://www.perplexity.ai/hub/legal/terms-of-service",
    "Acceptable Use Policy": "https://www.perplexity.ai/hub/legal/aup"
},
"You": {
    "terms and condition": "https://you.com/terms",
    "privacy policy": "https://you.com/privacy"
},
"hugging face": {
    "terms of service": "https://huggingface.co/terms-of-service",
    "privacy policy": "https://huggingface.co/privacy",
    "content policy": "https://huggingface.co/content-policy"
}
}





# ---------------------------------------------------------
# DATA PERSISTENCE
# ---------------------------------------------------------
def load_all_targets() -> Dict[str, Dict[str, str]]:
    targets = DEFAULT_TARGETS.copy()
    if os.path.exists(CUSTOM_FILE):
        try:
            with open(CUSTOM_FILE, "r") as f:
                custom = json.load(f)
                for plat, pages in custom.items():
                    if plat in targets:
                        targets[plat].update(pages)
                    else:
                        targets[plat] = pages
        except Exception:
            pass
    return targets

def save_custom_target(platform: str, page_type: str, url: str):
    custom = {}
    if os.path.exists(CUSTOM_FILE):
        try:
            with open(CUSTOM_FILE, "r") as f:
                custom = json.load(f)
        except Exception:
            pass
    
    if platform not in custom:
        custom[platform] = {}
    custom[platform][page_type] = url
    
    with open(CUSTOM_FILE, "w") as f:
        json.dump(custom, f, indent=4)

# ---------------------------------------------------------
# DATA MODELS & UTILITIES
# ---------------------------------------------------------
@dataclass
class Snapshot:
    timestamp: str
    original: str
    status: str
    digest: str

def sanitize_slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\-_.]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "item"

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def yyyymmdd_from_cal(cal: Calendar) -> str:
    ds = cal.get_date()
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(ds, fmt).strftime("%Y%m%d")
        except ValueError:
            pass
    raise ValueError(f"Unrecognized date format: {ds}")

# ---------------------------------------------------------
# WAYBACK CORE LOGIC
# ---------------------------------------------------------
def cdx_list_snapshots(url, from_ts, to_ts, timeout=60):
    params = {
        "url": url, "from": from_ts, "to": to_ts,
        "output": "json", "fl": "timestamp,original,statuscode,digest",
        "filter": "statuscode:200", "collapse": "digest",
    }
    headers = {"User-Agent": "WaybackPolicyScraper/1.0"}
    try:
        r = requests.get(CDX_API, params=params, headers=headers, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if not data or len(data) == 1: return []
        return [Snapshot(row[0], row[1], row[2], row[3]) for row in data[1:]]
    except Exception as e:
        raise RuntimeError(f"CDX failed: {e}")

def wayback_snapshot_url(timestamp: str, original_url: str) -> str:
    return f"{WAYBACK}/{timestamp}id_/{original_url}"

def extract_clean_text(html: str) -> str:
    if Document is not None:
        try:
            doc = Document(html)
            content = doc.summary(html_partial=True)
            text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", content, flags=re.S | re.I)
            text = re.sub(r"<[^>]+>", " ", text)
            return re.sub(r"\n{3,}", "\n\n", text).strip()
        except: pass
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def fetch_snapshot_html(snap_url, timeout=60, retries=5):
    headers = {"User-Agent": "WaybackPolicyScraper/1.0"}
    for attempt in range(retries):
        try:
            r = requests.get(snap_url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.text, {"final_url": r.url, "status_code": r.status_code}
        except (requests.exceptions.RequestException, Exception) as e:
            if attempt < retries - 1:
                sleep_time = (attempt + 1) * 5  # Waits 5s, 10s, 15s...
                time.sleep(sleep_time)
                continue
            else:
                raise e

def save_snapshot(base_out, platform, page_type, snapshot, original_url, html, fetch_meta):
    platform_slug = sanitize_slug(platform)
    page_slug = sanitize_slug(page_type)
    ts_dirname = datetime.strptime(snapshot.timestamp, "%Y%m%d%H%M%S").strftime("%Y%m%d_%H%M%S")

    out_dir = os.path.join(base_out, platform_slug, page_slug, ts_dirname)
    ensure_dir(out_dir)

    # Save the raw HTML as before
    with open(os.path.join(out_dir, "raw.html"), "w", encoding="utf-8") as f:
        f.write(html)
        
    # --- MODIFIED SECTION: Timestamped filename ---
    # Creates a name like "20230510123000.txt"
    txt_filename = f"{snapshot.timestamp}.txt"
    with open(os.path.join(out_dir, txt_filename), "w", encoding="utf-8") as f:
        f.write(extract_clean_text(html))

    clean_url = wayback_snapshot_url(snapshot.timestamp, snapshot.original).replace("id_/", "/")
    
    # Platform-specific mastersheet logic
    mastersheet_name = f"{platform_slug}_mastersheet.csv"
    mastersheet_path = os.path.join(base_out, mastersheet_name)
    file_exists = os.path.isfile(mastersheet_path)
    
    with open(mastersheet_path, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Date Saved", "Platform", "Page Type", "Snapshot Timestamp", "Wayback Link", "Local Path"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists: 
            writer.writeheader()
        writer.writerow({
            "Date Saved": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Platform": platform,
            "Page Type": page_type,
            "Snapshot Timestamp": snapshot.timestamp,
            "Wayback Link": clean_url,
            "Local Path": out_dir
        })

# ---------------------------------------------------------
# GUI CLASS
# ---------------------------------------------------------
class WaybackGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Wayback Policy Scraper Pro")
        self.geometry("1150x900")
        
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.left = ctk.CTkScrollableFrame(self)
        self.left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.right = ctk.CTkFrame(self)
        self.right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.all_targets = load_all_targets()
        self._setup_left_widgets()
        self._setup_right_widgets()

    def _setup_left_widgets(self):
        # --- UI STYLING FOR CALENDAR ---
        style = ctk.get_appearance_mode()
        
        # Date Selection Container
        date_fr = ctk.CTkFrame(self.left)
        date_fr.pack(fill="x", padx=10, pady=10)

        def create_cal_section(parent, title):
            container = ctk.CTkFrame(parent, fg_color="transparent")
            container.pack(side="left", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(container, text=title, font=("", 13, "bold")).pack()
            
            # Use date_pattern='mm/dd/yyyy' to force 4-digit years
            cal = Calendar(
                container, 
                selectmode="day", 
                showweeknumbers=False,
                headersmode="dropdown", 
                date_pattern="mm/dd/yyyy",
                background="#ffffff",
                foreground="black",
                headersbackground="#e0e0e0",
                headersforeground="black",
                selectbackground="#1f538d",
                selectforeground="red",
                normalforeground="black",
                weekendforeground="black"
            )
            cal.pack(pady=5)

            # Selection Display Box (Now matches mm/dd/yyyy)
            display_lbl = ctk.CTkLabel(container, text=f"Selected: {cal.get_date()}", 
                                      font=("", 11, "italic"), text_color="#1f538d")
            display_lbl.pack()

            # Manual Jump Section
            jump_fr = ctk.CTkFrame(container, fg_color="transparent")
            jump_fr.pack(fill="x", pady=5)
            
            # Placeholder updated to mm/dd/yyyy
            entry = ctk.CTkEntry(jump_fr, placeholder_text="MM/DD/YYYY", height=28)
            entry.pack(side="left", padx=(0, 5), expand=True, fill="x")

            def jump_to_date():
                raw = entry.get().strip()
                # Prioritize mm/dd/yyyy parsing
                for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%Y%m%d"):
                    try:
                        dt = datetime.strptime(raw, fmt)
                        cal.selection_set(dt)
                        display_lbl.configure(text=f"Selected: {cal.get_date()}")
                        return
                    except ValueError:
                        continue
                messagebox.showwarning("Format Error", "Please use MM/DD/YYYY")

            jump_btn = ctk.CTkButton(jump_fr, text="Jump", width=50, height=28, command=jump_to_date)
            jump_btn.pack(side="right")

            # Update label automatically when user clicks a date
            cal.bind("<<CalendarSelected>>", lambda e: display_lbl.configure(text=f"Selected: {cal.get_date()}"))
            
            return cal

        self.cal_start = create_cal_section(date_fr, "FROM")
        self.cal_end = create_cal_section(date_fr, "TO")

        # Custom Input Section
        add_fr = ctk.CTkFrame(self.left)
        add_fr.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(add_fr, text="Add Custom Target", font=("", 14, "bold")).pack(pady=5)
        self.ent_plat = ctk.CTkEntry(add_fr, placeholder_text="Platform Name")
        self.ent_plat.pack(fill="x", padx=20, pady=2)
        self.ent_type = ctk.CTkEntry(add_fr, placeholder_text="Policy Type (e.g. Terms)")
        self.ent_type.pack(fill="x", padx=20, pady=2)
        self.ent_url = ctk.CTkEntry(add_fr, placeholder_text="Original URL")
        self.ent_url.pack(fill="x", padx=20, pady=2)
        ctk.CTkButton(add_fr, text="Save Target", command=self.add_custom).pack(pady=10)

        # Platform/Policy Selection
        sel_fr = ctk.CTkFrame(self.left)
        sel_fr.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(sel_fr, text="Select One Platform").grid(row=0, column=0)
        self.plat_scroll = ctk.CTkScrollableFrame(sel_fr, height=150)
        self.plat_scroll.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.plat_var = ctk.StringVar()
        
        ctk.CTkLabel(sel_fr, text="Select Policy Types").grid(row=0, column=1)
        self.type_scroll = ctk.CTkScrollableFrame(sel_fr, height=150)
        self.type_scroll.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.type_vars = {}

        self.refresh_selection_lists()

        # Delete Button
        self.del_btn = ctk.CTkButton(sel_fr, text="Delete Selected", fg_color="#A30000", 
                                    hover_color="#7A0000", command=self.delete_selected_action)
        self.del_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Options
        self.out_dir_var = ctk.StringVar(value=os.path.abspath("out"))
        ctk.CTkEntry(self.left, textvariable=self.out_dir_var).pack(fill="x", padx=20, pady=10)
        self.run_btn = ctk.CTkButton(self.left, text="Start Download", command=self.start_run, 
                                    height=50, fg_color="green")
        self.run_btn.pack(fill="x", padx=20, pady=10)

        # In _setup_left_widgets, replace the button section at the bottom:
        button_fr = ctk.CTkFrame(self.left, fg_color="transparent")
        button_fr.pack(fill="x", padx=20, pady=10)

        self.run_btn = ctk.CTkButton(button_fr, text="Start Fresh", command=self.start_run, 
                                    height=50, fg_color="#1f538d")
        self.run_btn.pack(side="left", expand=True, padx=(0, 5))

        self.resume_btn = ctk.CTkButton(button_fr, text="Resume Download", command=self.start_run, 
                                       height=50, fg_color="green")
        self.resume_btn.pack(side="right", expand=True, padx=(5, 0))



    def _setup_right_widgets(self):
        self.status_label = ctk.CTkLabel(self.right, text="Status: Idle", font=("", 16))
        self.status_label.pack(pady=10)
        self.progress = ctk.CTkProgressBar(self.right)
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.set(0)
        self.log = ctk.CTkTextbox(self.right)
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_selection_lists(self):
        for widget in self.plat_scroll.winfo_children(): widget.destroy()
        for widget in self.type_scroll.winfo_children(): widget.destroy()
        
        self.all_targets = load_all_targets()
        platforms = sorted(self.all_targets.keys())
        
        # Reset variable if the platform no longer exists
        if self.plat_var.get() not in platforms and platforms:
            self.plat_var.set(platforms[0])

        for p in platforms:
            ctk.CTkRadioButton(self.plat_scroll, text=p, variable=self.plat_var, value=p, command=self.update_policy_checkboxes).pack(anchor="w")
        
        self.update_policy_checkboxes()

    def update_policy_checkboxes(self):
        # Clear existing checkboxes
        for widget in self.type_scroll.winfo_children(): widget.destroy()
        self.type_vars = {}
        
        plat = self.plat_var.get()
        if plat in self.all_targets:
            for t in sorted(self.all_targets[plat].keys()):
                v = ctk.BooleanVar(value=True)
                self.type_vars[t] = v
                ctk.CTkCheckBox(self.type_scroll, text=t, variable=v).pack(anchor="w")

    def add_custom(self):
        p, t, u = self.ent_plat.get().strip(), self.ent_type.get().strip(), self.ent_url.get().strip()
        if not (p and t and u):
            messagebox.showerror("Error", "Fill all fields")
            return
        save_custom_target(p, t, u)
        self.refresh_selection_lists()
        messagebox.showinfo("Success", f"Added {t} for {p}")

    def delete_selected_action(self):
        plat = self.plat_var.get()
        selected_types = [t for t, v in self.type_vars.items() if v.get()]

        if not plat or not selected_types:
            messagebox.showwarning("Warning", "Select a platform and at least one policy type to delete.")
            return

        confirm = messagebox.askyesno("Confirm", f"Delete {', '.join(selected_types)} from {plat}?")
        if not confirm: return

        # Update JSON file
        if os.path.exists(CUSTOM_FILE):
            try:
                with open(CUSTOM_FILE, "r") as f:
                    custom = json.load(f)
                if plat in custom:
                    for t in selected_types:
                        if t in custom[plat]: del custom[plat][t]
                    if not custom[plat]: del custom[plat]
                    with open(CUSTOM_FILE, "w") as f:
                        json.dump(custom, f, indent=4)
            except: pass

        # Update local targets (handles session removal for defaults too)
        if plat in self.all_targets:
            for t in selected_types:
                if t in self.all_targets[plat]: del self.all_targets[plat][t]
            if not self.all_targets[plat]: del self.all_targets[plat]

        self.refresh_selection_lists()
        messagebox.showinfo("Done", "Deleted successfully.")

    def start_run(self):
        plat = self.plat_var.get()
        selected_types = [t for t, v in self.type_vars.items() if v.get()]
        if not plat or not selected_types:
            messagebox.showerror("Error", "Select a platform and at least one policy type")
            return

        from_ts = yyyymmdd_from_cal(self.cal_start)
        to_ts = yyyymmdd_from_cal(self.cal_end)

        # --- DATE VALIDATION ---
        if int(from_ts) > int(to_ts):
            messagebox.showerror("Date Error", "The 'From' date cannot be after the 'To' date.")
            return

        out_dir = self.out_dir_var.get()
        self.run_btn.configure(state="disabled")
        self.log.delete("0.0", "end")

        def worker():
            try:
                tasks = []
                for t in selected_types:
                    if t in self.all_targets[plat]:
                        url = self.all_targets[plat][t]
                        self.log.insert("end", f"Searching {t}...\n")
                        snaps = cdx_list_snapshots(url, from_ts, to_ts)
                        for s in snaps: 
                            tasks.append((plat, t, url, s))

                total = len(tasks)
                if total == 0:
                    self.log.insert("end", "No snapshots found.\n")
                    self.status_label.configure(text="Idle")
                    return

                skipped = 0
                for i, (p, t, u, s) in enumerate(tasks, 1):
                    # --- RESUME LOGIC: Check if folder exists ---
                    platform_slug = sanitize_slug(p)
                    page_slug = sanitize_slug(t)
                    ts_dirname = datetime.strptime(s.timestamp, "%Y%m%d%H%M%S").strftime("%Y%m%d_%H%M%S")
                    check_path = os.path.join(out_dir, platform_slug, page_slug, ts_dirname)

                    if os.path.exists(check_path):
                        skipped += 1
                        self.progress.set(i/total)
                        continue

                    self.status_label.configure(text=f"Downloading {i}/{total}")
                    self.progress.set(i/total)
                    
                    # Added a small 2-second sleep to prevent "Connection Refused"
                    time.sleep(2) 
                    
                    html, meta = fetch_snapshot_html(wayback_snapshot_url(s.timestamp, s.original))
                    save_snapshot(out_dir, p, t, s, u, html, meta)
                    self.log.insert("end", f"Saved: {p} {t} ({s.timestamp})\n")
                
                self.log.insert("end", f"Done! (Processed {total}, Skipped {skipped})\n")
                self.status_label.configure(text="Finished ✅")
            except Exception as e:
                self.log.insert("end", f"CRITICAL ERROR: {e}\n")
                self.status_label.configure(text="Stopped (Error)")
            finally:
                self.run_btn.configure(state="normal")
                self.resume_btn.configure(state="normal")

if __name__ == "__main__":
    WaybackGUI().mainloop()