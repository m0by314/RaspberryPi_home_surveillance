#!/usr/bin/env python3
import unittest

import requests
import sys
import os

sys.path.insert(0, os.getcwd())

from lib.telebot import Telebot
from lib.camera import Camera
from lib.pir import Motiondetector
from lib.config import bot_id


if bot_id == 'Your_token_id':
    print("Variable bot_id is not defined in lib/config.py")
    sys.exit(1)


class TestBotMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response = requests.get("https://api.telegram.org/bot{TOKEN}/getMe".format(TOKEN=bot_id))
        cls.bot = Telebot(bot_id)
        if os.path.isfile('data.raw'):
            with open('data.raw') as fp:
                cls.chat_id = fp.read()
        else:
            cls.chat_id = requests.get("https://api.telegram.org/bot{TOKEN}/getUpdates".format(TOKEN=bot_id)) \
                    .json()['result'][0]['message']['chat']['id']
            with open('data.raw', 'w') as fp:
                fp.write(str(cls.chat_id))
        fp.close()

    def test_query_url(self):
        self.assertEqual(self.response.status_code, 200, "Cannot query url Telegram API Bot fail")

    def test_bot_query(self):
        self.assertEqual(self.bot.getMe(), self.response.json()['result'], "The response of the Telebot class \
                            and the Telegram url differs")

    def test_bot_status(self):
        self.assertEqual(self.bot.is_listen, 0, "Bot is listen")

    def test_set_start(self):
        self.bot.is_listen = True
        self.assertEqual(self.bot.is_listen, 1, "Cannot set Bot.is_listen to ON")

    def test_set_stop(self):
        self.bot.is_listen = False
        self.assertEqual(self.bot.is_listen, 0, "Cannot set Bot.is_listen to OFF")

    def test_handle(self):
        @self.bot.handler("/testsuite")
        def on_tests():
            return str("Test handler")

        msg = {'message_id': 305,
               'chat': {'id': self.chat_id, 'first_name': 'test', 'last_name': 'test', 'type': 'private'},
               'date': 1586725459, 'text': '/testsuite',
               'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]}
        self.assertEqual(self.bot._postreceive(msg), 0, "Handler doesn't function")

    def test_handler_photo(self):
        @self.bot.handler("/photo")
        def on_test_photo():
            return os.getcwd() + '/testsuite/logo-ok.png'

        msg = {'message_id': 305,
               'chat': {'id': self.chat_id, 'first_name': 'test', 'last_name': 'test', 'type': 'private'},
               'date': 1586725459, 'text': '/photo',
               'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]}
        self.assertEqual(self.bot._postreceive(msg), 0, "Handler photo doesn't function")


class TestCamera(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = os.getcwd() + '/tmp/video'
        cls.camera = Camera(10, cls.folder)

    def setUp(self) -> None:
        open(self.folder + "tests.txt", 'a').close()

    def test_recording(self):
        video = self.camera.start_recording()
        self.assertEqual(video["return_code"], 0, "ERROR: during recording video[\"return_code\"]")

    def test_take_photo(self):
        photo = self.camera.take_photo()
        self.assertTrue(os.path.isfile(photo))

    def test_purge_folder(self):
        self.assertEqual(self.camera.purge_records(), 'The records have been deleted', "purge_record doesn't function")


class TestPir(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pir = Motiondetector()

    def test_movement_detected(self):
        self.assertFalse(self.pir.movement_detected())


if __name__ == '__main__':
    unittest.main()