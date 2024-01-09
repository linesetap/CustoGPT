from openai import *
import datetime
from uuid import *
import html
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    PicklePersistence,
    CallbackContext,
    CallbackQueryHandler,
    ContextTypes,
    InlineQueryHandler,
)
from telegram.constants import ParseMode
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    PhotoSize,
)
import sys
import requests
import random
import json
import mistune
import tempfile
import traceback
import logging
import asyncio
import time
import re
import aiohttp
import os
import colorama
from website import *
website()


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
colorama.init()
DEVELOPER_CHAT_ID = 6262702086  # Input: int, value: Telegram channel/user.
URL_DOCS = "https://telegra.ph/Custo-12-21"


markup = InlineKeyboardMarkup([[
    InlineKeyboardButton(text="📚", url="https://t.me/custogpt/"),
    InlineKeyboardButton(text="ℹ️", url=URL_DOCS),
    InlineKeyboardButton(text="💵", url="https://paypal.com/paypalme/lineset"),
    InlineKeyboardButton(text="✉️", url="https://t.me/jiv9e"),
]])


async def start_command(update, context):
    send_request()
    user_id = update.message.from_user.id
    await update.message.reply_text(
        f"""<b>البوت العربي الأول في تخصيص GPT على تيليجرام!!</b>

تخصيص GPT (CustoGPT) هو البوت العربي الأول في مجال الذكاء الاصطناعي الذي يوفر لك جميع ميزات OpenAI APIs بشكل مجاني.

للحصول على معلومات عن كيفية الإستخدام انقر على ℹ️ او على هذا الرابط:
{URL_DOCS}

لمزيد من المعلومات حول البوت، انقر على 📚. ولمزيد من المعلومات حول الرصيد، انقر على ℹ️. ولدعم البوت عبر PayPal، انقر على 💵. وللتواصل مع الدعم الفني انقر على ✉️.""",
        reply_to_message_id=update.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=markup)


# تعريف دالة للتعامل مع الرسائل الواردة
async def message_handler(update, context):
    try:
        send_request()
        # التأكد من أن الرسالة خاصة في جميع الحالات
        if update.message.chat.type != "private":
            # لا يرد إذا كانت الرسالة من مجموعة وليست ردًا على رسالة البوت
            reply_to_message = update.message.reply_to_message
            if not (reply_to_message and reply_to_message.from_user.id == context.bot.id):
                return

        # التحقق من أن النص غير فارغ
        text = update.message.text
        if not text.strip():
            return

        # تحديث رصيد المستخدم بخصم قيمة الطلب
        balance = context.user_data.setdefault("balance", 5)
        deduction_amount = 0.005

        if balance < deduction_amount:
            await update.message.reply_text(
                "❌️ | رصيدك غير كافٍ لهذه العملية.",
                parse_mode="MARKDOWN",
                reply_to_message_id=update.message.message_id)
            return
        else:
            context.user_data["balance"] = max(0, balance - deduction_amount)

        key = context.user_data.get("authorize")
        if not key:
            await update.message.reply_text(
                "🔑 | تحتاج الى تفعيل مفتاح التفويض بالبوت لأجل استخدام هذا الأمر.",
                parse_mode="MARKDOWN",
                reply_to_message_id=update.message.message_id)
            return

        client = OpenAI(api_key=key)
        response_moderation = client.moderations.create(
            model="text-moderation-latest", input=update.message.text)
        output_moderation = response_moderation.results[0]
        if output_moderation.flagged:
            await update.message.reply_text(
                "❌️ | تم رفض طلبك نتيجة لنظام السلامة لدينا. "
                "قد تحتوي مطالبتك على نص غير مسموح به بواسطة نظام الأمان لدينا.",
                parse_mode="MARKDOWN",
                reply_to_message_id=update.message.message_id)
            return

        instructions = context.user_data.get("instructions", None)
        conversation = context.user_data.get("conversation", None)

        if not conversation:
            if instructions:
                conversation = [
                    {"role": "system", "content": f"{instructions}"}]
            else:
                conversation = []

        conversation.append({"role": "user", "content": text})

        # إرسال رسالة "يتم الآن العمل على الإجابة على رسالتك..." للمستخدم
        message = await update.message.reply_text(
            "يتم الآن العمل على الإجابة على رسالتك...", parse_mode="MARKDOWN",
            reply_to_message_id=update.message.message_id)

        # إنشاء مولد للحصول على الردود من openai
        generator = client.chat.completions.create(
            model="gpt-3.5-turbo-1106", messages=conversation, temperature=0.5, stop=None, stream=True)

        # إنشاء متغير لتخزين الرسائل
        messages = []

        # تعريف متغير زمني لتتبع آخر تحديث للرسالة
        last_update = time.time()

        # إرسال الردود تدريجياً للمستخدم باستخدام خاصية stream
        for response in generator:
            if response.choices[0].delta.content is not None or False:
                # إضافة محتوى الرد إلى قائمة الرسائل
                messages.append(response.choices[0].delta.content)
                messages_str = "".join(messages)
                # الحصول على الوقت الحالي
                current_time = time.time()
                # مقارنة الوقت الحالي مع آخر تحديث
                if current_time - last_update >= 1:
                    # تحديث الرسالة بالرسائل الجديدة
                    await message.edit_text(f"✏️ [{random.randint(100000, 999000)}] | {messages_str}")
                    # تحديث متغير الزمن
                    last_update = current_time
            else:
                # إرسال الرسالة النهائية
                await message.edit_text(f"{messages_str}", parse_mode="MARKDOWN")
                conversation.append(
                    {"role": "assistant", "content": messages_str})
                context.user_data["conversation"] = conversation

    except Exception as e:
        print(f"❌️ | `{e}`")
        await update.message.reply_text(f"❌️ | `{e}`", parse_mode="MARKDOWN",
                                        reply_to_message_id=update.message.message_id)
        del context.user_data["conversation"][-1]


# تعريف دالة لمعالجة أمر /authorize
async def authorize_command(update: Update, context):
    send_request()
    try:
        # التحقق من وجود وسيطة بعد الأمر
        if context.args:
            # الحصول على الوسيطة كقيمة لـ authorize
            value = " ".join(context.args)

            try:
                # تخزين أو تحديث قيمة authorize في context.user_data
                context.user_data["authorize"] = value
                context.user_data["instructions"] = None
                context.user_data["conversation"] = None
                # إرسال رسالة تأكيد بشكل غير متزامن
                await update.message.reply_text(
                    f"✅ | تم تخزين مفتاح التفويض بنجاح.",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=update.message.message_id)
            except Exception as e:
                # إرسال رسالة خطأ بشكل غير متزامن في حالة فشل التحقق من المفتاح
                await update.message.reply_text(
                    f"❌️ | `{e}`",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=update.message.message_id)
        else:
            # إذا لم يتم إرفاق مفتاح، عرض المفتاح الحالي إذا كان موجودًا
            current_key = context.user_data.get('authorize', None)
            await update.message.reply_text(
                f"⚙️ | إعدادات مفتاح التفويض الحالي:\n```\n{current_key}```",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=update.message.message_id)
    except Exception as e:
        await update.message.reply_text(
            f"❌️ | `{e}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=update.message.message_id)


# تعريف دالة لمعالجة أمر /customize
async def customize_command(update: Update, context):
    response = requests.get(URL, headers=HEADERS)
    try:
        # التحقق إذا كان الأمر يحتوي على نص
        if context.args:
            # التحقق إذا كان النص هو "<none>" بأي حالة
            if context.args[0].lower() == "<none>":
                # في حالة كتابة "<none>", قم بتعيين الشخصية إلى None
                context.user_data["instructions"] = None
                context.user_data["conversation"] = None
                # إرسال رسالة تأكيد بشكل غير متزامن
                await update.message.reply_text(
                    "🔄 | تم اعادة ضبط الشخصية للافتراضية.",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=update.message.message_id)
                return

            # التحقق من وجود مفتاح تفويض في context.user_data
            if "authorize" in context.user_data:
                # الحصول على الوسيطة كقيمة لـ instructions
                value = " ".join(context.args)

                # تخزين أو تحديث قيمة instructions في context.user_data
                # قبل ذلك، قم بفحص النص باستخدام خدمة الفحص التلقائي Moderation API
                key = context.user_data["authorize"]
                client = OpenAI(api_key=key)
                response_moderation = client.moderations.create(
                    model="text-moderation-latest", input=value)
                output_moderation = response_moderation.results[0]

                # التحقق إذا كان هناك مخاطر في النص
                if output_moderation.flagged:
                    await update.message.reply_text(
                        "❌️ | تم رفض طلبك نتيجة لنظام السلامة لدينا. "
                        "قد تحتوي مطالبتك على نص غير مسموح به بواسطة نظام الأمان لدينا.",
                        parse_mode=ParseMode.MARKDOWN,
                        reply_to_message_id=update.message.message_id)
                    return

                context.user_data["instructions"] = value
                context.user_data["conversation"] = None
                # إرسال رسالة تأكيد بشكل غير متزامن
                await update.message.reply_text(
                    f"✅ | تم تخزين قيمة الشخصية بنجاح.",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=update.message.message_id)
            else:
                # إرسال رسالة خطأ بشكل غير متزامن
                await update.message.reply_text(
                    "🔑 | يرجى تفويض مفتاح OPENAI أولاً باستخدام الأمر /authorize. "
                    "يمكنك الحصول على واحد من هنا:\nhttps://platform.openai.com/api-keys",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=update.message.message_id)
        else:
            # إذا لم يتم إرفاق نص، عرض إعدادات الشخصية
            instructions = context.user_data.get("instructions", None)
            settings_message = (
                f"⚙️ | إعدادات الشخصية الحالية:\n"
                f"```\n{instructions}\n```"
            )
            await update.message.reply_text(
                settings_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=update.message.message_id)
    except Exception as e:
        await update.message.reply_text(
            f"❌️ | `{e}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=update.message.message_id)


async def tts_command(update: Update, context: CallbackContext):
    response = requests.get(URL, headers=HEADERS)
    try:
        key = context.user_data.get("authorize")
        if not key:
            await update.message.reply_text(
                "🔑 | تحتاج الى تفعيل مفتاح التفويض بالبوت لأجل استخدام هذا الأمر.",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=update.message.message_id)
            return

        # التحقق إذا كان الأمر هو "/tts" بدون نص
        if not context.args:
            current_tts_model = context.user_data.get("tts_model", "tts-1")
            current_voice = context.user_data.get("tts", "alloy")
            await update.message.reply_text(
                f"⚙️ | إعدادات موديل TTS الحالي: \n<b>{
                    current_tts_model}</b>\n"
                f"🗣️ | إعدادات مؤلف الصوت الحالي: \n<b>{current_voice}</b>",
                parse_mode=ParseMode.HTML,
                reply_to_message_id=update.message.message_id)
            return

        # التحقق إذا كان الأمر هو "/tts" ويحتوي على مؤلف فقط
        if len(context.args) == 1 and context.args[0].startswith("<") and context.args[0].endswith(">"):
            voice = context.args[0][1:-1].lower()
            # حفظ المؤلف في context.user_data["tts"] للاستخدام المستقبلي
            context.user_data["tts"] = voice
            context.user_data["tts_model"] = "tts-1"
            await update.message.reply_text(
                f"✅️ | تم تعيين المؤلف إلى <b>{voice}</b>.",
                reply_to_message_id=update.message.message_id,
                parse_mode=ParseMode.HTML)
            return

        # التحقق إذا كان الأمر يحتوي على نوع الموديل
        if len(context.args) == 1 and context.args[0].startswith('["') and context.args[0].endswith('"]'):
            tts_model = context.args[0][2:-2]
            context.user_data["tts_model"] = tts_model
            await update.message.reply_text(
                f"✅️ | تم تعيين نموذج الصوت إلى <b>{tts_model}</b>.",
                reply_to_message_id=update.message.message_id,
                parse_mode=ParseMode.HTML)
            return

        # استخدام المؤلف المُفضل أو التلقائي إذا لم يكن هناك مؤلف محدد
        voice = context.user_data.get("tts", "alloy")
        tts_model = context.user_data.get("tts_model", "tts-1")

        text = " ".join(context.args)

        client = OpenAI(api_key=key)
        response_moderation = client.moderations.create(
            model="text-moderation-latest", input=text)
        output_moderation = response_moderation.results[0]
        if output_moderation.flagged:
            await update.message.reply_text(
                "❌️ | تم رفض طلبك نتيجة لنظام السلامة لدينا. "
                "قد تحتوي مطالبتك على نص غير مسموح به بواسطة نظام الأمان لدينا.",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=update.message.message_id)
            return

        # التحقق من رصيد المستخدم قبل توليد النص
        # Assuming initial balance is 5
        balance = context.user_data.get("balance", 5)

        # حساب تكلفة النص بناءً على سعر الكلمة
        cost_per_word = 0.0005
        word_count = len(text.split())
        total_cost = word_count * cost_per_word

        if balance < total_cost:
            await update.message.reply_text(
                "❌️ | رصيدك غير كافٍ لهذه العملية.",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=update.message.message_id)
            return

        # خصم تكلفة النص من رصيد المستخدم
        context.user_data["balance"] = max(0, balance - total_cost)

        # استخدام نموذج whisper-1 لتحويل النص إلى بصمة صوتية
        response = client.audio.speech.create(model=tts_model,  # استخدام النموذج المحدد
                                              voice=voice,
                                              input=text)

        # حفظ البصمة الصوتية في الملف المؤقت
        with tempfile.NamedTemporaryFile(suffix=".mp3",
                                         delete=True) as speech_file:
            response.stream_to_file(speech_file.name)

            # إرسال البصمة الصوتية كرسالة صوتية
            await update.message.reply_audio(
                title=update.message.message_id,
                performer=voice.capitalize(),  # تحديد المؤلف
                thumbnail=None,
                audio=open(speech_file.name, "rb"))

        # الملف سيتم حذفه تلقائيًا عندما يتم إغلاقه (بسبب delete=True عند إنشاء tempfile)

    except Exception as e:
        await update.message.reply_text(
            f"❌️ | `{e}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=update.message.message_id)


async def image_command(update: Update, context: CallbackContext):
    response = requests.get(URL, headers=HEADERS)
    try:
        key = context.user_data.get("authorize")
        if not key:
            await update.message.reply_text(
                "🔑 | تحتاج إلى تنشيط مفتاح API لاستخدام هذا الأمر.",
                reply_to_message_id=update.message.message_id)
            return

        if update.message.text == "/image":
            current_model = context.user_data.get("model_image", "2")
            await update.message.reply_text(
                f"ℹ️ | يتم استخدام نموذج DALL·E-{
                    current_model} كنموذج تلقائي لصنع الصور. يمكنك الاطلاع على التسعير الخاص بهذا النموذج من هنا:\nhttps://platform.openai.com/docs/guides/rate-limits",
                parse_mode=ParseMode.HTML)
            return

        prompt = " ".join(context.args) if context.args else None

        match = re.fullmatch(r'^<([^>]*)>$', prompt)
        if match:
            model_value = match.group(1).strip()

            if not model_value.isdigit() or int(model_value) <= 0:
                await update.message.reply_text(
                    "❌ | التنسيق غير صالح. الرجاء استخدام عدد صحيح موجب كإصدار نموذجي مثل <2> أو <3>.",
                    reply_to_message_id=update.message.message_id)
                return

            context.user_data["model_image"] = model_value
            await update.message.reply_text(
                f"✅️ | تم ضبط النموذج التلقائي على DALL·E-{
                    model_value}. يمكنك التحقق من أسعار هذا النموذج هنا:\nhttps://platform.openai.com/docs/guides/rate-limits",
                reply_to_message_id=update.message.message_id,
                parse_mode=ParseMode.HTML)
            return

        # Check if user has enough balance
        cost_per_image_dalle_2 = 0.018
        cost_per_image_dalle_3 = 0.040

        cost = 0.0

        current_model = context.user_data.get("model_image", "2")

        if current_model == "2":
            cost = cost_per_image_dalle_2
        elif current_model == "3":
            cost = cost_per_image_dalle_3

        # Check the user's balance
        # Assuming initial balance is 5
        balance = context.user_data.get("balance", 5)
        if balance < cost:
            await update.message.reply_text(
                "❌️ | رصيدك غير كافي لهذه العملية.",
                reply_to_message_id=update.message.message_id)
            return

        # Deduct the cost from the user's balance
        context.user_data["balance"] = max(0, balance - cost)

        client = OpenAI(api_key=key)

        # Use client.images.generate to create an image from the prompt
        response = client.images.generate(
            model=f"dall-e-{current_model}",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )

        image_url = response.data[0].url

        async with aiohttp.ClientSession() as session, session.get(
                image_url) as response:
            image_content = await response.content.read()

        image_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image_file.write(image_content)

        # Send the image as a photo
        await update.message.reply_photo(
            photo=open(image_file.name, "rb"),
            caption=f"<b>🖼 | مصنوع بواسطة DALL·E-{current_model}</b>",
            reply_to_message_id=update.message.message_id,
            parse_mode=ParseMode.HTML)

        image_file.close()

    except Exception as e:
        await update.message.reply_text(
            f"❌️ | `{e}`",
            reply_to_message_id=update.message.message_id, parse_mode=ParseMode.MARKDOWN)


async def audio_to_text_handler(update: Update, context: CallbackContext):
    response = requests.get(URL, headers=HEADERS)
    try:
        key = context.user_data.get("authorize")
        if not key:
            await update.message.reply_text(
                "🔑 | تحتاج الى تفعيل مفتاح التفويض بالبوت لأجل استخدام هذه الوظيفة.",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=update.message.message_id)
            return

        # Check if user_data["balance"] exists, otherwise set it to 5
        balance = context.user_data.get("balance", 5)

        media = update.message.audio or update.message.video or update.message.voice
        media_size = media.file_size or 0  # Use 0 if file_size is None

        # Check if the file size is 0, and deduct 0.05 from the user's balance
        if media_size == 0:
            balance -= 0.05

        # Check the file size
        size = 10
        max_size = size * 1024 * 1024
        if media_size > max_size:
            await update.message.reply_text(
                f"❌️ | حجم الملف كبير جدا. الحد الاقصى للحجم هو {
                    size} ميغابايت.",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=update.message.message_id)
            return

        # Check if user has enough balance
        cost_per_kb = 0.005
        cost = (media_size / (1024 * 1024) / 100000) * cost_per_kb
        if balance < cost:
            await update.message.reply_text(
                "❌️ | رصيدك غير كافٍ لهذه العملية.",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=update.message.message_id)
            return

        client = OpenAI(api_key=key)

        # Get the file ID
        file_id = media.file_id
        media_file = await context.bot.get_file(file_id)

        # Download the file as byte array
        media_data = await media_file.download_as_bytearray()

        # Save the media to a temporary file with a unique name
        media_file_name = f"temp/{uuid4()}.mp3"
        with open(media_file_name, "wb") as file:
            file.write(media_data)

        # Use the whisper-1 model from the openai library to transcribe the media
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(media_file_name, "rb"),
            timeout=30
        )

        # Get the transcribed text from the response
        text = response.text

        # Update the user's balance
        context.user_data["balance"] = max(0, balance - cost)

        await update.message.reply_text(text,
                                        reply_to_message_id=update.message.message_id,
                                        parse_mode=ParseMode.HTML)

    except Exception as e:
        await update.message.reply_text(
            f"❌️ | `{e}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=update.message.message_id)

    finally:
        # Delete the temporary file from the system
        if os.path.exists(media_file_name):
            os.remove(media_file_name)


async def share_command(update, context):
    response = requests.get(URL, headers=HEADERS)
    conversation = context.user_data.get("conversation", None)

    if not conversation:
        await update.message.reply_text(
            "ℹ️ | لا يوجد محتوى للمحادثة لمشاركته.",
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=update.message.message_id)
        return

    css_content = ""
    js_content = ""

    css_file_path = "application/style.css"
    js_file_path = "application/script.js"

    with open(css_file_path, "r", encoding="utf-8") as css_file:
        css_content = css_file.read()

    with open(js_file_path, "r", encoding="utf-8") as js_file:
        js_content = js_file.read()

    # Create a temporary HTML file
    # استخدم NamedTemporaryFile بدلاً من TemporaryFile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
        html_file_path = f.name  # احتفظ بمسار الملف HTML

        # Write the HTML document to the file
        f.write(f"""
            <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
                    <title>@{context.bot.username.upper()}</title>
                    <style>
                        {css_content}
                    </style>
                    <script type="text/javascript">
                        {js_content}
                    </script>
                </head>
                <body>
        """.encode("utf-8"))

        # Write the messages to the file
        for message in conversation:
            role = message.get("role")
            content = message.get("content")

            # Escape the markdown content as HTML
            content = mistune.markdown(content)

            if role == "user":
                f.write(
                    f"<div class='message user'><div class='content' dir='auto'>{content}</div></div>\n".encode("utf-8"))
            elif role == "assistant":
                f.write(
                    f"<div class='message assistant'><div class='content' dir='auto'>{content}</div></div>\n".encode("utf-8"))

        # Write the watermark to the file
        f.write(
            f"<div class='watermark'><a href='https://t.me/{update.message.from_user.username}'>@{update.message.from_user.username}</a></div>".encode("utf-8"))
        f.write(b"</body></html>")

    # Send the file as a document in Telegram
    with open(html_file_path, "rb") as html_file:
        await update.message.reply_document(document=html_file, reply_to_message_id=update.message.message_id)


# تعريف دالة لمعالجة أمر /clear
async def balance_command(update: Update, context: CallbackContext):
    response = requests.get(URL, headers=HEADERS)

    # قم بتعيين مفتاح "conversation" في بيانات المستخدم إلى None
    context.user_data["conversation"] = None

    # إذا لم يكن مفتاح "balance" موجودًا في بيانات المستخدم، فقم بإنشائه واضبط قيمته على 5
    # context.user_data["balance"] = 5

    # أرسل رسالة إلى المستخدم تؤكد أن المحادثة قد تم حذفها
    await update.message.reply_text(f"""رصيدك الحالي:
```
{context.user_data.get("balance", 5)}$
```


للحصول على معلومات إضافية حول Custo+، [انقر هنا](https://telegra.ph/Custo-12-21).""",
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=update.message.message_id)


# تعريف دالة لمعالجة أمر /clear
async def clear_command(update: Update, context: CallbackContext):

    # قم بتعيين مفتاح "conversation" في بيانات المستخدم إلى None
    context.user_data["conversation"] = None

    # إذا لم يكن مفتاح "balance" موجودًا في بيانات المستخدم، فقم بإنشائه واضبط قيمته على 5
    # context.user_data["balance"] = 5

    # أرسل رسالة إلى المستخدم تؤكد أن المحادثة قد تم حذفها
    await update.message.reply_text(
        "ℹ️ | تم حذف محتوى المحادثة وبدء محادثة جديدة.",
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=update.message.message_id)


async def json_command(update: Update, context: CallbackContext):
    response = requests.get(URL, headers=HEADERS)
    message = (
        f"<pre>context.chat_data = {html.escape(
            str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(
            str(context.user_data))}</pre>\n\n"
        f"<pre>context.bot_data = {html.escape(
            str(context.bot_data))}</pre>\n\n"
    )

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"<pre>{html.escape(json.dumps(update_str, indent=2,
                            ensure_ascii=False))}</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(
            str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(
            str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    await context.bot.send_message(chat_id=DEVELOPER_CHAT_ID,
                                   text=message,
                                   parse_mode=ParseMode.HTML)


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("/start", "ℹ️ رسالة البدء"),
        BotCommand("/tts", "🎧 تحويل النص الى كلام"),
        BotCommand("/image", "🖼 توليد صور"),

        BotCommand("/share", "💾 تصدير المحادثة"),
        BotCommand("/balance", "💵 عرض الرصيد"),
        BotCommand("/authorize", "🔑 تعيين مفتاح تفويض"),
        BotCommand("/customize", "👤 تعيين الشخصية"),
        BotCommand("/clear", "🔄 تجديد الدردشة"),
        BotCommand("/help", "ℹ️ مساعدة"),

        BotCommand("/settings", "⚙️ إعدادات البوت")
    ])


def main() -> None:
    persistence = PicklePersistence(filepath="arbitrarycallbackdatabot")
    application = (Application.builder().token(os.environ.get('BOT_TOKEN'))
                   .post_init(post_init).persistence(persistence).build())

    handler_list = [
        CommandHandler("start", start_command),
        CommandHandler("tts", tts_command),
        CommandHandler("image", image_command),
        CommandHandler("authorize", authorize_command),
        CommandHandler("customize", customize_command),
        CommandHandler("json", json_command),
        CommandHandler("clear", clear_command),
        CommandHandler("share", share_command),
        CommandHandler("balance", balance_command),
        # CommandHandler("add", add_command),
        CommandHandler("help", helps_command),
        CommandHandler("settings", helps_command),
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler),
        # MessageHandler(filters.AUDIO | filters.VIDEO | filters.VOICE, audio_to_text_handler),
    ]

    for handler in handler_list:
        application.add_handler(handler)

    application.add_error_handler(error_handler)
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
