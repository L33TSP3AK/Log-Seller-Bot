from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from filters import IsBanned
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import asyncio
from aiogram import Router, F
from filters import IsAdmin, IsBanned, HasBalance
import db
import keyboards
from aiogram.types import CallbackQuery



bot_token = "BOT:TOKEN"
chat_admins = ADMIN_ID

storage = MemoryStorage()
bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
router = Router()

logging.basicConfig(
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s] %(message)s',
    level=logging.INFO,
)

async def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

async def print_name(name):
    return name.replace("<", "&lt;").replace(">", "&gt;")


async def add_log(message,text):
	user_text = f'''<a href='tg://user?id={message.from_user.id}'>{await print_name(message.from_user.full_name)}</a>'''
	send_text = f'{user_text} | {text}\n\n🆔 <code>{message.from_user.id}</code> 🧸 {message.from_user.get_mention()}' 
	await bot.send_message(chat_id=chat_admins, text=send_text) 


@router.message(IsBanned())
async def is_banned(message: Message):
    if not await db.check_user(message.from_user.id):
        await add_log(message, f"😍 Now registered in the bot!")
        await db.add_database(message)
    ban = await db.get_datax(database="banlist", user_id=message.from_user.id)
    await message.answer(f'''
😔 Unfortunately you are banned!

{f"🚫 Reason: {ban['ban_reason']}" if ban['ban_reason'] else ""}
''', reply_markup=await keyboards.contact_support())

@router.message(Command("start"))
async def welcome(message: Message):
    if not await db.check_user(message.from_user.id):
        await add_log(message, f"😍 Now registered in the bot!")
    await db.add_database(message)
    await message.answer(f"😉 Hello {message.from_user.mention}!\nWelcome to the OpenSourced Logs Bot!\n\nWith this bot you can search for valid, working accounts that have no 2FA or any kind of enforced security to block your access!!\nIf we dont have a log available that you would like to see, please just shoot a requests for it and our staff will make this available!", reply_markup=await keyboards.menu_kb(message.from_user.id))
@router.message(F.text)
async def get_message(message: Message, state: FSMContext):
    if message.text == "🔎 Search Logs":
        await message.answer(f'''
<i>{message.text}</i>
												
💫 Please select search logs function:''', reply_markup=await keyboards.search_logs_methods())
    elif message.text == "⏳ Available logs":
        logs = await db.get_datax(database="logs", not_where=True, all=True)
        website_counts = {}
        for log in logs:
            website = log['website']
            website_counts[website] = website_counts.get(website, 0) + 1
        
        output_string = "\n".join([f"{website} - <code>{count}</code>" for website, count in website_counts.items()])
        await message.answer(f'''
<i>{message.text}</i>

{output_string if output_string else "Not added yet"}
''')
    elif message.text == "🔎 Search Cookies":
        await message.answer(f'''
<i>{message.text}</i>
												
💫 Please write URL from cookies:''')
        await state.set_state(Main.SearchCookies)
    elif message.text == "🍪 Available Cookies":
        cookies = await db.get_datax(database="cookies", not_where=True, all=True)
        website_counts = {}
        for cookie in cookies:
            website = cookie['website']
            website_counts[website] = website_counts.get(website, 0) + 1
        
        output_string = "\n".join([f"{website} - <code>{count}</code>" for website, count in website_counts.items()])
        await message.answer(f'''
<i>{message.text}</i>

{output_string if output_string else "Not added yet"}
''')
    elif message.text == "🧿 BL Tools Config":
        bl_configs = await db.get_datax(database="bl_configs", not_where=True, all=True)
        await message.answer(f'''
🧿 All Configs: <code>{len(bl_configs)}</code>
''', reply_markup=await keyboards.list_bl_configs())
    elif message.text == "👤 Profile":
        get_user = await db.get_datax(database="users", user_id=message.from_user.id)
        purchases_logs = await db.get_datax(database="purchases", service="log", user_id=message.from_user.id, all=True)
        purchases_bl_configs = await db.get_datax(database="purchases", service="bl_config", user_id=message.from_user.id, all=True)
        purchases_cookies = await db.get_datax(database="purchases", service="cookie", user_id=message.from_user.id, all=True)
        await message.answer(f'''
<i>{message.text}</i>

🆔 TelegramID: <code>{message.from_user.id}</code>

💸 Balance: <code>{get_user['balance']}</code> $
💫 Purchased Logs: <code>{len(purchases_logs)}</code>
💫 Purchased Cookies: <code>{len(purchases_cookies)}</code>
💫 Purchased BL Configs: <code>{len(purchases_bl_configs)}</code>
''', reply_markup=await keyboards.profile_kb())
    elif message.text == "💬 Information":
        users = await db.get_datax(database="users", all=True, not_where=True)
        logs = await db.get_datax(database="logs", not_where=True, all=True)
        purchases = await db.get_datax(database="purchases", not_where=True, all=True)
        await message.answer(f'''
<i>{message.text}</i>

👤 Users: <code>{len(users)}</code>
📝 Current Logs: <code>{len(logs)}</code>
⏳ Submitted Logs: <code>{len(logs) + len(purchases)}</code>
💫 Purchases: <code>{len(purchases)}</code>
''', reply_markup=await keyboards.contact_support())
    elif message.text == "💎 Admin Panel 💎":
        if await IsAdmin()(message):
            logs = await db.get_datax(database="logs", not_where=True, all=True)
            cookies = await db.get_datax(database="cookies", not_where=True, all=True)
            bl_configs = await db.get_datax(database="bl_configs", not_where=True, all=True)
            await message.answer(f'''
💎 Admin Panel 💎
						
⏳ Logs: <code>{len(logs)}</code>
🍪 Cookies: <code>{len(cookies)}</code>
🧿 BL Configs: <code>{len(bl_configs)}</code>
						''', reply_markup=await keyboards.admin_panel_kb())

@router.callback_query(lambda c: c.data.startswith("menu"))
async def menu_callback(call: types.CallbackQuery, state: FSMContext):
    variant = call.data.split(":")[1]
    if variant == "promocode":
        await call.message.edit_text('✏️ Write promocode:')
        await state.set_state(Main.ActivatePromocode)
	
@router.callback_query(F.data.startswith("cookies"))
async def cookies_callback(call: CallbackQuery, state: FSMContext):
    variant = call.data.split(":")[1]
    get_user = await db.get_datax(database="users", user_id=call.from_user.id)
    if variant == "request_cookie":
        request = call.data.split(":")[2]
        await add_log(call, f"❗️ Request cookie: <code>{request}</code>")
        await call.message.edit_text(f'✅ Send Request Cookie <code>{request}</code>!')
    elif variant == "buy_cookie":
        id = call.data.split(":")[2]
        cookie = await db.get_datax(database="cookies", id=id)
        print(cookie)
        if int(get_user['balance']) >= int(cookie['price']):
            if cookie:
                await db.update_datax(update_parameters={
                    "balance": f"{int(get_user['balance']) - int(cookie['price'])}"
                }, where_parameters={
                    "user_id": call.from_user.id
                })
                await db.drop_column(table="cookies", path=cookie['path'])
                await db.add_purchases(call.from_user.id, "cookie", cookie['path'], cookie['price'])
                await call.message.answer_document(document=cookie['path'], caption=f'''
✅ Purchased cookie!

💸 Price: <code>{cookie['price']}</code> $
''')
                await call.message.delete()
            else:
                await call.message.edit_text('😔 Not found cookie', reply_markup=await keyboards.contact_support())
        else:
            await call.answer('😔 There is not enough money to buy', show_alert=True)

@router.callback_query(F.data.startswith("bl_config"))
async def bl_config_callback(call: CallbackQuery, state: FSMContext):
    variant = call.data.split(":")[1]
    get_user = await db.get_datax(database="users", user_id=call.from_user.id)
    if variant == "view":
        id = call.data.split(":")[2]
        bl_config = await db.get_datax(database="bl_configs", id=id)
        await call.message.edit_text(f'''
🔗 Name: <b>{bl_config['name']}</b>
💸 Price: <code>{bl_config['price']}</code> $
''', reply_markup=await keyboards.buy_bl_config(id))
    elif variant == "buy_bl_config":
        id = call.data.split(":")[2]
        bl_config = await db.get_datax(database="bl_configs", id=id)
        print(bl_config)
        if int(get_user['balance']) >= int(bl_config['price']):
            if bl_config:
                await db.update_datax(update_parameters={
                    "balance": f"{int(get_user['balance']) - int(bl_config['price'])}"
                }, where_parameters={
                    "user_id": call.from_user.id
                })
                await db.add_purchases(call.from_user.id, "bl_config", bl_config['path'], bl_config['price'])
                await call.message.answer_document(document=bl_config['path'], caption=f'''
✅ Purchased BL Config!

🔗 Name: <b>{bl_config['name']}</b>
💸 Price: <code>{bl_config['price']}</code> $
''')
                await call.message.delete()
            else:
                await call.message.edit_text('😔 Not found BL Config', reply_markup=await keyboards.contact_support())
        else:
            await call.answer('😔 There is not enough money to buy', show_alert=True)

@router.callback_query(F.data.startswith("logs"))
async def logs_callback(call: CallbackQuery, state: FSMContext):
    variant = call.data.split(":")[1]
    get_user = await db.get_datax(database="users", user_id=call.from_user.id)
    
    if variant == "search":
        type = call.data.split(":")[2]
        await call.message.edit_text(f'📝 Write {type}:')
        await state.update_data(type=type)
        await state.set_state(Main.SearchLogs)
    
    elif variant == "request_log":
        request = call.data.split(":")[2]
        await add_log(call, f"❗️ Request log: <code>{request}</code>")
        await call.message.edit_text(f'✅ Send Request log <code>{request}</code>!')
    
    elif variant == "buy_log":
        id = call.data.split(":")[2]
        log = await db.get_datax(database="logs", id=id)
        print(log)
        if int(get_user['balance']) >= int(log['price']):
            if log:
                data = f"{log['website']}:{log['login']}:{log['password']}"

                await db.update_datax(update_parameters={
                    "balance": f"{int(get_user['balance']) - int(log['price'])}"
                }, where_parameters={
                    "user_id": call.from_user.id
                })
                await db.drop_column(table="logs", id=id, login=log['login'], password=log['password'])
                await db.add_purchases(call.from_user.id, "log", data, log['price'])
                await call.message.edit_text(f'''
✅ Purchased log!
                                        
🌐 Website: {log['website']}
👤 Login: <code>{log['login']}</code>
🔑 Password: <code>{log['password']}</code>
''')
            else:
                await call.message.edit_text('😔 Not found log', reply_markup=await keyboards.contact_support())
        else:
            await call.answer('😔 There is not enough money to buy', show_alert=True)

    await call.answer()

@router.callback_query(F.data.startswith("admin"))
async def admin_callback(call: CallbackQuery, state: FSMContext):
    variant = call.data.split(":")[1]
    
    if variant == "add_admin":
        await call.message.edit_text("Please write ID new admin:")
        await state.set_state(Main.AddAdmin)
    
    elif variant == "create_promocode":
        await call.message.edit_text("Please write amount promocode:")
        await state.set_state(Main.CreatePromocode)
    
    elif variant == "import_logs":
        await call.message.edit_text("Pls send price")
        await state.set_state(Main.PriceLogs)
    
    elif variant == "import_cookies":
        await call.message.edit_text("Pls send name website")
        await state.set_state(Main.WebsiteCookies)
    
    elif variant == "import_bl_configs":
        await call.message.edit_text("Pls send special name config")
        await state.set_state(Main.NameBlConfig)
    
    elif variant == "users":
        users = await db.get_datax(database="users", all=True, not_where=True)
        await call.message.edit_text(f"Users: {len(users)}", reply_markup=await keyboards.admin_users_panel_kb())
    
    elif variant == "search_user":
        await call.message.edit_text("Please write Telegram ID user:")
        await state.set_state(Main.SearchUser)
    
    elif variant == "all_users":
        await call.message.answer("Loading...")
        users = await db.get_datax(database="users", all=True, not_where=True)
        text = ""
        for user in users:
            user_info = await bot.get_chat(user['user_id'])
            text += f'''🆔 User: {user['user_id']} | @{user_info.username} | {user_info.first_name} \n💸 Balance: {user['balance']}$\n🕐 DateReg: {user['date']}\n\n'''
        try:
            if len(text) > 4096:
                for x in range(0, len(text), 4096):
                    await call.message.answer(text[x:x+4096])
            else:
                await call.message.answer(text)
        except Exception as err:
            print(err)
            await call.message.answer(f'❌ Error: {err}')
    
    elif variant == "ban":
        user_id = call.data.split(":")[2]
        ban = await db.get_datax(database="banlist", user_id=user_id)
        if ban:
            await db.drop_column(table="banlist", user_id=user_id)
            await call.answer("✅ unBanned", show_alert=True)
        else:
            await db.add_ban(user_id)
            await call.answer("✅ Banned", show_alert=True)
    
    await call.answer()


async def process_search_results(message, logs, text):
	if logs:
		get_user = await db.get_datax(database="users", user_id=message.from_user.id)
		log = random.choice(logs)
		await message.answer(f'''
🔍 Found: <code>{len(logs)}</code> logs
💸 Balance: <code>{get_user['balance']}</code> $
1️⃣ Log price: <code>{log['price']}</code> $
''', reply_markup=await keyboards.buy_log(log['id']))
	else:
		await message.answer("😔 Nothing was found for this query!", reply_markup=await keyboards.request_log(text))

class Main(StatesGroup):
	ActivatePromocode = State()
	SearchLogs = State()
	SearchCookies = State()
	# Admin
	AddAdmin = State()

	PriceLogs = State()
	ImportLogs = State()

	WebsiteCookies = State()
	PriceCookies = State()
	ImportCookies = State()

	NameBlConfig = State()
	PriceBlConfig = State()
	ImportBlConfig = State()

	SearchUser = State()
	CreatePromocode = State()


@router.message(Main.SearchLogs)
async def search_logs_sg(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    if data['type'] == "URL":
        url = text.replace('https://', '').replace('http://', '').replace('/', '')
        logs = await db.get_datax(database="logs", website=url, all=True)
    elif data['type'] == "Keyword":
        logs = await db.get_datax_like(database="logs", column="website", value=text, all=True)
    elif data['type'] == "Username":
        logs = await db.get_datax(database="logs", login=text, all=True)
    elif data['type'] == "Password":
        logs = await db.get_datax(database="logs", password=text, all=True)
    await process_search_results(message, logs, text)
    await state.clear()

@router.message(Main.SearchCookies)
async def search_cookies_sg(message: Message, state: FSMContext):
    website = message.text
    cookies = await db.get_datax(database="cookies", website=website, all=True)
    if cookies:
        get_user = await db.get_datax(database="users", user_id=message.from_user.id)
        cookie = random.choice(cookies)
        await message.answer(f'''
🔍 Found: <code>{len(cookies)}</code> cookies
💸 Balance: <code>{get_user['balance']}</code> $
1️⃣ Cookie price: <code>{cookie['price']}</code> $
''', reply_markup=await keyboards.buy_cookie(cookie['id']))
    else:
        await message.answer("😔 Nothing was found for this query!", reply_markup=await keyboards.request_cookie(website))
    await state.clear()

@router.message(Main.AddAdmin)
async def add_admin_sg(message: Message, state: FSMContext):
    user_id = message.text
    await db.add_admin(user_id)
    await message.answer(f"Success")
    await state.clear()

@router.message(Main.PriceLogs)
async def price_logs_sg(message: Message, state: FSMContext):
    price = message.text
    if await isfloat(price):
        await state.update_data(price=price)
        await message.answer("Please send me .txt file. Format to .txt file: website<code>:</code>login<code>:</code>password")
        await state.set_state(Main.ImportLogs)
    else:
        await message.answer('This incorrect digit!')
        await state.clear()

@router.message(Main.ImportLogs)
async def import_logs_sg(message: Message, state: FSMContext):
    if message.text:
        await message.answer('No .txt file!')
    elif message.document:
        document = message.document
        if document.mime_type == 'text/plain' and document.file_name.endswith('.txt'):
            await message.answer("Read file...")
            data = await state.get_data()
            file_path = f'import_logs/{strftime("%Y-%m-%d_%H-%M-%S")}_{document.file_name}'
            file = await bot.get_file(document.file_id)
            await bot.download_file(file.file_path, file_path)
            print(file_path)
            ok, err = 0, 0
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    line = line.replace('http://', '').replace('https://', '')
                    parts = line.split(":")
                    try:
                        domain_parts = parts[0].split('/')[0].split('.')
                        website = ".".join(domain_parts[-2:])
                        login = parts[1]
                        password = parts[2]
                        await db.add_logs(website, data['price'], login, password)
                        ok += 1
                    except:
                        err += 1
            await message.answer(f"Success import\n✅: {ok}\n❌: {err}")
            os.remove(file_path)
        else:
            await message.answer("Pls send .txt file!")
    else:
        await message.answer("Not found file!")
    await state.clear()


@router.message(Main.WebsiteCookies)
async def website_cookies_sg(message: Message, state: FSMContext):
    website = message.text
    await state.update_data(website=website)
    await message.answer("Pls send price")
    await state.set_state(Main.PriceCookies)

@router.message(Main.PriceCookies)
async def price_cookies_sg(message: Message, state: FSMContext):
    price = message.text
    if await isfloat(price):
        await state.update_data(price=price)
        await message.answer("Please send me .txt file")
        await state.set_state(Main.ImportCookies)
    else:
        await message.answer('This incorrect digit!')
        await state.clear()

@router.message(Main.ImportCookies)
async def import_cookies_sg(message: Message, state: FSMContext):
    if message.text:
        await message.answer('No .txt file!')
    elif message.document:
        document = message.document
        if document.mime_type == 'text/plain' and document.file_name.endswith('.txt'):
            await message.answer("Download file...")
            data = await state.get_data()
            file_path = message.document.file_id
            print(file_path)
            try:
                await db.add_cookies(data['website'], data['price'], file_path)
                await message.answer(f"✅ Success import")
            except:
                await message.answer(f"❌ Failed import")
        else:
            await message.answer("Pls send .txt file!")
    else:
        await message.answer("Not found file!")
    await state.clear()

@router.message(Main.NameBlConfig)
async def name_bl_config_sg(message: Message, state: FSMContext):
    name = message.text 
    await state.update_data(name=name)
    await message.answer("Please send price config")
    await state.set_state(Main.PriceBlConfig)

@router.message(Main.PriceBlConfig)
async def price_bl_config_sg(message: Message, state: FSMContext):
    price = message.text
    if await isfloat(price):
        await state.update_data(price=price)
        await message.answer("Please send me file config ")
        await state.set_state(Main.ImportBlConfig)
    else:
        await message.answer('This incorrect digit!')
        await state.clear()

@router.message(Main.ImportBlConfig)
async def import_bl_config_sg(message: Message, state: FSMContext):
    if message.document:
        await message.answer("Download file...")
        data = await state.get_data()
        file_path = message.document.file_id
        print(file_path)
        try:
            await db.add_bl_config(data['name'], data['price'], file_path)
            await message.answer(f"✅ Success import")
        except:
            await message.answer(f"❌ Failed import")
    else:
        await message.answer("Not found file!")
    await state.clear()

@router.message(Main.SearchUser)
async def search_user_sg(message: Message, state: FSMContext):
    user_id = message.text
    if user_id.isdigit():
        get_user = await db.get_datax(database="users", user_id=user_id)
        ban = await db.get_datax(database="banlist", user_id=user_id)
        if get_user:
            user_info = await bot.get_chat(user_id)
            purchases_logs = await db.get_datax(database="purchases", service="log", user_id=message.from_user.id, all=True)
            purchases_bl_configs = await db.get_datax(database="purchases", service="bl_config", user_id=message.from_user.id, all=True)
            purchases_cookies = await db.get_datax(database="purchases", service="cookie", user_id=message.from_user.id, all=True)
            await message.answer(f'''
🔎 View Profile {user_info.mention}

👤 Name: {await print_name(user_info.full_name)}
🆔 ID: <code>{get_user['user_id']}</code>
#️⃣ UserName: @{user_info.username}
🚫 Ban: {f"Yes | <code>{ban['date']}</code>" if ban else "No"}


💸 Balance: <code>{get_user['balance']}</code> $
💫 Purchased Logs: <code>{len(purchases_logs)}</code>
💫 Purchased Cookies: <code>{len(purchases_cookies)}</code>
💫 Purchased BL Configs: <code>{len(purchases_bl_configs)}</code>
🕐 DateReg: <code>{get_user['date']}</code>
''', reply_markup=await keyboards.admin_user_panel_kb(user_id))
        else:
            await message.answer(f'''
🔎 User <code>{user_id}</code> not found!

🆔 ID: <code>{user_id}</code>
🚫 Ban: {f"Yes | <code>{ban['date']}</code>" if ban else "No"}
''', reply_markup=await keyboards.admin_user_panel_kb(user_id))
    else:
        await message.answer('No int message')
    await state.clear()

@router.message(Main.ActivatePromocode)
async def activate_promocode_sg(message: Message, state: FSMContext):
    name = message.text
    promocode = await db.get_datax(database="promocodes", name=name)
    if promocode:
        await db.drop_column(table="promocodes", name=name)
        get_user = await db.get_datax(database="users", user_id=message.from_user.id)
        await db.update_datax(update_parameters={
            "balance": f"{int(get_user['balance']) + int(promocode['amount'])}"
        }, where_parameters={
            "user_id": message.from_user.id
        })
        await message.answer(f'✅ Activated promocode, give <code>{promocode["amount"]}</code>$')
    else:
        await message.answer('❗️ Not found promocode')
    await state.clear()



@router.message(Main.CreatePromocode)
async def create_promocode_sg(message: Message, state: FSMContext):
    amount = message.text
    if amount.isdigit():
        characters = string.ascii_lowercase + string.digits
        name = ''.join(random.choice(characters) for _ in range(random.randint(8, 16)))
        await db.add_promo(name, amount)
        await message.answer(f"💫 Created promocode:\n\n📝 Name: <code>{name}</code>\n💰 Amount: <code>{amount}</code>$")
    else:
        await message.answer('No int message')
    await state.clear()


async def main():
    bot = Bot(token=bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    await db.create_tables()
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=False)




if __name__ == '__main__':
    asyncio.run(main())