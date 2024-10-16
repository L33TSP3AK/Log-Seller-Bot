from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import main, db

async def menu_kb(user_id):
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	if await main.IsAdmin().check(user_id=user_id):
		keyboard.add(KeyboardButton("💎 Admin Panel 💎"))
	keyboard.add(KeyboardButton("🔎 Search Logs"),KeyboardButton("🔎 Search Cookies"))
	keyboard.add(KeyboardButton("⏳ Available logs"),KeyboardButton("🍪 Available Cookies"))
	keyboard.add(KeyboardButton("🧿 BL Tools Config"))
	keyboard.add(KeyboardButton("💬 Information"),KeyboardButton("👤 Profile"))
	return keyboard

async def profile_kb():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("🎁 Activate Promocode 🎁", callback_data="menu:promocode"))
	return keyboard

async def contact_support():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("👨‍💻 Contact Support", url="https://t.me/Cash_Out_Gang1337"))
	return keyboard

# Logs
async def request_log(value):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("💎 Request", callback_data=f"logs:request_log:{value}"))
	keyboard.add(InlineKeyboardButton("👨‍💻 Contact Support", url="https://t.me/Cash_Out_Gang1337"))
	return keyboard

async def search_logs_methods():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("🌐 URL", callback_data=f"logs:search:URL"))
	keyboard.add(InlineKeyboardButton("🔤 Keyword", callback_data=f"logs:search:Keyword"))
	keyboard.add(InlineKeyboardButton("👤 Username", callback_data=f"logs:search:Username"))
	keyboard.add(InlineKeyboardButton("🔑 Password", callback_data=f"logs:search:Password"))
	return keyboard

async def buy_log(id):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("💸 Buy 💸", callback_data=f"logs:buy_log:{id}"))
	return keyboard

# Cookies
async def request_cookie(value):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("💎 Request", callback_data=f"cookies:request_cookie:{value}"))
	keyboard.add(InlineKeyboardButton("👨‍💻 Contact Support", url="https://t.me/Cash_Out_Gang1337"))
	return keyboard

async def buy_cookie(id):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("💸 Buy 💸", callback_data=f"cookies:buy_cookie:{id}"))
	return keyboard

# BL Configs
async def list_bl_configs():
	keyboard = InlineKeyboardMarkup()
	bl_configs = await db.get_datax(database="bl_configs", not_where=True, all=True)
	for bl_config in bl_configs:
		keyboard.add(InlineKeyboardButton(f"{bl_config['price']}$ | {bl_config['name']}", callback_data=f"bl_config:view:{bl_config['id']}"))
	return keyboard

async def buy_bl_config(id):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("💸 Buy 💸", callback_data=f"bl_config:buy_bl_config:{id}"))
	return keyboard

# Admin
async def admin_panel_kb():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("💎 Add Admin", callback_data="admin:add_admin"), InlineKeyboardButton("👤 Users", callback_data="admin:users"))
	keyboard.add(InlineKeyboardButton("🎁 Create Promocode", callback_data="admin:create_promocode"))
	keyboard.add(InlineKeyboardButton("📝 Import Logs", callback_data="admin:import_logs"),InlineKeyboardButton("🍪 Import Cookies", callback_data="admin:import_cookies"))
	keyboard.add(InlineKeyboardButton("🧿 Import BL Configs", callback_data="admin:import_bl_configs"))
	return keyboard

async def admin_users_panel_kb():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("👤 All Users", callback_data="admin:all_users"))
	keyboard.add(InlineKeyboardButton("🔍 Search User", callback_data="admin:search_user"))
	return keyboard

async def admin_user_panel_kb(user_id):
	keyboard = InlineKeyboardMarkup()
	ban = await db.get_datax(database="banlist",user_id=user_id)
	keyboard.add(InlineKeyboardButton("unBan" if ban else "Ban", callback_data=f"admin:ban:{user_id}"))
	return keyboard
	