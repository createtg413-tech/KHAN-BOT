import os
import requests
import random
import time
from telebot import types
import telebot
from flask import Flask
from threading import Thread

# ==========================================
#  ১. আপনার লাইভ কনফিগারেশন ডাটা
# ==========================================
BOT_TOKEN = "8654959462:AAHr_XqPHdniQCxCazjtWFzOj9yUI4bCx6M"
GRIZZLY_API_KEY = "bea0584f29b670bf7647951bf8b9db9a"
ADMIN_ID = 8524193966

CHANNEL_ID = "@HiddenSource2"  
GROUP_ID = "@urkhanvai2"      

bot = telebot.TeleBot(BOT_TOKEN)

# রেন্ডার ফ্রেন্ডলি ইন-মেমোরি ডাটাবেস (ফাইল সিস্টেম ক্র্যাশ করবে না)
MEMORY_DB = {}
GLOBAL_ORDERS = {}

def load_db():
    return MEMORY_DB

def save_db(db):
    global MEMORY_DB
    MEMORY_DB = db

# ==========================================
#  ২. ২৪ ঘণ্টা লাইভ রাখার ওয়েব পিন (Flask - Render Fixed)
# ==========================================
app = Flask('')

@app.route('/')
def home(): 
    return "🔥 Khan Premium Telegram Sniper Engine is Live! 🔥"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive(): 
    Thread(target=run_server, daemon=True).start()

# ==========================================
#  ৩. মেম্বারশিপ চেক (স্মার্ট জয়েনিং লজিক)
# ==========================================
def is_joined_all(user_id):
    if user_id == ADMIN_ID: return True
    try:
        ch_member = bot.get_chat_member(CHANNEL_ID, user_id)
        gr_member = bot.get_chat_member(GROUP_ID, user_id)
        allowed = ['member', 'administrator', 'creator']
        if ch_member.status in allowed and gr_member.status in allowed:
            return True
        return False
    except Exception: return False

# ==========================================
#  ৪. মেইন ড্যাশবোর্ড ইন্টারফেস (Premium Look)
# ==========================================
def send_dashboard(chat_id, user_id):
    db = load_db()
    user_data = db.get(str(user_id), {'balance': 0.05, 'lang': 'en'})
    balance = user_data.get('balance', 0.05)
    lang = user_data.get('lang', 'en')
    
    text = {
        'bn': f"• **خان ওটিপি স্নাইপার (টেলিগ্রাম স্পেশাল)** •\n\n👤 **আপনার আইডি:** `{user_id}`\n💰 **মোট ব্যালেন্স:** {balance:.4f} USDT\n🏆 **রিলিজ র‍্যাঙ্ক:** VIP0",
        'en': f"• **Khan Telegram OTP Sniper** •\n\n👤 **Your ID:** `{user_id}`\n💰 **Total Balance:** {balance:.4f} USDT\n🏆 **Rank:** VIP0"
    }.get(lang, "• **Khan Telegram OTP Sniper** •")
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("💳 Deposit", callback_data="dep_menu"), types.InlineKeyboardButton("🎡 Lucky Spin", callback_data="spin_wheel"))
    markup.row(types.InlineKeyboardButton("👥 Referral (2%)", callback_data="ref_menu"), types.InlineKeyboardButton("💬 Live Support", callback_data="support_chat"))
    
    if user_id == ADMIN_ID:
        markup.row(types.InlineKeyboardButton("👑 Khan Admin Panel", callback_data="admin_panel"))
        
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

# ==========================================
#  ৫. কমান্ড হ্যান্ডলিং (/start)
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text_args = message.text.split()
    
    db = load_db()
    s_user_id = str(user_id)
    
    if s_user_id not in db:
        db[s_user_id] = {'lang': None, 'balance': 0.05, 'referred_by': None, 'last_spin': 0, 'verified': False}
        if len(text_args) > 1 and text_args[1].isdigit():
            referrer = text_args[1]
            if referrer != s_user_id and referrer in db:
                db[s_user_id]['referred_by'] = referrer
        save_db(db)

    if not is_joined_all(user_id) or not db[s_user_id].get('verified', False):
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("📢 Join Main Channel", url="https://t.me/HiddenSource2"))
        markup.row(types.InlineKeyboardButton("💬 Join Support Group", url="https://t.me/urkhanvai2"))
        markup.row(types.InlineKeyboardButton("🔗 External Web Verify (🔒)", url="https://your-verification-link.com"))
        markup.row(types.InlineKeyboardButton("🔄 Verify Me", callback_data="check_all_join"))
        bot.send_message(chat_id, "⚠️ **Access Denied!**\nবট ব্যবহার করতে টাস্কগুলো সম্পন্ন করে নিচের বাটনে চাপ দিন:", reply_markup=markup)
        return

    if db[s_user_id]['lang'] is None:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🇺🇸 English", callback_data="slang_en"), types.InlineKeyboardButton("🇧🇩 বাংলা", callback_data="slang_bn"))
        bot.send_message(chat_id, "✨ **Welcome to Khan VIP Sniper** ✨\n\nSelect Language / ভাষা নির্বাচন করুন:", reply_markup=markup)
    else:
        send_dashboard(chat_id, user_id)

# ==========================================
#  ৬. Admin প্যানেল কমান্ডস
# ==========================================
@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    db = load_db()
    total_users = len(db)
    text = f"👑 **খান ভাই স্পেশাল Admin প্যানেল** 👑\n\n👥 মোট রেজিস্টার্ড ইউজার: {total_users}\n⚡ সক্রিয় ওটিপি সেশন: {len(GLOBAL_ORDERS)}\n\n⚙️ **কমান্ড গাইড:**\n👉 ইউজার ব্যালেন্স দিতে লিখুন:\n`/addbalance ইউজার_আইডি পরিমাণ`"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['addbalance'])
def add_balance_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        _, target_id, amount = message.text.split()
        db = load_db()
        if target_id in db:
            db[target_id]['balance'] += float(amount)
            save_db(db)
            bot.send_message(message.chat.id, f"✅ ইউজার `{target_id}` এর একাউন্টে ${amount} যোগ করা হয়েছে।", parse_mode="Markdown")
            bot.send_message(int(target_id), f"💰 **এডমিন আপনার একাউন্টে ${amount} ক্রেডিট যোগ করেছেন!**")
        else:
            bot.send_message(message.chat.id, "❌ এই আইডির কোনো ইউজার বটে নাই!")
    except Exception:
        bot.send_message(message.chat.id, "❌ ফরম্যাট ভুল! উদাহরণ: `/addbalance 123456 5.0`")

# ==========================================
#  ৭. বাটন ও অ্যাকশন কন্ট্রোলার (Callbacks)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    s_user_id = str(user_id)
    db = load_db()
    
    if call.data == "check_all_join":
        if is_joined_all(user_id):
            db[s_user_id]['verified'] = True
            save_db(db)
            bot.answer_callback_query(call.id, "✅ ভেরিফিকেশন সফল!")
            try:
                bot.delete_message(chat_id, call.message.message_id)
            except Exception: pass
            handle_start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ আপনি এখনো সবগুলো টাস্ক সম্পন্ন করেননি!", show_alert=True)
        return

    if call.data.startswith("slang_"):
        db[s_user_id]['lang'] = call.data.split("_")[1]
        save_db(db)
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception: pass
        send_dashboard(chat_id, user_id)

    elif call.data == "admin_panel":
        if user_id == ADMIN_ID: admin_cmd(call.message)

    elif call.data == "spin_wheel":
        current_time = time.time()
        if current_time - db.get(s_user_id, {}).get('last_spin', 0) < 86400:
            bot.answer_callback_query(call.id, "❌ আজকে অলরেডি স্পিন করেছেন!", show_alert=True)
            return
        win_amount = round(random.uniform(0.002, 0.05), 4)
        db[s_user_id]['balance'] = db.get(s_user_id, {}).get('balance', 0.05) + win_amount
        db[s_user_id]['last_spin'] = current_time
        save_db(db)
        bot.answer_callback_query(call.id, f"🎉 আপনি ${win_amount} ফ্রি বোনাস জিতেছেন!", show_alert=True)
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception: pass
        send_dashboard(chat_id, user_id)

    elif call.data == "ref_menu":
        ref_link = f"https://t.me/KhanSniperBot_YourLink?start={user_id}"
        try:
            bot.edit_message_text(f"👥 **রেফারেল প্রোগ্রাম (২%)**\n\n🔗 **আপনার রেফার লিংক:**\n`{ref_link}`", chat_id, call.message.message_id, parse_mode="Markdown")
        except Exception: pass

    elif call.data == "dep_menu":
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("বিকাশ (bKash)", callback_data="p_bkash"), types.InlineKeyboardButton("নগদ (Nagad)", callback_data="p_nagad"))
        markup.row(types.InlineKeyboardButton("Binance Pay", callback_data="p_binance"), types.InlineKeyboardButton("USDT TRC20", callback_data="p_usdt"))
        try:
            bot.edit_message_text("💳 নম্বরের ওপর চাপ দিলেই অটো-কপি হয়ে যাবে:", chat_id, call.message.message_id, reply_markup=markup)
        except Exception: pass

    elif call.data.startswith("p_"):
        method = call.data.split("_")[1]
        details = {'bkash': '`01948805285`', 'nagad': '`01948805285`', 'usdt': '`TKpCgqq4iEZmbZnF9B4iz6GLNnN9n8eVoV`', 'binance': '`849519589`'}[method]
        try:
            bot.edit_message_text(f"📥 ডিপোজিট করুন:\n\n💰 **ঠিকানা:** {details}\n\nTxID বটের `Live Support`-এ পাঠান।", chat_id, call.message.message_id, parse_mode="Markdown")
        except Exception: pass

    elif call.data == "support_chat":
        msg = bot.send_message(chat_id, "💬 আপনার মেসেজ বা স্ক্রিনশটটি এখানে পাঠান:")
        bot.register_next_step_handler(msg, process_support_msg)

    elif call.data.startswith("claim_"):
        _, order_id, country_id, price_str = call.data.split("_")
        price = float(price_str)
        
        if db.get(s_user_id, {}).get('balance', 0.0) < price:
            bot.answer_callback_query(call.id, "❌ পর্যাপ্ত ব্যালেন্স নেই!", show_alert=True)
            return
        
        if order_id in GLOBAL_ORDERS:
            bot.answer_callback_query(call.id, "❌ অলরেডি অন্য একজন স্নাইপ করে নিয়েছেন।", show_alert=True)
            return
            
        API_URL = f"https://api.grizzlysms.com/stubs/handler_api.php?api_key={GRIZZLY_API_KEY}&action=getNumber&service=tg&country={country_id}"
        
        try:
            res = requests.get(API_URL).text
            if res.startswith("ACCESS_NUMBER"):
                _, api_order_id, phone_number = res.split(":")
                GLOBAL_ORDERS[order_id] = {'user': user_id, 'api_id': api_order_id, 'price': price}
                
                try:
                    bot.edit_message_text(f"🔒 **Number Snipped!**\n👤 Snipped by: `{user_id}`", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
                except Exception: pass
                
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton("🔄 Fetch OTP Code", callback_data=f"fotp_{order_id}"))
                markup.row(types.InlineKeyboardButton("❌ Cancel & Refund", callback_data=f"cncl_{order_id}"))
                bot.send_message(user_id, f"🎯 **স্নাইপ সফল!**\n\n📱 নম্বর: `{phone_number}`\n💵 মূল্য: ${price:.2f} USDT", reply_markup=markup, parse_mode="Markdown")
            else:
                bot.answer_callback_query(call.id, "❌ এপিআই স্টক খালি!", show_alert=True)
        except Exception:
            bot.answer_callback_query(call.id, "❌ কানেকশন এরর!", show_alert=True)

    elif call.data.startswith("fotp_"):
        order_id = call.data.split("_")[1]
        ord_info = GLOBAL_ORDERS.get(order_id)
        
        if not ord_info: return
        STATUS_URL = f"https://api.grizzlysms.com/stubs/handler_api.php?api_key={GRIZZLY_API_KEY}&action=getStatus&id={ord_info['api_id']}"
        
        try:
            res = requests.get(STATUS_URL).text
            if res.startswith("STATUS_OK"):
                code = res.split(":")[1]
                price = ord_info['price']
                
                db[s_user_id]['balance'] = db.get(s_user_id, {}).get('balance', 0.05) - price
                
                referrer = db.get(s_user_id, {}).get('referred_by')
                if referrer and referrer in db:
                    db[referrer]['balance'] = db.get(referrer, {}).get('balance', 0.0) + (price * 0.02)
                save_db(db)
                    
                bot.send_message(chat_id, f"✅ **ওটিপি কোড:** `{code}`", parse_mode="Markdown")
                try:
                    bot.delete_message(chat_id, call.message.message_id)
                except Exception: pass
                if order_id in GLOBAL_ORDERS: del GLOBAL_ORDERS[order_id]
            elif res == "STATUS_WAIT_CODE":
                bot.answer_callback_query(call.id, "⏳ ওটিপি আসেনি! আবার চাপুন।", show_alert=True)
        except Exception: pass

    elif call.data.startswith("cncl_"):
        order_id = call.data.split("_")[1]
        ord_info = GLOBAL_ORDERS.get(order_id)
        if ord_info:
            try:
                requests.get(f"https://api.grizzlysms.com/stubs/handler_api.php?api_key={GRIZZLY_API_KEY}&action=setStatus&status=8&id={ord_info['api_id']}")
            except Exception: pass
            bot.answer_callback_query(call.id, "❌ অর্ডার বাতিল করা হয়েছে।")
            try:
                bot.delete_message(chat_id, call.message.message_id)
            except Exception: pass
            if order_id in GLOBAL_ORDERS: del GLOBAL_ORDERS[order_id]

def process_support_msg(message):
    try:
        bot.send_message(ADMIN_ID, f"🔔 **সাপোর্ট মেসেজ!**\n👤 আইডি: `{message.from_user.id}`\n💬 {message.text}")
        bot.send_message(message.chat.id, "✅ এডমিনের কাছে পাঠানো হয়েছে।")
    except Exception: pass

# ==========================================
#  ৮. 🔁 অটোমেটিক স্টক চেকার (Auto-Fetch Stream)
# ==========================================
def auto_grizzly_fetcher():
    country_id = "133" 
    price = 0.60
    
    while True:
        try:
            check_url = f"https://api.grizzlysms.com/stubs/handler_api.php?api_key={GRIZZLY_API_KEY}&action=getPrices&service=tg&country={country_id}"
            response = requests.get(check_url)
            
            if response.status_code == 200:
                try:
                    res = response.json()
                    if res and country_id in res.get('tg', {}):
                        count = res['tg'][country_id].get('count', 0)
                        if count > 0:
                            order_id = str(int(time.time()))
                            markup = types.InlineKeyboardMarkup()
                            markup.row(types.InlineKeyboardButton("🛒 Claim Telegram Number", callback_data=f"claim_{order_id}_{country_id}_{price}"))
                            
                            bot.send_message(GROUP_ID, f"⚡ **AUTOMATIC TELEGRAM DROP!** ⚡\n\n🎯 সার্ভিস: `TELEGRAM (tg)`\n💵 মূল্য: ${price} USDT\n\n🔥 স্টক এসেছে! দ্রুত স্নাইপ করুন।", reply_markup=markup)
                            time.sleep(120)
                except Exception: pass
        except Exception: pass
        time.sleep(15)

# ==========================================
#  ৯. ইঞ্জিন বুটআপ
# ==========================================
if __name__ == '__main__':
    keep_alive()
    Thread(target=auto_grizzly_fetcher, daemon=True).start()
    print("🚀 Khan Professional Telegram Sniper Bot is fully armed!")
    
    # রেন্ডার ফ্রেন্ডলি ক্র্যাশ-প্রুফ পোলিং লুপ
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception:
            time.sleep(5)
