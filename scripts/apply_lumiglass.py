#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LumiGlass — Telegram Android customization script.
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "telegram-src"

if not PROJECT.is_dir():
    raise SystemExit(
        "ERROR: telegram-src folder not found."
    )


def read_file(relative_path):
    path = PROJECT / relative_path
    if not path.is_file():
        raise SystemExit(f"ERROR: source file not found: {path}")
    return path, path.read_text(encoding="utf-8")


def write_file(path, content):
    path.write_text(content, encoding="utf-8")


def replace_required(content, old, new, description):
    if new in content:
        return content
    if old not in content:
        raise SystemExit(
            f"ERROR: cannot find source anchor: {description}"
        )
    return content.replace(old, new, 1)


def replace_in_style(content, style_name, replacements):
    pattern = (
        r'(<style\s+name="' + re.escape(style_name) +
        r'"[^>]*>)(.*?)(</style>)'
    )
    match = re.search(pattern, content, flags=re.S)

    if not match:
        raise SystemExit(f"ERROR: style not found: {style_name}")

    body = match.group(2)

    for old, new in replacements:
        if new in body:
            continue
        if old not in body:
            raise SystemExit(
                f"ERROR: style item not found in {style_name}: {old}"
            )
        body = body.replace(old, new, 1)

    return content[:match.start(2)] + body + content[match.end(2):]
# ============================================================
# 1. APP NAME + ANDROID MANIFEST MERGE
# ============================================================

path, content = read_file(
    "TMessagesProj/src/main/AndroidManifest.xml"
)

if not re.search(
    r'<manifest\b[^>]*\bxmlns:tools\s*=',
    content,
    flags=re.S
):
    content = re.sub(
        r'(<manifest\b)',
        r'\1 xmlns:tools="http://schemas.android.com/tools"',
        content,
        count=1
    )

match = re.search(r"<application\b[^>]*>", content, flags=re.S)

if not match:
    raise SystemExit("ERROR: Android application tag not found")

application_tag = match.group(0)

if re.search(r'\bandroid:label\s*=', application_tag):
    application_tag = re.sub(
        r'android:label\s*=\s*"[^"]*"',
        'android:label="LumiGlass"',
        application_tag,
        count=1
    )
else:
    application_tag = (
        application_tag[:-1] +
        ' android:label="LumiGlass">'
    )

replace_match = re.search(
    r'\btools:replace\s*=\s*"([^"]*)"',
    application_tag
)

if replace_match:
    attributes = [
        item.strip()
        for item in replace_match.group(1).split(",")
        if item.strip()
    ]

    if "android:label" not in attributes:
        attributes.append("android:label")

    replacement = 'tools:replace="' + ",".join(attributes) + '"'

    application_tag = re.sub(
        r'\btools:replace\s*=\s*"[^"]*"',
        replacement,
        application_tag,
        count=1
    )
else:
    application_tag = (
        application_tag[:-1] +
        ' tools:replace="android:label">'
    )

content = (
    content[:match.start()] +
    application_tag +
    content[match.end():]
)

write_file(path, content)


# ============================================================
# 2. STARTUP THEME
# ============================================================
# ============================================================
# 2. STARTUP THEME
# ============================================================

path, content = read_file(
    "TMessagesProj/src/main/res/values/styles.xml"
)

content = replace_in_style(
    content,
    "Theme.TMessages.Start",
    [
        (
            '<item name="android:colorBackground">'
            '@android:color/white</item>',
            '<item name="android:colorBackground">'
            '#100D12</item>'
        ),
        (
            '<item name="android:windowBackground">'
            '@android:color/white</item>',
            '<item name="android:windowBackground">'
            '#100D12</item>'
        ),
    ]
)

old_accent = '<item name="android:background">#ff527da3</item>'
new_accent = '<item name="android:background">#FF792F4A</item>'

if old_accent in content:
    content = content.replace(old_accent, new_accent, 1)
elif new_accent not in content:
    raise SystemExit("ERROR: startup accent color not found")

write_file(path, content)


# ============================================================
# 3. LUMIGLASS COLOR PALETTE
# ============================================================

path, content = read_file(
    "TMessagesProj/src/main/res/values/colors.xml"
)

content = re.sub(
    r'\s*<!-- LumiGlass palette -->.*?'
    r'<!-- /LumiGlass palette -->',
    '',
    content,
    flags=re.S
)

palette = """
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

if "</resources>" not in content:
    raise SystemExit("ERROR: colors.xml has no resources closing tag")

content = content.replace(
    "</resources>",
    palette + "\n</resources>",
    1
)

write_file(path, content)


# ============================================================
# 4. CHAT LIST GLASS CARDS
# ============================================================

path, content = read_file(
    "TMessagesProj/src/main/java/org/telegram/ui/Cells/DialogCell.java"
)

field_anchor = "    protected float translationX;\n"

field_code = """    protected float translationX;

    // LumiGlass card drawing resources.
    private final Paint lumiCardPaint =
            new Paint(Paint.ANTI_ALIAS_FLAG);

    private final Paint lumiCardBorderPaint =
            new Paint(Paint.ANTI_ALIAS_FLAG);

    private final RectF lumiGlassCardRect = new RectF();
"""

if "lumiGlassCardRect" not in content:
    content = replace_required(
        content,
        field_anchor,
        field_code,
        "DialogCell translationX field"
    )

draw_anchor = """        float cornersRadius = dp(8) * cornerProgress;
"""

draw_code = """        // LumiGlass rounded glass card.
        float lumiInsetX = dp(8);
        float lumiInsetY = dp(3);

        lumiGlassCardRect.set(
                lumiInsetX,
                lumiInsetY,
                getMeasuredWidth() - lumiInsetX,
                getMeasuredHeight() - lumiInsetY
        );

        lumiCardPaint.setStyle(Paint.Style.FILL);
        lumiCardPaint.setColor(0xFF211923);

        canvas.drawRoundRect(
                lumiGlassCardRect,
                dp(16),
                dp(16),
                lumiCardPaint
        );

        lumiCardBorderPaint.setStyle(Paint.Style.STROKE);
        lumiCardBorderPaint.setStrokeWidth(dp(1));
        lumiCardBorderPaint.setColor(0x55FFFFFF);

        canvas.drawRoundRect(
                lumiGlassCardRect,
                dp(16),
                dp(16),
                lumiCardBorderPaint
        );

        float cornersRadius = dp(8) * cornerProgress;
"""

if "LumiGlass rounded glass card." not in content:
    content = replace_required(
        content,
        draw_anchor,
        draw_code,
        "DialogCell drawing anchor"
    )

write_file(path, content)


# ============================================================
# 5. RUBY GLASS BOTTOM TAB CAPSULE
# ============================================================

path, content = read_file(
    "TMessagesProj/src/main/java/org/telegram/ui/MainTabsLayout.java"
)

old_color = (
    "selectorPaint.setColor(Theme.multAlpha("
    "Theme.getColor(Theme.key_glass_tabSelected, resourcesProvider), "
    "0.09f));"
)

new_color = (
    "selectorPaint.setColor(Theme.multAlpha(0xFFA52A50, 0.28f));"
)

if old_color in content:
    content = content.replace(old_color, new_color, 1)
elif new_color not in content:
    raise SystemExit("ERROR: tab selector color anchor not found")

paint_anchor = (
    "    final Paint selectorPaint = "
    "new Paint(Paint.ANTI_ALIAS_FLAG);\n"
)

paint_code = paint_anchor + (
    "    final Paint selectorBorderPaint = "
    "new Paint(Paint.ANTI_ALIAS_FLAG);\n"
)

if "selectorBorderPaint" not in content:
    content = replace_required(
        content,
        paint_anchor,
        paint_code,
        "MainTabsLayout selector paint"
    )

draw_anchor = """            canvas.drawRoundRect(
                    x - sWidth / 2f, (getHeight() - sHeight) / 2f,
                    x + sWidth / 2f, (getHeight() + sHeight) / 2f,
                    sHeight / 2f, sHeight / 2f, selectorPaint);
"""

draw_code = """            float left = x - sWidth / 2f;
            float top = (getHeight() - sHeight) / 2f;
            float right = x + sWidth / 2f;
            float bottom = (getHeight() + sHeight) / 2f;
            float radius = sHeight / 2f;

            canvas.drawRoundRect(
                    left, top, right, bottom,
                    radius, radius, selectorPaint);

            selectorBorderPaint.setStyle(Paint.Style.STROKE);
            selectorBorderPaint.setStrokeWidth(dp(1));
            selectorBorderPaint.setColor(0x66FFFFFF);

            canvas.drawRoundRect(
                    left + dp(0.5f),
                    top + dp(0.5f),
                    right - dp(0.5f),
                    bottom - dp(0.5f),
                    radius,
                    radius,
                    selectorBorderPaint);
"""

if "selectorBorderPaint.setStyle" not in content:
    content = replace_required(
        content,
        draw_anchor,
        draw_code,
        "MainTabsLayout selector drawing"
    )

write_file(path, content)


# ============================================================
# 6. GLASS CHAT COMPOSER
# ============================================================

path, content = read_file(
    "TMessagesProj/src/main/java/org/telegram/ui/Components/ChatActivityEnterView.java"
)

composer_anchor = """        textFieldContainer.setPadding(0, dp(1), 0, 0);
"""

composer_code = """        textFieldContainer.setPadding(0, dp(1), 0, 0);

        // LumiGlass: rounded graphite glass surface behind the composer.
        android.graphics.drawable.GradientDrawable lumiComposerBackground =
                new android.graphics.drawable.GradientDrawable();
        lumiComposerBackground.setShape(
                android.graphics.drawable.GradientDrawable.RECTANGLE
        );
        lumiComposerBackground.setColor(0xE6211923);
        lumiComposerBackground.setCornerRadius(dp(22));
        lumiComposerBackground.setStroke(dp(1), 0x66FFFFFF);
        textFieldContainer.setBackground(lumiComposerBackground);
        if (android.os.Build.VERSION.SDK_INT >= 21) {
            textFieldContainer.setElevation(dp(3));
        }
"""

if "LumiGlass: rounded graphite glass surface" not in content:
    content = replace_required(
        content,
        composer_anchor,
        composer_code,
        "Chat composer textFieldContainer padding"
    )

write_file(path, content)


# ============================================================
# 7. PATCH VALIDATION
# ============================================================

checks = {
    "TMessagesProj/src/main/AndroidManifest.xml": [
        'android:label="LumiGlass"'
    ],
    "TMessagesProj/src/main/res/values/colors.xml": [
        'name="lumi_bg"',
        'name="lumi_ruby"',
        'name="lumi_glass_border"'
    ],
    "TMessagesProj/src/main/java/org/telegram/ui/Cells/DialogCell.java": [
        "lumiGlassCardRect",
        "LumiGlass rounded glass card."
    ],
    "TMessagesProj/src/main/java/org/telegram/ui/Components/ChatActivityEnterView.java": [
        "LumiGlass: rounded graphite glass surface",
        "lumiComposerBackground.setCornerRadius(dp(22))"
    ],
    "TMessagesProj/src/main/java/org/telegram/ui/MainTabsLayout.java": [
        "selectorBorderPaint",
        "0xFFA52A50"
    ]
}

for relative_path, markers in checks.items():
    file_path = PROJECT / relative_path

    if not file_path.is_file():
        raise SystemExit(
            f"ERROR: validation file missing: {relative_path}"
        )

    data = file_path.read_text(encoding="utf-8")

    for marker in markers:
        if marker not in data:
            raise SystemExit(
                f"ERROR: validation failed in {relative_path}: {marker}"
            )


print("")
print("LumiGlass patch applied.")
print("App label: LumiGlass")
print("Palette: dark graphite / ruby")
print("Chat list: rounded glass cards")
print("Bottom tabs: ruby glass capsule")
print("Bottom tabs: native Telegram touch handling preserved")
print("Chat composer: rounded graphite glass surface")
print("")
print("Android compilation is performed by GitHub Actions.")
