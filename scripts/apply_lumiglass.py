from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "telegram-src"

if not PROJECT.exists():
    raise SystemExit("Telegram source folder not found")

# Название приложения
manifest = PROJECT / "TMessagesProj/src/main/AndroidManifest.xml"
content = manifest.read_text(encoding="utf-8")

content, count = re.subn(
    r"<application\b",
    '<application android:label="LumiGlass"',
    content,
    count=1
)
if count != 1:
    raise SystemExit("Could not set LumiGlass app name")

manifest.write_text(content, encoding="utf-8")

# Цвет стартового экрана
styles = PROJECT / "TMessagesProj/src/main/res/values/styles.xml"
content = styles.read_text(encoding="utf-8")

old = '<item name="android:colorBackground">@android:color/white</item>'
new = '<item name="android:colorBackground">#100D12</item>'

if old not in content:
    raise SystemExit("Start screen background not found")

content = content.replace(old, new, 1)

old = '<item name="android:windowBackground">@android:color/white</item>'
new = '<item name="android:windowBackground">#100D12</item>'

content = content.replace(old, new, 1)

old = '<item name="android:background">#ff527da3</item>'
new = '<item name="android:background">#FF792F4A</item>'

if old not in content:
    raise SystemExit("Start screen accent not found")

content = content.replace(old, new, 1)
styles.write_text(content, encoding="utf-8")

print("LumiGlass: dark start screen configured")
