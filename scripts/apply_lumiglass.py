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

# Стартовый экран
styles = PROJECT / "TMessagesProj/src/main/res/values/styles.xml"
content = styles.read_text(encoding="utf-8")

content = content.replace(
    '<item name="android:colorBackground">@android:color/white</item>',
    '<item name="android:colorBackground">#100D12</item>',
    1
)
content = content.replace(
    '<item name="android:windowBackground">@android:color/white</item>',
    '<item name="android:windowBackground">#100D12</item>',
    1
)

old = '<item name="android:background">#ff527da3</item>'
if old not in content:
    raise SystemExit("Start screen accent not found")

content = content.replace(
    old,
    '<item name="android:background">#FF792F4A</item>',
    1
)
styles.write_text(content, encoding="utf-8")

# Палитра LumiGlass
colors = PROJECT / "TMessagesProj/src/main/res/values/colors.xml"
content = colors.read_text(encoding="utf-8")

block = """
    <!-- LumiGlass palette -->
    <color name="lumi_bg">#100D12</color>
    <color name="lumi_surface">#211923</color>
    <color name="lumi_surface_light">#30232F</color>
    <color name="lumi_ruby">#A52A50</color>
    <color name="lumi_ruby_light">#D65378</color>
    <color name="lumi_text">#FFFFFF</color>
    <color name="lumi_text_secondary">#B9AFB8</color>
    <color name="lumi_glass_border">#55FFFFFF</color>
"""

content = re.sub(
    r"\s*<!-- LumiGlass palette -->.*?<!-- /LumiGlass palette -->",
    "",
    content,
    flags=re.S
)

block = block.replace(
    "    <!-- LumiGlass palette -->",
    "    <!-- LumiGlass palette -->"
).rstrip() + "\n    <!-- /LumiGlass palette -->\n"

content = content.replace("</resources>", block + "</resources>")
colors.write_text(content, encoding="utf-8")

print("LumiGlass: base palette configured")
