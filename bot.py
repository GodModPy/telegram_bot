import base64

from telegram import Update, PhotoSize
from telegram.ext import filters, ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu, load_prompt, send_text_buttons,bot_mode,quiz_counter)
import credentials

bot_mode = bot_mode()
bot_mode.mode = "default"
quiz_count = quiz_counter()

async def default_callback_handler(update: Update,
                                   context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    query = update.callback_query.data
    if query == 'new_random':
        await random(update, context)
    elif query == 'back_start':
        await start(update, context)


async def message_handler(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):
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
        print(f'Resived message {message}')

async def photo_handler(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):
    if bot_mode.mode == 'image':
        photo = update.message.photo[0]
        photo_id = photo.file_id
        bot = update.get_bot()
        image = await bot.get_file(photo_id)
        image_url = image.file_path
        await image_send(update,context,image_url)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        'image':'Опис зображення',

    })

async def image_recognition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = 'image'
    await send_text(update,context,'Очікую на зображення')

async def image_send (update: Update, context: ContextTypes.DEFAULT_TYPE,image_url):
    image_description = await chat_gpt.send_photo(image_url)
    await send_text_buttons(update,context,image_description,{
        'image_next': 'Надіслати ще зображення', 'image_quit': 'Завершити'
    })

async def image_buttons (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    button = update.callback_query.data
    if button == 'image_next':
        await image_recognition(update,context)
    elif button == 'image_quit':
        bot_mode.mode = "default"
        await start(update, context)

async def translator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = 'translator'
    await send_image(update, context, 'translator')
    await send_text_buttons(update, context, load_message('translator'), {
        'translator_english': 'Англійська',
        'translator_german': 'Німецька',
        'translator_french': 'Французька',
        'translator_quit': 'Завершити роботу з перекладачем GPT'
    })

async def translator_next(update: Update, context: ContextTypes.DEFAULT_TYPE,massege):
    translated_text = await chat_gpt.add_message(massege)
    await send_text_buttons(update, context,translated_text,{
        'translator_change_language':'Змінити мову перекладу',
        'translator_quit':'Завершити'})


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = 'default'
    await send_image(update, context, 'random')
    await send_text(update, context, load_message('random'))
    random_fact = await chat_gpt.send_question(load_prompt('random'), "Дай цікавий факт")
    await send_text_buttons(update, context, random_fact, {
        'new_random': "Хочу ще факт",
        'back_start': "Закінчити"})

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = 'gpt'
    await send_image(update, context, 'gpt')
    await send_text(update, context, load_message('gpt'))
    chat_gpt.set_prompt(load_prompt('gpt'))

async def gpt_question(update: Update, context: ContextTypes.DEFAULT_TYPE, question):
    answer = await chat_gpt.add_message(question)
    await send_text(update, context, answer)

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = 'talk'
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, 'Оберіть відому особистість, з якою хочете поговорити:', {
        'talk_cb':'Курт Кобейн - Соліст гурту Nirvana 🎸',
        'talk_qn':'Єлизавета II - Королева Обєднаного Королівства 👑',
        'talk_jt':'Джон Толкін - Автор книги "Володар Перснів" 📖',
        'talk_fn':'Фрідріх Ніцше - Філософ 🧠',
        'talk_sh':'Стівен Гокінг - Фізик 🔬'
    })
async def active_talk(update: Update, context: ContextTypes.DEFAULT_TYPE,message):
    await send_text_buttons(update, context, await chat_gpt.add_message(message), {
        'talk_end':'Завершити розмову'
    })


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode.mode = 'quiz'
    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, load_message('quiz'), {
        'quiz_prog':'Quiz по основам програмування',
        'quiz_math':'Quiz по математиці',
        'quiz_biology':'Quiz по біології',
        'quiz_quit':'Завершити Quiz'
    })
    chat_gpt.set_prompt(load_prompt('quiz'))


async def active_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE,message):
    reply = await chat_gpt.add_message(message)
    if reply == "Правильно!":
        quiz_count.questions_count +=1
        quiz_count.wright_answers  +=1
    else:
        quiz_count.questions_count +=1
    await send_text_buttons(update, context, reply, {
        'quiz_next':'next question',
        'quiz_change':'change topic',
        'quiz_quit':'end quiz'
    })

async def talk_buttons(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
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
        bot_mode.mode = 'default'
        await start(update,context)

async def quiz_buttons(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    button = update.callback_query.data
    if button == 'quiz_prog':
        await send_text(update, context,await chat_gpt.add_message('quiz_prog'))
    elif button == 'quiz_math':
        await send_text(update, context,await chat_gpt.add_message('quiz_math'))
    elif button == 'quiz_biology':
        await send_text(update, context,await chat_gpt.add_message('quiz_biology'))
    elif button == 'quiz_next':
        await send_text(update, context,await chat_gpt.add_message('задай нове запитання'))
    elif button == 'quiz_change':
        await quiz(update,context)
    elif button == 'quiz_quit':
        await send_text(update, context,
                        f' Квіз закінчено, загальна кількість запитань {quiz_count.questions_count}, правильних відповідей {quiz_count.wright_answers}')
        bot_mode.mode = 'default'

async def translator_buttons(update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    button = update.callback_query.data
    if button == 'translator_english':
        await send_text(update, context, 'Введи текст для перекладу на обрану мову')
        await chat_gpt.add_message('Переклади наступне повідомлення англійською мовою')
    elif button == 'translator_german':
        await send_text(update, context, 'Введи текст для перекладу на обрану мову')
        await chat_gpt.add_message('Переклади наступне повідомлення німецькою мовою')
    elif button == 'translator_french':
        await send_text(update, context, 'Введи текст для перекладу на обрану мову')
        await chat_gpt.add_message('Переклади наступне повідомлення французькою мовою')
    elif button == 'translator_change_language':
        bot_mode.mode = 'default'
        await translator(update,context)
    elif button == 'translator_quit':
        bot_mode.mode = 'default'
        await start(update,context)

chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)
app = ApplicationBuilder().token(credentials.BOT_TOKEN).build()

# Зареєструвати обробник команди можна так:
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('translator', translator))
app.add_handler(CommandHandler('image', image_recognition))

# Зареєструвати обробник колбеку можна так:

app.add_handler(CallbackQueryHandler(talk_buttons, pattern='^talk_'))
app.add_handler(CallbackQueryHandler(quiz_buttons, pattern='^quiz_'))
app.add_handler(CallbackQueryHandler(translator_buttons, pattern='^translator_'))
app.add_handler(CallbackQueryHandler(image_buttons, pattern='^image_'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.add_handler(MessageHandler(filters.TEXT, message_handler))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.run_polling()
