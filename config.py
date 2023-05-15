import pyromod
from pyrogram import Client, filters

api_id = 123456789
api_hash = "..."

app = Client("my_account", api_id=api_id, api_hash=api_hash)
app_crash = Client("crash_recovery", api_id=api_id, api_hash=api_hash)
app_daivinchik = Client("daivinchik", api_id=api_id, api_hash=api_hash)
vinchik_id = 1234060895