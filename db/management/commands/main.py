# Turn off bytecode generation
import sys

from django.core.exceptions import ObjectDoesNotExist

sys.dont_write_bytecode = True

# Django specific settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import django

django.setup()

# Import your models for use in your script
import datetime
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand
from django_q.models import Schedule
from telegram import Bot, Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)
from telegram.utils.request import Request
from django.utils import timezone
from db.models import Profile

GIVEN_ID = 403839849

#GIVEN_ID = -1001192018710

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def remind_duty():
    # Telegram bot SETTINGS
    token = settings.TOKEN
    request = Request(
        connect_timeout=0.5,
        read_timeout=1.0
    )
    bot = Bot(
        request=request,
        token=token
    )

    weekday = date.today().weekday()
    if weekday < 6:
        p = Profile.objects.order_by('duty').first()
        prev_date_of_profile = p.duty.strftime('%m/%d/%y')
        p.duty = p.duty.strptime(prev_date_of_profile, '%m/%d/%y') + datetime.timedelta(days=7)
        if datetime.datetime.now().strftime("%H:%M") >= "00:00":
            p.save()
        print('here')
        message = f"Bugun, {p}\n" \
                  f"https://telegra.ph/Navbatchi-Vazifalari-06-24"
        bot.send_message(chat_id=GIVEN_ID, text=message)


def todays_duty(update: Update, context: CallbackContext):
    weekday = date.today().weekday()
    if weekday < 6:
        p = Profile.objects.order_by('duty').first()
        text = f"Bugungi, <b>{p}!</b>"
    else:
        text = f"Bugun Yakshanbaku!"
    update.message.reply_text(text=text, parse_mode=ParseMode.HTML)


def tomorrow_duty(update: Update, context: CallbackContext):
    weekday = date.today().weekday()
    if weekday < 6:
        p = Profile.objects.order_by('duty').first()
        try:
            next_one = Profile.objects.get(id=p.id + 1)
        except ObjectDoesNotExist:
            next_one = Profile.objects.get(id=1)
        cur_duty = next_one.duty.strftime('%m/%d/%y')
        next_one.duty = next_one.duty.strptime(cur_duty, '%m/%d/%y') + datetime.timedelta(days=7)
        next_one.save()
        text = f"{p} yo'qligi sabab, Yangi {next_one}"
    else:
        text = f"Bugun Yakshanbaku!"
    update.message.reply_text(text=text, parse_mode=ParseMode.HTML)


class Command(BaseCommand):
    help = 'Telegram_bot'

    def handle(self, *args, **options):
        try:
            now2 = timezone.now()
            date2 = datetime.datetime(now2.year, now2.month, now2.day)
            next_d = date2.replace(hour=9, minute=0, second=0)
            Schedule.objects.update_or_create(
                func='db.management.commands.main.remind_duty',
                defaults={
                    'schedule_type': Schedule.DAILY,
                    'repeats': -1,
                    'next_run': next_d
                }
            )

        except Exception as e:
            print(e)

        token = settings.TOKEN
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0
        )
        bot = Bot(
            request=request,
            token=token
        )

        updater = Updater(bot=bot, use_context=True)
        dispatcher = updater.dispatcher
        today_duty_handler = CommandHandler('today', todays_duty)
        next_handler = CommandHandler('next', tomorrow_duty)
        start_handler = CommandHandler('start', start)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(today_duty_handler)
        dispatcher.add_handler(next_handler)

        updater.start_polling()
        updater.idle()
