"""
YouTube Video Viral / Performance Analyzer
--------------------------------------------
Kisi bhi YouTube video ka URL do, ye bata dega:
- Video viral hai ya nahi (views/day ke hisaab se)
- Engagement kaisa hai (likes + comments vs views)
- Views channel ke subscribers se kitne zyada/kam hain
- Title, description, tags ka SEO analysis
- Overall verdict + sudharne ke suggestions

REQUIREMENT:
    pip install yt-dlp

RUN:
    python3 video_viral_analyzer.py
"""

import re
import sys
from datetime import datetime

try:
    import yt_dlp
except ImportError:
    print("yt-dlp install nahi hai. Pehle ye chalao:\n    pip install yt-dlp")
    sys.exit(1)


# ---------------- Data fetch ----------------

def fetch_video_info(url: str) -> dict:
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
    return info


# ---------------- Helper calculations ----------------

def days_since_upload(upload_date_str: str) -> int:
    # upload_date format: YYYYMMDD
    upload_date = datetime.strptime(upload_date_str, "%Y%m%d")
    delta = datetime.now() - upload_date
    return max(delta.days, 1)


def format_number(n):
    if n is None:
        return "N/A"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


# ---------------- Analysis logic ----------------

def analyze_virality(views, days, subscribers):
    views_per_day = views / days

    if views_per_day >= 50_000:
        speed_verdict = "🔥 BOHOT VIRAL — views bahut tezi se aa rahe hain"
    elif views_per_day >= 5_000:
        speed_verdict = "📈 Trending — accha momentum hai"
    elif views_per_day >= 500:
        speed_verdict = "🙂 Normal growth — steady hai par viral nahi"
    else:
        speed_verdict = "😐 Slow — views bahut kam aa rahe hain"

    reach_note = ""
    if subscribers and subscribers > 0:
        ratio = views / subscribers
        if ratio >= 10:
            reach_note = f"Views subscribers se {ratio:.1f}x zyada hain — video subscribers ke bahar bhi phaila hai (ye viral ka strong sign hai) 🚀"
        elif ratio >= 2:
            reach_note = f"Views subscribers se {ratio:.1f}x hain — thoda organic reach mila hai"
        else:
            reach_note = f"Views mostly apne subscribers tak hi limited hain ({ratio:.1f}x) — abhi bahar nahi phaila"

    return views_per_day, speed_verdict, reach_note


def analyze_engagement(views, likes, comments):
    if not views:
        return 0, "Data nahi mila"

    likes = likes or 0
    comments = comments or 0
    engagement_rate = ((likes + comments) / views) * 100

    if engagement_rate >= 8:
        verdict = "🔥 Excellent — log video se bahut jyada interact kar rahe hain"
    elif engagement_rate >= 4:
        verdict = "✅ Good — healthy engagement hai"
    elif engagement_rate >= 1:
        verdict = "🙂 Average — thik-thak hai, aur behtar ho sakta hai"
    else:
        verdict = "⚠️ Low — log dekh to rahe hain par like/comment nahi kar rahe"

    return engagement_rate, verdict


def analyze_title(title: str):
    notes = []
    length = len(title)

    if length < 30:
        notes.append("Title chhota hai (< 30 chars) — thoda aur descriptive/curiosity wala bana sakte ho")
    elif length > 70:
        notes.append("Title thoda lamba hai (> 70 chars) — search results mein cut ho sakta hai")
    else:
        notes.append("Title ki length sahi hai (30-70 chars ka range ideal hota hai)")

    has_number = bool(re.search(r"\d", title))
    has_question = "?" in title
    has_brackets = bool(re.search(r"[\(\[].*[\)\]]", title))
    has_caps_word = bool(re.search(r"\b[A-Z]{3,}\b", title))

    if not (has_number or has_question or has_brackets or has_caps_word):
        notes.append("Title mein koi curiosity hook nahi hai (number, question, [brackets], ya CAPS word try karo)")
    else:
        hooks = []
        if has_number:
            hooks.append("number")
        if has_question:
            hooks.append("question")
        if has_brackets:
            hooks.append("brackets")
        if has_caps_word:
            hooks.append("CAPS word")
        notes.append(f"Title mein hook mila: {', '.join(hooks)} — accha hai")

    return notes


def analyze_description(description: str):
    if not description:
        return ["Description khaali hai — SEO ke liye kam se kam 2-3 lines aur keywords zaroor daalo"]

    length = len(description)
    if length < 100:
        return [f"Description bahut chhota hai ({length} chars) — aur detail add karo, SEO ke liye 250+ chars accha hota hai"]
    return [f"Description ki length thik hai ({length} chars)"]


def analyze_tags(tags):
    if not tags:
        return ["Koi tags nahi lage — kam se kam 5-10 relevant tags add karo, discoverability badhegi"]
    count = len(tags)
    if count < 5:
        return [f"Sirf {count} tags lage hain — aur tags add karo (ideal: 8-15)"]
    return [f"{count} tags lage hain — accha hai"]


# ---------------- Main report ----------------

def print_report(info: dict):
    title = info.get("title", "N/A")
    views = info.get("view_count") or 0
    likes = info.get("like_count") or 0
    comments = info.get("comment_count") or 0
    subscribers = info.get("channel_follower_count")
    upload_date_str = info.get("upload_date")
    description = info.get("description", "")
    tags = info.get("tags") or []
    duration = info.get("duration") or 0

    print("=" * 55)
    print(f"VIDEO: {title}")
    print("=" * 55)

    print(f"\nViews: {format_number(views)}  |  Likes: {format_number(likes)}  |  Comments: {format_number(comments)}")
    if subscribers:
        print(f"Channel Subscribers: {format_number(subscribers)}")
    print(f"Duration: {duration // 60}m {duration % 60}s")

    # Virality
    if upload_date_str:
        days = days_since_upload(upload_date_str)
        views_per_day, speed_verdict, reach_note = analyze_virality(views, days, subscribers)
        print(f"\n--- VIRALITY (Upload ke {days} din baad) ---")
        print(f"Views/day: {format_number(int(views_per_day))}")
        print(speed_verdict)
        if reach_note:
            print(reach_note)
    else:
        print("\n(Upload date nahi mila, virality speed calculate nahi ho payi)")

    # Engagement
    engagement_rate, engagement_verdict = analyze_engagement(views, likes, comments)
    print(f"\n--- ENGAGEMENT ---")
    print(f"Engagement Rate: {engagement_rate:.2f}%")
    print(engagement_verdict)

    # Title
    print(f"\n--- TITLE ANALYSIS ---")
    for note in analyze_title(title):
        print(f"- {note}")

    # Description
    print(f"\n--- DESCRIPTION ANALYSIS ---")
    for note in analyze_description(description):
        print(f"- {note}")

    # Tags
    print(f"\n--- TAGS ANALYSIS ---")
    for note in analyze_tags(tags):
        print(f"- {note}")

    print("\n" + "=" * 55)
    print("FINAL VERDICT")
    print("=" * 55)
    if upload_date_str and views_per_day >= 5000 and engagement_rate >= 4:
        print("✅ Ye video VIRAL trend mein hai — views aur engagement dono strong hain!")
    elif upload_date_str and views_per_day >= 500:
        print("🙂 Ye video normal perform kar rahi hai, viral nahi hai — par content thik hai.")
    else:
        print("⚠️ Ye video abhi viral nahi hui — title/tags/description improve karke retry karo.")


def main():
    url = input("YouTube video ka URL daalo: ").strip()
    print("\nVideo ka data fetch ho raha hai...\n")
    try:
        info = fetch_video_info(url)
    except Exception as e:
        print(f"Error: video ka data nahi mila -> {e}")
        return

    print_report(info)


if __name__ == "__main__":
    main()
