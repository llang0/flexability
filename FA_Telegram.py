import asyncio
import threading
import queue, os, json
import telegram
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler

from lib.FlexUnlimited import FlexUnlimited

# init ingredients for running flex scanner in another thread
queue = queue.Queue()
thread = None
stop_event = asyncio.Event()
flexUnlimited = FlexUnlimited(stop_event, queue=queue)


CHAT_ID = 5755626527
LOGIN = 0
link = "https://www.amazon.com/ap/signin?ie=UTF8&clientContext=134-9172090-0857541&openid.pape.max_auth_age=0&use_global_authentication=false&accountStatusPolicy=P1&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&use_audio_captcha=false&language=en_US&pageId=amzn_device_na&arb=97b4a0fe-13b8-45fd-b405-ae94b0fec45b&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fap%2Fmaplanding&openid.assoc_handle=amzn_device_na&openid.oa2.response_type=token&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.ns.oa2=http%3A%2F%2Fwww.amazon.com%2Fap%2Fext%2Foauth%2F2&openid.oa2.scope=device_auth_access&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&disableLoginPrepopulate=0&openid.oa2.client_id=device%3A32663430323338643639356262653236326265346136356131376439616135392341314d50534c4643374c3541464b&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"

# globals for stations command
# check for valid station list and generate one if it doesn't exist
if not os.path.exists("station_list.json"):
    flexUnlimited.getAllServiceAreas()

# load station codes into list
with open("station_list.json", "r") as f:
    station_data = json.load(f)
stations = [item for item in station_data.keys()]

# load user preferences
with open("config.json", "r") as f:
    config = json.load(f)

checked_buttons = [False] * len(stations)
chosen_stations = [item for item in config["desiredWarehouses"]]
speed_var = config["refreshInterval"]

for i in range(len(stations)):
    if chosen_stations.count(stations[i]):
        checked_buttons[i] = True


def user_known():
  """helper method to check if user is registered or not"""
  dict = flexUnlimited.__dict__
  for k in dict:
    #print(dict)
    if k == "desiredWeekdays":
      continue
    if k == "lastBlock":
       continue
    if dict[k] == None:
      print(f"{k} is set to None")
      return False
  return True

from lib.Config import Config
config = Config()

async def generate_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """generates new config file and fills in some info"""
  if not os.path.exists("config.json"):
    with open("config.json", 'w') as file:
        dict = config.as_dict()
        dict["chat_id"] = update.message.from_user.id
        dict["first_name"]= update.message.from_user.first_name
        dict["last_name"] = update.message.from_user.last_name
        dict["language_code"] = update.message.from_user.language_code
        json.dump(dict, file, indent=4)
  else: 
    pass
  

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # handled by commandHandler
    await context.bot.send_message(chat_id=update.message.chat_id, text="Welcome to FlexAbility!")
    if user_known():
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ready to /startscan! Use /stopscan to stop ")
        return ConversationHandler.END
    else:
       await generate_config(update, context)
       await update.message.reply_text(
      f"Open the following link, sign in, and enter the entire resulting URL into this chat.\n {link}"
      )
       return LOGIN
    
    
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # handled by conversationHandler
    """gets maplanding from user and registers account"""
    user = update.message.from_user
    maplanding_url = update.message.text
    flexUnlimited.registerAccount(maplanding_url)
    flexUnlimited.re_init()
    # print(f"Input from user: {maplanding_url}")
    # pass imput into flexUnlimited register function
    await update.message.reply_text(
        "Thank you! Use /start to restart the bot with your new credentials"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # handled by conversationHandler
    """Cancels and ends the conversation."""
    user = update.message.from_user
    print("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Please try again, FlexAbility can't run without a valid response."
    )

    return ConversationHandler.END

# ==============================================================================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    data = query.data

    if data.startswith('check'):
        index = int(data[6:])
        checked_buttons[index] = not checked_buttons[index]
        keyboard = await create_keyboard()
        await query.edit_message_reply_markup(reply_markup=keyboard)

async def create_keyboard():
    """create keyboard used for picking stations"""
    buttons = []
    with open("station_list.json", "r") as f:
        data = json.load(f)
    for i in range(len(stations)):
        checked = checked_buttons[i]
        text = f"{'✅' if checked else ' '} {data[stations[i]]}"
        button = InlineKeyboardButton(text, callback_data=f"check:{i}")
        buttons.append([button])

    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard

async def station_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
   """sends station filter inline keyboard"""
   keyboard = await create_keyboard()
   await update.message.reply_text("Select stations then use /startscan:", reply_markup=keyboard)


async def speed(update: Update, context: ContextTypes.DEFAULT_TYPE):
  global speed_var
  if float(context.args[0]) < 1.6 :
     await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Enter a value higher than 1.6")
     return
  try:
    speed_var = float(context.args[0])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your speed is set to {speed_var}")
  except:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error! Please type /speed followed by a number")



def update_filters():
  """updates config file to reflect chosen stations
  then reinits flexUnlimited with new values"""
  print(f"speed set to: {speed_var}")

  # update chosen_stations based on checked_buttons
  chosen_stations = []
  for i in range(len(stations)):
    if checked_buttons[i]:
      chosen_stations.append(stations[i])

  # update config based on chosen_stations 
  with open("config.json", "r+") as configFile:
    config = json.load(configFile)
    config["desiredWarehouses"] = chosen_stations
    config["refreshInterval"] = speed_var
    configFile.seek(0)
    json.dump(config, configFile, indent=2)
    configFile.truncate()

  # reinit flexUnlimited with new config values
  flexUnlimited.re_init()

# ==============================================================================================================

def scanner_thread(stop_event):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(flexUnlimited.run())
    except asyncio.CancelledError:
        pass


async def start_scanner_thread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global thread
    if thread is not None and thread.is_alive():
        # Thread is already running
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Already scanning :)")
        return
    stop_event.clear()
    thread = threading.Thread(target=scanner_thread, args=(stop_event,))
    thread.start()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Scanning started")


async def startscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # always update filters
    update_filters()
    await start_scanner_thread(update, context)
    #await context.bot.send_message(chat_id=update.effective_chat.id, text="Scanning started")


async def stopscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global thread
    stop_event.set()
    if thread is not None and thread.is_alive():
        thread.join()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Scanning stopped")




async def get_scan_status(context: ContextTypes.DEFAULT_TYPE):
    if not queue.empty():
        message = queue.get()
        await context.bot.send_message(chat_id=CHAT_ID, text=message)





if __name__ == "__main__":
    print("***Welcome to FlexAbility!***")
    application = ApplicationBuilder().token('5968329152:AAEmCj_lky3G6XHaTCqZN9m_wa5UVw3XNVw').build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, login)],
        },
        fallbacks= [CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    start_handler = CommandHandler('start', start)
    startscan_handler = CommandHandler('startscan', startscan)
    stopscan_handler = CommandHandler('stopscan', stopscan)
    station_filters_handler = CommandHandler('stations', station_filters)
    speed_handler = CommandHandler('speed', speed)

    application.add_handler(start_handler)
    application.add_handler(startscan_handler)
    application.add_handler(stopscan_handler)
    application.add_handler(station_filters_handler)
    application.add_handler(speed_handler)

    application.add_handler(CallbackQueryHandler(button_callback))

    job_queue = application.job_queue
    job_checkq = job_queue.run_repeating(get_scan_status, interval=1, first=10)

    application.run_polling()
