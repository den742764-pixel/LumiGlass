from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "telegram-src"

if not PROJECT.exists():
    raise SystemExit("Telegram source folder not found")


def replace_once(content, old, new, error):
    if old not in content:
        if new in content:
            return content
        raise SystemExit(error)
    return content.replace(old, new, 1)


# --------------------------------------------------
# Название приложения
# --------------------------------------------------

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


# --------------------------------------------------
# Стартовый экран
# --------------------------------------------------

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
new = '<item name="android:background">#FF792F4A</item>'

if old in content:
    content = content.replace(old, new, 1)
elif new not in content:
    raise SystemExit("Start screen accent not found")

styles.write_text(content, encoding="utf-8")


# --------------------------------------------------
# Палитра LumiGlass
# --------------------------------------------------

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


# --------------------------------------------------
# Стеклянные карточки списка чатов
# --------------------------------------------------

dialog_cell = PROJECT / (
    "TMessagesProj/src/main/java/org/telegram/ui/Cells/DialogCell.java"
)

content = dialog_cell.read_text(encoding="utf-8")

field_anchor = "    protected float translationX;\n"

fields = """    protected float translationX;

    // LumiGlass chat card paints
    private final Paint lumiCardPaint =
            new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint lumiCardBorderPaint =
            new Paint(Paint.ANTI_ALIAS_FLAG);
"""

if "LumiGlass chat card paints" not in content:
    content = replace_once(
        content,
        field_anchor,
        fields,
        "DialogCell field anchor not found"
    )

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

        canvas.drawRoundRect(
                rect, dp(16), dp(16), lumiCardPaint
        );

        lumiCardBorderPaint.setStyle(Paint.Style.STROKE);
        lumiCardBorderPaint.setStrokeWidth(dp(1));
        lumiCardBorderPaint.setColor(0x55FFFFFF);

        canvas.drawRoundRect(
                rect, dp(16), dp(16), lumiCardBorderPaint
        );

        float cornersRadius = dp(8) * cornerProgress;
"""

if "LumiGlass rounded chat card" not in content:
    content = replace_once(
        content,
        draw_anchor,
        draw_code,
        "DialogCell drawing anchor not found"
    )

dialog_cell.write_text(content, encoding="utf-8")


# --------------------------------------------------
# Исправление поиска контактов
# --------------------------------------------------

search_adapter = PROJECT / (
    "TMessagesProj/src/main/java/org/telegram/ui/Adapters/SearchAdapter.java"
)

content = search_adapter.read_text(encoding="utf-8")

old_search = """                if (allUnregistredContacts == null) {
                    allUnregistredContacts = new ArrayList<>();
                    for (ContactsController.Contact contact : ContactsController.getInstance(currentAccount).phoneBookContacts) {
                        ContactEntry contactEntry = new ContactEntry();
                        contactEntry.contact = contact;
                        contactEntry.q1 = (contact.first_name + " " + contact.last_name).toLowerCase();
                        contactEntry.q2 = (contact.last_name + " " + contact.first_name).toLowerCase();
                        allUnregistredContacts.add(contactEntry);
                    }
                }
                for (int i = 0; i < allUnregistredContacts.size(); i++) {
                    ContactEntry contact = allUnregistredContacts.get(i);
                    if ((search2 != null && (contact.q1.toLowerCase().contains(search2) || contact.q1.toLowerCase().contains(search2))) || contact.q1.toLowerCase().contains(search1) || contact.q1.toLowerCase().contains(search1)) {
                        unregistredContacts.add(contact.contact);
                    }
                }
"""

new_search = """                // Rebuild the phonebook cache on every search.
                // This keeps results current after Telegram contact sync.
                allUnregistredContacts = new ArrayList<>();

                for (ContactsController.Contact phoneContact :
                        ContactsController.getInstance(currentAccount).phoneBookContacts) {

                    ContactEntry entry = new ContactEntry();
                    entry.contact = phoneContact;

                    String first = phoneContact.first_name == null
                            ? "" : phoneContact.first_name.trim();

                    String last = phoneContact.last_name == null
                            ? "" : phoneContact.last_name.trim();

                    entry.q1 = (first + " " + last).trim().toLowerCase();
                    entry.q2 = (last + " " + first).trim().toLowerCase();

                    allUnregistredContacts.add(entry);
                }

                // Digits typed by the user. Phone matching is limited
                // to numbers already present in the user's own phonebook.
                String searchDigits = search1.replaceAll("[^0-9]", "");

                for (int i = 0; i < allUnregistredContacts.size(); i++) {
                    ContactEntry entry = allUnregistredContacts.get(i);

                    boolean nameMatches =
                            (!entry.q1.isEmpty() && entry.q1.contains(search1))
                            || (!entry.q2.isEmpty() && entry.q2.contains(search1));

                    if (!nameMatches && search2 != null) {
                        nameMatches =
                                (!entry.q1.isEmpty() && entry.q1.contains(search2))
                                || (!entry.q2.isEmpty() && entry.q2.contains(search2));
                    }

                    boolean phoneMatches = false;

                    if (searchDigits.length() >= 5) {
                        for (String phone : entry.contact.phones) {
                            if (phone == null) {
                                continue;
                            }

                            String phoneDigits = phone.replaceAll("[^0-9]", "");

                            if (phoneDigits.equals(searchDigits)
                                    || phoneDigits.endsWith(searchDigits)
                                    || searchDigits.endsWith(phoneDigits)
                                        && phoneDigits.length() >= 7) {
                                phoneMatches = true;
                                break;
                            }
                        }

                        if (!phoneMatches) {
                            for (String phone : entry.contact.shortPhones) {
                                if (phone == null) {
                                    continue;
                                }

                                String phoneDigits = phone.replaceAll("[^0-9]", "");

                                if (phoneDigits.equals(searchDigits)
                                        || phoneDigits.endsWith(searchDigits)
                                        || searchDigits.endsWith(phoneDigits)
                                            && phoneDigits.length() >= 7) {
                                    phoneMatches = true;
                                    break;
                                }
                            }
                        }
                    }

                    if (nameMatches || phoneMatches) {
                        unregistredContacts.add(entry.contact);
                    }
                }
"""

content = replace_once(
    content,
    old_search,
    new_search,
    "SearchAdapter phonebook search block not found; source version may have changed"
)

search_adapter.write_text(content, encoding="utf-8")


# --------------------------------------------------
# Нижняя панель LumiGlass
# --------------------------------------------------

tabs_layout = PROJECT / (
    "TMessagesProj/src/main/java/org/telegram/ui/MainTabsLayout.java"
)

content = tabs_layout.read_text(encoding="utf-8")


# Импорт порога движения пальца

if "import android.view.ViewConfiguration;" not in content:
    content = replace_once(
        content,
        "import android.view.ViewGroup;\n",
        "import android.view.ViewGroup;\n"
        "import android.view.ViewConfiguration;\n",
        "Could not add ViewConfiguration import"
    )


# Рубиновое заполнение капсулы

old = (
    "selectorPaint.setColor(Theme.multAlpha("
    "Theme.getColor(Theme.key_glass_tabSelected, resourcesProvider), "
    "0.09f));"
)

new = "selectorPaint.setColor(Theme.multAlpha(0xFFA52A50, 0.28f));"

if old in content:
    content = content.replace(old, new, 1)
elif new not in content:
    raise SystemExit("Capsule fill anchor not found")


# Контур капсулы

paint_anchor = (
    "    final Paint selectorPaint = "
    "new Paint(Paint.ANTI_ALIAS_FLAG);\n"
)

paint_code = paint_anchor + (
    "    final Paint selectorBorderPaint = "
    "new Paint(Paint.ANTI_ALIAS_FLAG);\n"
)

if "selectorBorderPaint" not in content:
    content = replace_once(
        content,
        paint_anchor,
        paint_code,
        "Capsule paint anchor not found"
    )


# Отрисовка стеклянной капсулы

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
                    radius, radius, selectorBorderPaint);
"""

if "selectorBorderPaint.setStyle" not in content:
    content = replace_once(
        content,
        draw_anchor,
        draw_code,
        "Capsule drawing anchor not found"
    )


# --------------------------------------------------
# Настоящий свайп без удерживания
# --------------------------------------------------

gesture_fields = """    // LumiGlass immediate horizontal swipe
    private boolean lumiTrackingTouch;
    private boolean lumiDraggingTouch;
    private float lumiDownX;
    private float lumiDownY;
    private float lumiLastX;
    private float lumiLastY;
    private int lumiTouchSlop;
"""

if "LumiGlass immediate horizontal swipe" not in content:
    content = replace_once(
        content,
        "    private boolean isInLongPress;\n",
        gesture_fields + "\n    private boolean isInLongPress;\n",
        "Could not add LumiGlass gesture fields"
    )


# Инициализация порога движения

constructor_anchor = """        super(context);
        this.resourcesProvider = resourcesProvider;
"""

constructor_code = """        super(context);
        this.resourcesProvider = resourcesProvider;
        lumiTouchSlop = ViewConfiguration.get(context)
                .getScaledTouchSlop();
"""

content = replace_once(
    content,
    constructor_anchor,
    constructor_code,
    "MainTabsLayout constructor anchor not found"
)


# Горизонтальный свайп начинает перемещать капсулу
# сразу после обычного системного порога движения пальца.

old_dispatch = """    @Override
    public boolean dispatchTouchEvent(MotionEvent ev) {
        clickHelper.onTouchEvent(this, ev);
        return super.dispatchTouchEvent(ev);
    }
"""

new_dispatch = """    @Override
    public boolean dispatchTouchEvent(MotionEvent ev) {
        final int action = ev.getActionMasked();

        if (action == MotionEvent.ACTION_DOWN) {
            lumiTrackingTouch = true;
            lumiDraggingTouch = false;
            lumiDownX = ev.getX();
            lumiDownY = ev.getY();
            lumiLastX = lumiDownX;
            lumiLastY = lumiDownY;

            return super.dispatchTouchEvent(ev);
        }

        if (!lumiTrackingTouch) {
            return super.dispatchTouchEvent(ev);
        }

        if (action == MotionEvent.ACTION_MOVE) {
            final float x = ev.getX();
            final float y = ev.getY();
            lumiLastX = x;
            lumiLastY = y;

            if (!lumiDraggingTouch) {
                final float dx = x - lumiDownX;
                final float dy = y - lumiDownY;

                if (Math.abs(dx) > lumiTouchSlop
                        && Math.abs(dx) > Math.abs(dy)) {

                    lumiDraggingTouch = true;

                    MotionEvent cancel = MotionEvent.obtain(ev);
                    cancel.setAction(MotionEvent.ACTION_CANCEL);
                    super.dispatchTouchEvent(cancel);
                    cancel.recycle();

                    AndroidUtilities.cancelRunOnUIThread(
                            restoreDrawSelector
                    );

                    setSkipDrawSelector(true);
                    checkLongMove(
                            lumiDownX, lumiDownY, true, false
                    );
                    checkLongMove(x, y, false, false);

                    invalidate();
                    return true;
                }

                return super.dispatchTouchEvent(ev);
            }

            checkLongMove(x, y, false, false);
            invalidate();
            return true;
        }

        if (action == MotionEvent.ACTION_UP) {
            if (lumiDraggingTouch) {
                checkLongMove(
                        ev.getX(), ev.getY(), false, true
                );

                lumiTrackingTouch = false;
                lumiDraggingTouch = false;

                AndroidUtilities.runOnUIThread(
                        restoreDrawSelector, 250
                );

                if (lastLongSelectedView != null) {
                    lastLongSelectedView.performClick();
                }

                lastLongSelectedView = null;
                invalidate();
                return true;
            }

            lumiTrackingTouch = false;
            return super.dispatchTouchEvent(ev);
        }

        if (action == MotionEvent.ACTION_CANCEL) {
            if (lumiDraggingTouch) {
                checkLongMove(
                        lumiLastX, lumiLastY, false, true
                );

                AndroidUtilities.runOnUIThread(
                        restoreDrawSelector, 250
                );

                lastLongSelectedView = null;
                invalidate();
            }

            lumiTrackingTouch = false;
            lumiDraggingTouch = false;
            return super.dispatchTouchEvent(ev);
        }

        if (lumiDraggingTouch) {
            return true;
        }

        return super.dispatchTouchEvent(ev);
    }
"""

content = replace_once(
    content,
    old_dispatch,
    new_dispatch,
    "MainTabsLayout dispatchTouchEvent anchor not found"
)

tabs_layout.write_text(content, encoding="utf-8")


# --------------------------------------------------
# Готово
# --------------------------------------------------

print(
    "LumiGlass: palette, chat cards, contact name/phone search, "
    "ruby glass capsule and immediate swipe navigation configured"
)
