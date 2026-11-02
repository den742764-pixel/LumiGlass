from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "telegram-src"

if not PROJECT.exists():
    raise SystemExit("Telegram source folder not found")

manifest = PROJECT / "TMessagesProj/src/main/AndroidManifest.xml"
if not manifest.exists():
    raise SystemExit("AndroidManifest.xml not found")

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
print("LumiGlass: app name configured")
