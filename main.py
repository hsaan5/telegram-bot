from flask import Flask
from threading import Thread
import os

app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"
def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run).start()
BOT_TOKEN = "8675201793:AAGZDEWD_WSjjQlg68NJBkZ2sxgI6Xb5oDU"
ADMIN_ID = 7262235922

# ============================================
# لا تعدل تحت هذا السطر
# ============================================

import telebot
from telebot import types
import json
BOT_TOKEN = os.getenv("BOT_TOKEN")
import time

DATA_FILE = "servers.json"
USERS_FILE = "users.json"

REQUIRED_CHANNELS = [
    {"id": "@Husseinv5", "name": "قناة حسين",      "url": "https://t.me/Husseinv5"},
    {"id": "@lJ77D",     "name": "القناة الثانية",  "url": "https://t.me/lJ77D"},
    {"id": "@lJ77B",     "name": "القناة الثالثة",  "url": "https://t.me/lJ77B"},
]

bot = telebot.TeleBot(BOT_TOKEN)
USER_STATE = {}
BROADCAST_STATE = {}


# ============================================
# تنسيق مـــلام
# ============================================

def t(text):
    return f"╭─❰ مـــلام ❱─╮\n{text}\n╰─────────────╯"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception:
            return []
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception:
            return []
    return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)


def add_user(uid):
    users = load_users()
    if not isinstance(users, list):
        users = []
    if uid not in users:
        users.append(uid)
        save_users(users)


def flag(code):
    if not code or len(code) != 2:
        return "🌍"
    return "".join(chr(ord(c) + 127397) for c in code.upper())


def is_admin(uid):
    return uid == ADMIN_ID


def get_by(protocol, country):
    data = load_data()
    return [s for s in data if s["protocol"] == protocol and s["country"] == country]


def check_subscription(uid):
    not_joined = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], uid)
            status = member.status
            if hasattr(status, "value"):
                status = status.value
            status = str(status).lower().replace("chatmemberstatus.", "")
            if status not in ["creator", "administrator", "member"]:
                not_joined.append(ch)
        except Exception as e:
            print(f"[SUB-SKIP] {ch['id']}: {e}")
    return not_joined


def send_subscribe_message(chat_id, message_id=None, edit=False):
    text = (
        "🔒 الأشـــتـــراك الإجـــبـــاري\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        "عزيزي،\n"
        "يجب الاشتراك في القنوات\n"
        "لاستخدام البوت:\n\n"
    )
    kb = types.InlineKeyboardMarkup(row_width=1)
    for ch in REQUIRED_CHANNELS:
        text += f"📢 {ch['name']}\n"
        kb.add(types.InlineKeyboardButton(f"اشترك في {ch['name']}", url=ch["url"]))
    kb.add(types.InlineKeyboardButton("✅ تـــم الأشـــتـــراك", callback_data="check_sub"))
    text += "\n━━━━━━━━━━━━━━━━━\nبعد الاشتراك اضغط (تم الاشتراك) 👇"

    final = t(text)

    if edit and message_id:
        try:
            bot.edit_message_text(final, chat_id, message_id, reply_markup=kb)
            return
        except Exception:
            pass
    bot.send_message(chat_id, final, reply_markup=kb)


def user_menu(uid=None):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("VMess 📦", callback_data="user|vmess"),
        types.InlineKeyboardButton("VLESS ⚡", callback_data="user|vless"),
    )
    kb.add(types.InlineKeyboardButton("Trojan 🔒", callback_data="user|trojan"))
    if uid and is_admin(uid):
        kb.add(types.InlineKeyboardButton("🎛️ لـــوحـــة الأدمن", callback_data="open_admin"))
    return kb


def send_main_menu(chat_id, message_id=None, edit=False, uid=None):
    text = (
        "✨ أهـــلاً وســـهـــلاً!\n"
        "━━━━━━━━━━━━━━━━━\n"
        "🤖 بوت سيرفرات V2Ray\n"
        "👇 اختر البروتوكول:"
    )
    final = t(text)
    if edit and message_id:
        try:
            bot.edit_message_text(final, chat_id, message_id, reply_markup=user_menu(uid))
            return
        except Exception:
            pass
    bot.send_message(chat_id, final, reply_markup=user_menu(uid))


def countries_menu(protocol):
    data = load_data()
    kb = types.InlineKeyboardMarkup(row_width=2)
    available = {}
    for s in data:
        if s["protocol"] == protocol:
            c = s["country"]
            available[c] = available.get(c, 0) + 1

    if not available:
        kb.add(types.InlineKeyboardButton("لا توجد سيرفرات", callback_data="noop"))
    else:
        buttons = []
        for country, count in sorted(available.items()):
            label = f"{protocol.upper()} {country} {flag(country)} ({count})"
            buttons.append(types.InlineKeyboardButton(label, callback_data=f"view|{protocol}|{country}"))
        for i in range(0, len(buttons), 2):
            kb.add(*buttons[i:i + 2])

    kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_user"))
    return kb


def admin_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("➕ إضـــافـــة سيرفر", callback_data="admin|add"))
    kb.add(
        types.InlineKeyboardButton("📋 عـــرض السيرفرات", callback_data="admin|list"),
        types.InlineKeyboardButton("📊 الإحـــصـــائـــيـــات", callback_data="admin|stats"),
    )
    kb.add(
        types.InlineKeyboardButton("🗑️ حـــذف سيرفر", callback_data="admin|del"),
        types.InlineKeyboardButton("🗑️ حـــذف الـــكـــل", callback_data="admin|clear"),
    )
    kb.add(types.InlineKeyboardButton("📢 إذاعـــة رســـالـــة", callback_data="admin|broadcast"))
    kb.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة", callback_data="back_user"))
    return kb


def protocol_menu(action):
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("VMess 📦", callback_data=f"{action}|vmess"),
        types.InlineKeyboardButton("VLESS ⚡", callback_data=f"{action}|vless"),
        types.InlineKeyboardButton("Trojan 🔒", callback_data=f"{action}|trojan"),
    )
    kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_admin"))
    return kb


def country_picker(action, protocol):
    kb = types.InlineKeyboardMarkup(row_width=3)
    countries = ["FR", "DE", "US", "GB", "NL", "TR", "CA", "IR", "JP", "SG", "RU", "IN", "AE", "IT", "ES", "PL"]
    btns = [types.InlineKeyboardButton(f"{c} {flag(c)}", callback_data=f"{action}|{protocol}|{c}") for c in countries]
    for i in range(0, len(btns), 3):
        kb.add(*btns[i:i + 3])
    kb.add(types.InlineKeyboardButton("✏️ دولة أخرى", callback_data=f"{action}|{protocol}|OTHER"))
    kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="admin|add"))
    return kb


# ============================================
# الأوامر
# ============================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    uid = message.from_user.id
    add_user(uid)

    if not is_admin(uid):
        not_joined = check_subscription(uid)
        if not_joined:
            send_subscribe_message(message.chat.id)
            return

    send_main_menu(message.chat.id, uid=uid)


@bot.message_handler(commands=['myid'])
def cmd_myid(message):
    bot.reply_to(message, t(f"🆔 معرفك: `{message.from_user.id}`"), parse_mode="Markdown")


@bot.message_handler(func=lambda m: m.from_user.id in USER_STATE, content_types=['text'])
def handle_add_text(message):
    uid = message.from_user.id
    state = USER_STATE.get(uid)
    if not state:
        return

    link = message.text.strip()

    if state.get("waiting_custom_country"):
        country = link.upper()[:2]
        if len(country) != 2 or not country.isalpha():
            bot.reply_to(message, t("❌ رمز دولة غير صحيح\nأرسل مثل: FR أو DE"))
            return
        protocol = state["protocol"]
        saved_link = state["link"]
        data = load_data()
        data.append({"protocol": protocol, "country": country, "link": saved_link})
        save_data(data)
        USER_STATE.pop(uid, None)
        bot.reply_to(
            message,
            t(
                f"✅ تـــم إضـــافـــة السيرفر\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"البروتوكول: {protocol.upper()}\n"
                f"الدولة: {country} {flag(country)}"
            ),
            reply_markup=admin_menu()
        )
        return

    if link.startswith(("vmess://", "vless://", "trojan://")):
        protocol = state["protocol"]
        country = state["country"]
        data = load_data()
        data.append({"protocol": protocol, "country": country, "link": link})
        save_data(data)
        USER_STATE.pop(uid, None)
        bot.reply_to(
            message,
            t(
                f"✅ تـــم إضـــافـــة السيرفر\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"البروتوكول: {protocol.upper()}\n"
                f"الدولة: {country} {flag(country)}\n"
                f"المجموع: {len(data)} سيرفر"
            ),
            reply_markup=admin_menu()
        )
    else:
        bot.reply_to(
            message,
            t(
                "❌ رابط غير صحيح\n"
                "━━━━━━━━━━━━━━━━━\n"
                "يجب أن يبدأ بـ:\n"
                "vmess:// أو vless:// أو trojan://"
            )
        )


@bot.message_handler(func=lambda m: m.from_user.id in BROADCAST_STATE, content_types=['text'])
def handle_broadcast(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    text = message.text
    BROADCAST_STATE.pop(uid, None)
    users = load_users()
    bot.reply_to(message, t(f"📢 جاري الإرسال لـ {len(users)} مستخدم..."))
    success = 0
    fail = 0
    for user_id in users:
        try:
            bot.send_message(user_id, t(text))
            success += 1
            time.sleep(0.05)
        except Exception:
            fail += 1
    bot.send_message(
        message.chat.id,
        t(
            f"✅ تـــم الإرســـال\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"نجح: {success}\n"
            f"فشل: {fail}"
        ),
        reply_markup=admin_menu()
    )


# ============================================
# الأزرار
# ============================================

@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    data = call.data
    uid = call.from_user.id

    if data == "check_sub":
        not_joined = check_subscription(uid)
        if not_joined:
            names = ", ".join([c["name"] for c in not_joined])
            bot.answer_callback_query(call.id, f"❌ لم تشترك في: {names}", show_alert=True)
            send_subscribe_message(call.message.chat.id, call.message.message_id, edit=True)
            return
        bot.answer_callback_query(call.id, "✅ شكراً!", show_alert=True)
        send_main_menu(call.message.chat.id, call.message.message_id, edit=True, uid=uid)
        return

    if not is_admin(uid):
        not_joined = check_subscription(uid)
        if not_joined:
            bot.answer_callback_query(call.id, "❌ اشترك أولاً!", show_alert=True)
            send_subscribe_message(call.message.chat.id, call.message.message_id, edit=True)
            return

    if data == "open_admin":
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "❌ للمشرف فقط")
            return
        try:
            bot.edit_message_text(
                t("🎛️ لـــوحـــة الأدمن\n━━━━━━━━━━━━━━━━━\nاختر عملية:"),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=admin_menu()
            )
        except Exception:
            pass
        return

    if data == "back_user":
        send_main_menu(call.message.chat.id, call.message.message_id, edit=True, uid=uid)
        return

    if data.startswith("user|"):
        protocol = data.split("|")[1]
        try:
            bot.edit_message_text(
                t(f"اختر الدولة لـ {protocol.upper()}:"),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=countries_menu(protocol)
            )
        except Exception:
            pass
        return

    if data.startswith("view|"):
        _, protocol, country = data.split("|")
        servers = get_by(protocol, country)
        if not servers:
            bot.answer_callback_query(call.id, "لا توجد سيرفرات")
            return

        title = f"سيرفرات {protocol.upper()} {country} {flag(country)}\n"
        title += "━━━━━━━━━━━━━━━━━\n"
        text = title
        for i, s in enumerate(servers, 1):
            text += f"\n{i}. `{s['link']}`\n"

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data=f"user|{protocol}"))

        try:
            bot.edit_message_text(
                t(text), call.message.chat.id, call.message.message_id,
                parse_mode="Markdown", reply_markup=kb
            )
        except Exception:
            try:
                bot.edit_message_text(
                    t(title + "الرسالة طويلة، سترسل على دفعات."),
                    call.message.chat.id, call.message.message_id
                )
            except Exception:
                pass
            for i in range(0, len(servers), 3):
                chunk = "\n".join([f"`{s['link']}`" for s in servers[i:i + 3]])
                bot.send_message(call.message.chat.id, t(chunk), parse_mode="Markdown")
            bot.send_message(call.message.chat.id, t("السيرفرات اعلاه"), reply_markup=kb)
        return

    if not is_admin(uid):
        bot.answer_callback_query(call.id, "❌ للمشرف فقط")
        return

    if data == "back_admin":
        try:
            bot.edit_message_text(
                t("🎛️ لـــوحـــة الأدمن\nاختر عملية:"),
                call.message.chat.id, call.message.message_id,
                reply_markup=admin_menu()
            )
        except Exception:
            pass
        return

    if data == "admin|add":
        try:
            bot.edit_message_text(
                t("➕ إضـــافـــة سيرفر\n\nاختر البروتوكول:"),
                call.message.chat.id, call.message.message_id,
                reply_markup=protocol_menu("add")
            )
        except Exception:
            pass
        return

    if data.startswith("add|") and len(data.split("|")) == 2:
        protocol = data.split("|")[1]
        try:
            bot.edit_message_text(
                t(f"اختر الدولة لـ {protocol.upper()}:"),
                call.message.chat.id, call.message.message_id,
                reply_markup=country_picker("addp", protocol)
            )
        except Exception:
            pass
        return

    if data.startswith("addp|"):
        _, protocol, country = data.split("|")
        if country == "OTHER":
            USER_STATE[uid] = {"protocol": protocol, "waiting_custom_country": True, "link": None}
            try:
                bot.edit_message_text(
                    t("📥 أرسل رابط السيرفر أولاً:"),
                    call.message.chat.id, call.message.message_id
                )
            except Exception:
                pass
            return

        USER_STATE[uid] = {"protocol": protocol, "country": country}
        try:
            bot.edit_message_text(
                t(
                    f"📥 الآن أرسل رابط السيرفر\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"البروتوكول: {protocol.upper()}\n"
                    f"الدولة: {country} {flag(country)}"
                ),
                call.message.chat.id, call.message.message_id
            )
        except Exception:
            pass
        return

    if data == "admin|list":
        servers = load_data()
        if not servers:
            bot.answer_callback_query(call.id, "لا توجد سيرفرات")
            return
        groups = {}
        for s in servers:
            key = (s["protocol"], s["country"])
            groups[key] = groups.get(key, 0) + 1
        text = "📋 السيرفرات المحفوظة\n━━━━━━━━━━━━━━━━━\n"
        for (p, c), n in sorted(groups.items()):
            text += f"• {p.upper()} {c} {flag(c)}: {n}\n"
        text += f"\nالمجموع: {len(servers)}"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_admin"))
        try:
            bot.edit_message_text(t(text), call.message.chat.id, call.message.message_id, reply_markup=kb)
        except Exception:
            pass
        return

    if data == "admin|stats":
        users = load_users()
        servers = load_data()
        vmess_count = sum(1 for s in servers if s["protocol"] == "vmess")
        vless_count = sum(1 for s in servers if s["protocol"] == "vless")
        trojan_count = sum(1 for s in servers if s["protocol"] == "trojan")
        countries = {}
        for s in servers:
            countries[s["country"]] = countries.get(s["country"], 0) + 1

        text = (
            "📊 الإحصائيات\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            f"👥 عدد المستخدمين: {len(users)}\n\n"
            f"📦 إجمالي السيرفرات: {len(servers)}\n"
            f"  • VMess: {vmess_count}\n"
            f"  • VLESS: {vless_count}\n"
            f"  • Trojan: {trojan_count}\n\n"
            "🌍 السيرفرات حسب الدولة:\n"
        )
        if countries:
            for c, n in sorted(countries.items(), key=lambda x: -x[1]):
                text += f"  • {c} {flag(c)}: {n}\n"
        else:
            text += "  لا توجد\n"

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_admin"))
        try:
            bot.edit_message_text(t(text), call.message.chat.id, call.message.message_id, reply_markup=kb)
        except Exception:
            pass
        return

    if data == "admin|del":
        servers = load_data()
        if not servers:
            bot.answer_callback_query(call.id, "لا توجد سيرفرات")
            return
        kb = types.InlineKeyboardMarkup(row_width=1)
        for i, s in enumerate(servers):
            label = f"🗑️ {i+1}. {s['protocol'].upper()} {s['country']} {flag(s['country'])}"
            kb.add(types.InlineKeyboardButton(label, callback_data=f"del|{i}"))
        kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_admin"))
        try:
            bot.edit_message_text(
                t("🗑️ اختر سيرفر للحذف:"),
                call.message.chat.id, call.message.message_id,
                reply_markup=kb
            )
        except Exception:
            pass
        return

    if data.startswith("del|"):
        idx = int(data.split("|")[1])
        servers = load_data()
        if 0 <= idx < len(servers):
            removed = servers.pop(idx)
            save_data(servers)
            bot.answer_callback_query(call.id, f"تم حذف {removed['protocol'].upper()} {removed['country']}")
        else:
            bot.answer_callback_query(call.id, "لم يعد موجودا")

        if servers:
            kb = types.InlineKeyboardMarkup(row_width=1)
            for i, s in enumerate(servers):
                label = f"🗑️ {i+1}. {s['protocol'].upper()} {s['country']} {flag(s['country'])}"
                kb.add(types.InlineKeyboardButton(label, callback_data=f"del|{i}"))
            kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_admin"))
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)
            except Exception:
                pass
        else:
            try:
                bot.edit_message_text(t("لا توجد سيرفرات الآن."), call.message.chat.id, call.message.message_id, reply_markup=admin_menu())
            except Exception:
                pass
        return

    if data == "admin|clear":
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("✅ نعم احذف الكل", callback_data="clear|yes"),
            types.InlineKeyboardButton("❌ إلغاء", callback_data="back_admin"),
        )
        try:
            bot.edit_message_text(
                t("⚠️ هل أنت متأكد؟"),
                call.message.chat.id, call.message.message_id,
                reply_markup=kb
            )
        except Exception:
            pass
        return

    if data == "clear|yes":
        save_data([])
        try:
            bot.edit_message_text(
                t("✅ تـــم حـــذف كـــل السيرفرات"),
                call.message.chat.id, call.message.message_id,
                reply_markup=admin_menu()
            )
        except Exception:
            pass
        return

    if data == "admin|broadcast":
        BROADCAST_STATE[uid] = True
        try:
            bot.edit_message_text(
                t("📢 أرسل الرسالة التي تريد إذاعتها:"),
                call.message.chat.id, call.message.message_id
            )
        except Exception:
            pass
        return

    if data == "noop":
        bot.answer_callback_query(call.id)
        return


# ============================================
# التشغيل
# ============================================

if __name__ == "__main__":
    print("=" * 40)
    print("Bot is running...")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"Servers loaded: {len(load_data())}")
    print(f"Users registered: {len(load_users())}")
    print(f"Required channels: {len(REQUIRED_CHANNELS)}")
    print("=" * 40)

    try:
        bot.delete_webhook()
        bot.get_updates(offset=-1)
    except Exception as e:
        print(f"تنبيه: {e}")

    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Starting polling...")
            bot.infinity_polling(none_stop=True, interval=1, timeout=30, skip_pending=True)
        except Exception as e:
            print(f"❌ توقف: {e}")
            print("إعادة التشغيل بعد 5 ثوان...")
            time.sleep(5)
