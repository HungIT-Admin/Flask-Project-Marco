import os
from urllib.parse import quote_plus
from datetime import timedelta

class Config:
    password = quote_plus("dfer?thunder2")
    SECRET_KEY = '-?7xDO72{o+ZWqDjd(c|c'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://thunderbyte:{password}@paragon.sui-inter.net:3306/mmeil_lager"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)