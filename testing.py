import discord
import logging
from discord.ext import commands
import requests

API_KEY = 'aae20fe489b352655e5fcacbba53f140'  #API KEY
sport = 'basketball_nba'
response = requests.get(f'https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={API_KEY}&regions=us')
print(response.json())
