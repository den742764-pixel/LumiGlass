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

content = re.sub(
    r"\s*<!-- LumiGlass palette -->.*?<!-- /LumiGlass palette -->",
    "",
    content,
    flags=re.S
)

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
    <!-- /LumiGlass palette -->
"""

content = content.replace("</resources>", block + "\n</resources>")
colors.write_text(content, encoding="utf-8")

# Карточки списка чатов LumiGlass
dialog_cell = PROJECT / "TMessagesProj/src/main/java/org/telegram/ui/Cells/DialogCell.java"
content = dialog_cell.read_text(encoding="utf-8")

field_anchor = "    protected float translationX;\n"

fields = """    protected float translationX;

    // LumiGlass chat card paints
    private final Paint lumiCardPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint lumiCardBorderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
"""

if "LumiGlass chat card paints" not in content:
    if field_anchor not in content:
        raise SystemExit("DialogCell field anchor not found")
    content = content.replace(field_anchor, fields, 1)

draw_anchor = """        if (translationX != 0) {
            canvas.save();
            canvas.translate(translationX, 0);
            gtx += translationX;
        }

        float cornersRadius = dp(8) * cornerProgress;
"""

draw_code = """        if (translationX != 0) {
            canvas.save();
            canvas.translate(translationX, 0);
            gtx += translationX;
        }

        // LumiGlass rounded chat card
        float cardInsetX = dp(8);
        float cardInsetY = dp(3);

        rect.set(
            cardInsetX,
            cardInsetY,
            getMeasuredWidth() - cardInsetX,
            getMeasuredHeight() - cardInsetY
        );

        lumiCardPaint.setStyle(Paint.Style.FILL);
        lumiCardPaint.setColor(0xFF211923);
        canvas.drawRoundRect(rect, dp(16), dp(16), lumiCardPaint);

        lumiCardBorderPaint.setStyle(Paint.Style.STROKE);
        lumiCardBorderPaint.setStrokeWidth(dp(1));
        lumiCardBorderPaint.setColor(0x55FFFFFF);
        canvas.drawRoundRect(rect, dp(16), dp(16), lumiCardBorderPaint);

        float cornersRadius = dp(8) * cornerProgress;
"""

if "LumiGlass rounded chat card" not in content:
    if draw_anchor not in content:
        raise SystemExit("DialogCell drawing anchor not found")
    content = content.replace(draw_anchor, draw_code, 1)

dialog_cell.write_text(content, encoding="utf-8")

# Более быстрое перетаскивание нижней капсулы
tabs_layout = PROJECT / "TMessagesProj/src/main/java/org/telegram/ui/MainTabsLayout.java"
content = tabs_layout.read_text(encoding="utf-8")

old = """        public long getLongPressDuration() {
            return ClickHelper.Delegate.super.getLongPressDuration() * 750 / 1000;
        }"""

new = """        public long getLongPressDuration() {
            return 140;
        }"""

if old in content:
    content = content.replace(old, new, 1)
elif new not in content:
    raise SystemExit("MainTabsLayout gesture anchor not found")

tabs_layout.write_text(content, encoding="utf-8")

print("LumiGlass: palette, chat cards and faster tab dragging configured")
