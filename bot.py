from telegram import Update
from telegram.ext import filters, ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu, load_prompt, send_text_buttons, BotMode, QuizCounter)
import logging
import credentials

bot_mode = BotMode()
bot_mode.mode = "default"

# ===============================logging===========================================

logger = logging.getLogger(__name__)
def configure_logging(level):
    logging.basicConfig(
        level=level,
        datefmt = "%Y-%m-%d %H:%M:%S",
        format = "[%(asctime)s] %(module)s:%(lineno)d %(levelname)s %(funcName)s - %(message)s"
    )
configure_logging(level=logging.INFO)

# ===============================start menu code block===========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("func start started")
    bot_mode.mode = 'default'
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start':'Головне меню',
        'random':'Дізнатися випадковий цікавий факт 🧠',
        'gpt':'Задати питання чату GPT 🤖',
        'talk':'Поговорити з відомою особистістю 👤',
        'quiz':'Взяти участь у квіз ❓',
        'translator':'Перекладач GPT 📝',
        'image':'Опис зображення'
    })

# ===============================image recognition code block===========================================

async def image_recognition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("func image_recognition started")
    bot_mode.mode = 'image'
    await send_text(update,context,'Очікую на зображення')

async def image_send (update: Update, context: ContextTypes.DEFAULT_TYPE,image_url):
    logger.info("func image_send started")
    image_description = await chat_gpt.send_photo(image_url)
    await send_text_buttons(update,context,image_description,{
        'image_quit': 'Завершити'
    })

async def image_buttons (update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("func image_buttons started")
    await update.callback_query.answer()
    button = update.callback_query.data
    if button == 'image_quit':
        await start(update, context)

async def photo_handler(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):
    logger.info("func photo_handler started")
    if bot_mode.mode == 'image':
        photo = update.message.photo[0]
        photo_id = photo.file_id
        bot = update.get_bot()
        image = await bot.get_file(photo_id)
        image_url = image.file_path
        await image_send(update,context,image_url)

# ===============================translator code block===========================================

async def translator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = 'default'
    logger.info("func translator started")
    await send_image(update, context, 'translator')
    await send_text_buttons(update, context, load_message('translator'), {
        'translator_english': 'Англійська',
        'translator_german': 'Німецька',
        'translator_french': 'Французька',
        'translator_quit': 'Завершити роботу з перекладачем GPT'
    })
async def translator_next(update: Update, context: ContextTypes.DEFAULT_TYPE,massage):
    logger.info("func translator_next started")
    translated_text = await chat_gpt.add_message(massage)
    await send_text_buttons(update, context,translated_text,{
        'translator_change_language':'Змінити мову перекладу',
        'translator_quit':'Завершити'})

async def translator_buttons(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
    logger.info("func translator_buttons started")
    bot_mode.mode = 'translator'
    await update.callback_query.answer()
    button = update.callback_query.data
    if button == 'translator_english':
        await send_text(update, context, 'Введи текст для перекладу на обрану мову')
        chat_gpt.set_prompt(f'{load_prompt('translation')} англійська')
    elif button == 'translator_german':
        await send_text(update, context, 'Введи текст для перекладу на обрану мову')
        chat_gpt.set_prompt(f'{load_prompt('translation')} німецька')
    elif button == 'translator_french':
        await send_text(update, context, 'Введи текст для перекладу на обрану мову')
        chat_gpt.set_prompt(f'{load_prompt('translation')} французька')
    elif button == 'translator_change_language':
        bot_mode.mode = 'default'
        await translator(update,context)
    elif button == 'translator_quit':
        bot_mode.mode = 'default'
        await start(update,context)

# ===============================random fact code block===========================================

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("func random started")
    bot_mode.mode = 'default'
    await send_image(update, context, 'random')
    await send_text(update, context, load_message('random'))
    random_fact = await chat_gpt.send_question(load_prompt('random'), "Дай цікавий факт")
    await send_text_buttons(update, context, random_fact, {
        'random_new': "Хочу ще факт",
        'random_start': "Закінчити"})

async def random_buttons(update: Update,
                                   context:ContextTypes.DEFAULT_TYPE):
    logger.info("func random_buttons started")
    await update.callback_query.answer()
    query = update.callback_query.data
    if query == 'random_new':
        await random(update, context)
    elif query == 'random_start':
        await start(update, context)

# ===============================gpt question code block===========================================

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("func gpt started")
    bot_mode.mode = 'gpt'
    await send_image(update, context, 'gpt')
    await send_text(update, context, load_message('gpt'))
    chat_gpt.set_prompt(load_prompt('gpt'))

async def gpt_question(update: Update, context: ContextTypes.DEFAULT_TYPE, question):
    logger.info("func gpt_question started")
    answer = await chat_gpt.add_message(question)
    await send_text_buttons(update, context, answer,{'gpt_quit':'Завершити'})

async def gpt_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("func gpt_buttons started")
    await update.callback_query.answer()
    button = update.callback_query.data
    if button == 'gpt_quit':
        await start(update,context)

# ===============================famous person talk code block===========================================

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = "default"
    logger.info("func talk started")
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, 'Оберіть відому особистість, з якою хочете поговорити:', {
        'talk_cb':'Курт Кобейн - Соліст гурту Nirvana 🎸',
        'talk_qn':'Єлизавета II - Королева Обєднаного Королівства 👑',
        'talk_jt':'Джон Толкін - Автор книги "Володар Перснів" 📖',
        'talk_fn':'Фрідріх Ніцше - Філософ 🧠',
        'talk_sh':'Стівен Гокінг - Фізик 🔬'
    })
async def active_talk(update: Update, context: ContextTypes.DEFAULT_TYPE,message):
    logger.info("func active_talk started")
    await send_text_buttons(update, context, await chat_gpt.add_message(message), {
        'talk_end':'Завершити розмову'
    })
async def talk_buttons(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = 'talk'
    logger.info("func talk_buttons started")
    await update.callback_query.answer()
    button = update.callback_query.data
    if button == 'talk_cb':
        chat_gpt.set_prompt(load_prompt('talk_cobain'))
        await send_image(update,context,'talk_cobain')
        await send_text(update, context, 'Давай поспілкуємось чуваче')
    elif button == 'talk_qn':
        chat_gpt.set_prompt(load_prompt('talk_queen'))
        await send_image(update, context, 'talk_queen')
        await send_text(update, context, 'Її величність чекає')
    elif button == 'talk_jt':
        chat_gpt.set_prompt(load_prompt('talk_tolkien'))
        await send_image(update, context, 'talk_tolkien')
        await send_text(update, context, 'Джон з радістю відповість на твої питання')
    elif button == 'talk_fn':
        chat_gpt.set_prompt(load_prompt('talk_nietzsche'))
        await send_image(update, context, 'talk_nietzsche')
        await send_text(update, context, 'Фрідріх Ніцше готовий поділитися своїми поглядами')
    elif button == 'talk_sh':
        chat_gpt.set_prompt(load_prompt('talk_hawking'))
        await send_image(update, context, 'talk_hawking')
        await send_text(update, context, 'Стівен Гокінг розповість багато цікавого, запитуй')
    elif button == 'talk_end':
        await start(update,context)

# ===============================quiz code block===========================================
quiz_count = QuizCounter()

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = "default"
    logger.info("func quiz started")
    chat_gpt.set_prompt(load_prompt('quiz'))
    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, load_message('quiz'), {
        'quiz_prog': 'Quiz по основам програмування',
        'quiz_math': 'Quiz по математиці',
        'quiz_biology': 'Quiz по біології',
        'quiz_quit': 'Завершити Quiz'
    })

async def active_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE,message):
    logger.info("func active_quiz started")
    reply = await chat_gpt.add_message(message)
    if reply == "Правильно!":
        quiz_count.questions_count +=1
        quiz_count.wright_answers  +=1
    else:
        quiz_count.questions_count +=1
    await send_text_buttons(update, context, reply, {
        'quiz_more':'Наступне запитання',
        'quiz_change':'Змінити тему',
        'quiz_quit':'Завершити квіз'
    })

async def quiz_buttons(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
    logger.info("func quiz_buttons started")
    bot_mode.mode = 'quiz'
    await update.callback_query.answer()
    button = update.callback_query.data
    if button == 'quiz_prog':
        await send_text(update, context,await chat_gpt.add_message('quiz_prog'))
    elif button == 'quiz_math':
        await send_text(update, context,await chat_gpt.add_message('quiz_math'))
    elif button == 'quiz_biology':
        await send_text(update, context,await chat_gpt.add_message('quiz_biology'))
    elif button == 'quiz_more':
        await send_text(update, context,await chat_gpt.add_message('quiz_more'))
    elif button == 'quiz_change':
        await quiz(update,context)
    elif button == 'quiz_quit':
        await send_text(update, context,
                        f' Квіз завершено, загальна кількість запитань {quiz_count.questions_count}, правильних відповідей {quiz_count.wright_answers}')
        bot_mode.mode = 'default'
        quiz_count.questions_count = 0
        quiz_count.wright_answers = 0

# ===============================common message handler code block===========================================

async def message_handler(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):
    logger.info("func message_handler started")
    message = update.message.text
    if bot_mode.mode == 'gpt':
        await gpt_question(update, context, message)
    elif bot_mode.mode == 'quiz':
        await active_quiz(update,context, message)
    elif bot_mode.mode == 'translator':
        await translator_next(update,context,message)
    elif  bot_mode.mode == 'talk':
        await active_talk(update,context,message)
    else:
        logging.info("Received message: %s",message)

# ===============================bot main code block===========================================

chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)
app = ApplicationBuilder().token(credentials.BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('translator', translator))
app.add_handler(CommandHandler('image', image_recognition))

app.add_handler(CallbackQueryHandler(talk_buttons, pattern='^talk_'))
app.add_handler(CallbackQueryHandler(quiz_buttons, pattern='^quiz_'))
app.add_handler(CallbackQueryHandler(translator_buttons, pattern='^translator_'))
app.add_handler(CallbackQueryHandler(image_buttons, pattern='^image_'))
app.add_handler(CallbackQueryHandler(gpt_buttons, pattern='^gpt_'))
app.add_handler(CallbackQueryHandler(random_buttons,pattern='^random_'))

app.add_handler(MessageHandler(filters.TEXT, message_handler))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

app.run_polling()



