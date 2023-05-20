import sys
import os

print(sys.prefix)

from whatsapp_api_client_python.API import GreenApi

from src_bot.common.messages import *
from src_bot.common.green_api import *
from src_bot.common.validators import *

from src_bot.common.google.api import GoogleSheetsAuthData
from src_bot.google.GoogleSheetSource import GoogleSheetSource


# def line_from_file_generator(path: str):
#     with open(path, "r") as file:
#         for line in file:
#             yield line.strip()


# if __name__ == "__main__":
# wa = GreenApi(
#     idInstance=ID_INSTANCE,
#     apiTokenInstance=API_TOKEN_INSTANCE
# )

# phone_dispenser = line_from_file_generator(PHONE_NUMBERS_SPAM_PATH)

# cache = set()
# for phone_number in phone_dispenser:
#     try:
#         phone_number = validate_phone(phone_number)
#         chatId: str = '{0}{1}'.format(phone_number, CHAT_ID_MOBILE_DOMAIN)
#         for i in range(25):
#             message = 'Привет, это уфанет бот. Это тестовое сообщение №{0} из 100'.format(i)
#             wa.sending.sendMessage(
#                 chatId=chatId,
#                 message=message
#             )
#             print(message)
#      except Exception as err:
#          log -> print(f"Sending message {err=}, {type(err)=}")
#          LOGGER TODO

# google = GoogleSheetSource(
#     GoogleSheetsAuthData(),
#     "1q509auOyUD5qwiKqwjOZfFmlFz73rmyiVp4AxQIcg7I",
#     "A:A",
# )
# for phone in google:
#     print(phone)



# def generalMailing():
#     cache = set()

#     wa = GreenApi (
#         idInstance=ID_INSTANCE,
#         apiTokenInstance=os.environ.get('GREEN_API_TOKEN') #API_TOKEN_INSTANCE
#     )

#     google = GoogleSheetSource(
#         GoogleSheetsAuthData(),
#         os.environ.get('GOOGLE_API_TOKEN'), #"1q509auOyUD5qwiKqwjOZfFmlFz73rmyiVp4AxQIcg7I",
#         "A:A",
#     )

#     for phone_number in google:
#         if phone_number in cache:
#             continue
#         cache.add(phone_number)

#         try:
#             phone_number = validate_phone(phone_number)
#             chatId: str = '{0}{1}'.format(phone_number, CHAT_ID_MOBILE_DOMAIN)
#             message = 'Привет, это уфанет бот. Это тестовое сообщение №{0} из 100'.format(i)
#             wa.sending.sendMessage(
#                 chatId=chatId,
#                 message=message
#             )
#         except Exception as err:
            #log -> print(f"Sending message {err=}, {type(err)=}")

