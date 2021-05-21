import logging
import configparser
import json
import select
import sys
import subprocess

from pircam import Pircam
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


# Enable logging
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('settings.ini')

pircam = None

class Modecam:
    bot = None
    allowed_users = []
    watching_users = []

    # Start handler to open new convertion with the bot.
    def start(self, update, context):
        user = update.message.from_user
        logger.info('Starting to talk with user %s, ID: %s',
                user['username'],
                user['id'])

        update.message.reply_text('Hi {}'.
                format(user['first_name']))

        print('')
        print('add user id {} ?'.format(user['id']))
        print('type y for yes or n for no')

        inp, outp, exception = select.select([sys.stdin], [], [], 5)

        if (inp and sys.stdin.readline().strip() == 'y'):
            self.allowed_users.append(user['id'])
            self.allowed_users.append(131211)

            config['DEFAULT']['AllowedUsers'] = json.dumps(self.allowed_users)
            with open('settings.ini', 'w') as configfile:
                config.write(configfile)

            print("User added")
        else:
            print("User was not added")

    def ping(self, update, context):
        user = update.message.from_user

        update.message.reply_text('Hello, up and running')

    def help(self, update, context):
        helpText = ('Available commands:\n' +
        '/watch - start watching\n' +
        '/off - stop watching\n' +
        '/ping - check ping\n' +
        'Or the following short forms:\n' +
        '/w - start watching\n' +
        '/o - stop watching\n')

        update.message.reply_text(helpText)

    # Handler to start observering
    def watch(self, update, context):
        user = update.message.from_user
        logger.info('Entering watch - %s', user['id'])

        # check user permissions
        if user['id'] in self.allowed_users:
            # check if user is already watching
            if user['id'] in self.watching_users:
                update.message.reply_text('already watching')
            else:
                # start new pircam if first user
                if len(self.watching_users) == 0:
                    pircam.start()

                self.watching_users.append(user['id'])
                update.message.reply_text('starting to watch')

        else:
            update.message.reply_text('you are not allowed to run this service')

        logger.info('currently watching users: %s', self.watching_users)


    # status handler
    def status(self, update, context):
        statusText = ''
        proc = subprocess.Popen(['./status.sh'], stdout=subprocess.PIPE)

        for line in proc.stdout:
            statusText += line.decode('utf-8') + '\n'

        update.message.reply_text(statusText)


    # Callback to send image
    def sendPicture(self, stream):
        if len(self.watching_users) == 0:
            logger.info('no one watching')
        else:
            logger.info('sending picture')

            for userId in self.watching_users:
                stream.seek(0)
                self.bot.send_photo(chat_id=userId, photo=stream)


    # Callback to send audio
    def sendAudio(self, stream):
        if len(self.watching_users) == 0:
            logger.info('no one watching')
        else:
            logger.info('sending voice message')

            for userId in self.watching_users:
                stream.seek(0)
                self.bot.send_voice(chat_id=userId, voice=stream)


    # Turn the watch handler off.
    def off(self, update, context):
        user = update.message.from_user
        logger.info('stop watching - %s', user['id'])

        if user['id'] in self.watching_users:
            self.watching_users.remove(user['id'])
            update.message.reply_text('stopped watching')

            if len(self.watching_users) == 0:
                logger.info('turning modecam off')
                update.message.reply_text('modecam turned off')
                pircam.stop()
            else:
                logger.info('modecam still on')

                update.message.reply_text('but modecam is still running')

        else:
            update.message.reply_text('you have not been watching')


    def error(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)


    def startBot(self):
        self.allowed_users = json.loads(config['DEFAULT']['AllowedUsers'])

        # Create the Updater
        updater = Updater(config['DEFAULT']['Token'], use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # start with the bot command
        dp.add_handler(CommandHandler("start", self.start))

        # help command
        dp.add_handler(CommandHandler("h", self.help))
        dp.add_handler(CommandHandler("help", self.help))

        # ping command
        dp.add_handler(CommandHandler("p", self.ping))
        dp.add_handler(CommandHandler("ping", self.ping))

        # status
        dp.add_handler(CommandHandler("stat", self.status))
        dp.add_handler(CommandHandler("status", self.status))

        # start to watch
        dp.add_handler(CommandHandler("w", self.watch))
        dp.add_handler(CommandHandler("watch", self.watch))

        # stop watching
        dp.add_handler(CommandHandler("o", self.off))
        dp.add_handler(CommandHandler("off", self.off))
        dp.add_handler(CommandHandler("stop", self.off))

        self.bot = dp.bot

        # log all errors
        dp.add_error_handler(self.error)
        logger.info('up and running')

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

# Create the telegram bot
modecam = Modecam()

pircam = Pircam(modecam,
            config['DEFAULT']['PirPin'],
            config['DEFAULT']['CameraDeviceIndex'],
            config['DEFAULT']['AudioDeviceIndex'])

modecam.startBot()
