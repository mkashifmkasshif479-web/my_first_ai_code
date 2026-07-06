"""
YouTube Title Generator
-----------------------
Kisi bhi YouTube video URL se uska original title nikaal kar,
usse kai catchy / SEO-friendly title suggestions banata hai.

Requirement: sirf 'requests' library chahiye (pip install requests)
Koi YouTube API key ki zaroorat NAHI hai (oEmbed endpoint use kiya hai).

Run karne ka tarika:
    python3 youtube_title_generator.py
"""

import re
import random
import requests


# ---------- Step 1: URL se Video ID nikaalna ----------
def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",   # normal + shorts + embed
        r"youtu\.be\/([0-9A-Za-z_-]{11})",   # short links
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Video ID nahi mil paya. URL sahi hai kya check karo.")


# ---------- Step 2: oEmbed se video ka original title fetch karna ----------
def get_video_title(video_id: str) -> str:
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    response = requests.get(oembed_url, timeout=10)
    if response.status_code != 200:
        raise ValueError("Video ka data nahi mil paya. Video private/deleted ho sakta hai.")
    data = response.json()
    return data.get("title", "")


# ---------- Step 3: Catchy title variations generate karna ----------
POWER_WORDS = [
    "INSANE", "SHOCKING", "UNSTOPPABLE", "ULTIMATE", "SECRET",
    "PRO", "GODLIKE", "SAVAGE", "EPIC", "DEADLY", "LEGENDARY"
]

EMOJIS = ["🔥", "😱", "💀", "⚡", "🎯", "🏆", "👑", "💯"]

TEMPLATES = [
    "{emoji} {power} {title} {emoji}",
    "{title} - {power} Gameplay {emoji}",
    "This {title} Will SHOCK You {emoji}",
    "{power} {title}?? You Won't Believe This {emoji}",
    "How I Did {title} ({power} Method) {emoji}",
    "{title} | {power} Moments Compilation {emoji}",
    "I Tried {title} And This Happened {emoji}",
    "{power} {title} - Full Breakdown {emoji}",
    "Nobody Expected {title} To Go This Way {emoji}",
    "{title} Explained In {power} Detail {emoji}",
]


def clean_title(raw_title: str) -> str:
    # Extra emoji/symbols hata kar plain text nikaalna, taaki naye templates lagayein
    cleaned = re.sub(r"[^\w\s]", "", raw_title)
    return cleaned.strip()


def generate_titles(original_title: str, count: int = 8):
    base = clean_title(original_title)
    if not base:
        base = original_title

    suggestions = set()
    attempts = 0
    while len(suggestions) < count and attempts < count * 5:
        attempts += 1
        template = random.choice(TEMPLATES)
        title = template.format(
            title=base,
            power=random.choice(POWER_WORDS),
            emoji=random.choice(EMOJIS),
        )
        # YouTube title limit ~100 characters
        title = title[:100].strip()
        suggestions.add(title)

    return list(suggestions)


# ---------- Main Program ----------
def main():
    url = input("YouTube video ka URL daalo: ").strip()

    try:
        video_id = extract_video_id(url)
        original_title = get_video_title(video_id)
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"\nOriginal Title: {original_title}\n")
    print("Yeh raha kuch acche title suggestions:\n")

    suggestions = generate_titles(original_title, count=8)
    for i, title in enumerate(suggestions, start=1):
        print(f"{i}. {title}")


if __name__ == "__main__":
    main()
