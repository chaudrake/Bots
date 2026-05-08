# Le script envoie 8 tweets. 1 toutes les 60 mn.
import os
import sys
import logging
import time
import re
import pandas as pd
from dotenv import load_dotenv
import tweepy
from datetime import datetime

# Configuration - le script se trouve déjà dans le bon dossier
# Pas besoin de changer de répertoire, on utilise le dossier courant
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(WORKING_DIR, 'log.log')
EXCEL_FILE = os.path.join(WORKING_DIR, 'elus-deputes-depCorrige.csv')
TWEETED_DEPUTES_FILE = os.path.join(WORKING_DIR, 'tweeted_deputes.txt')

# Pour changer l'intervalle, changer le 1er chiffre. Par exemple 15 * 60 pour un tweet toutes les 15 mn
TWEET_INTERVAL = 60 * 60
TWEET_COUNT = 8

# API Twitter
ACCESS_KEY = os.getenv('DEPUTE_ACCESS_KEY')
ACCESS_SECRET = os.getenv('DEPUTE_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('DEPUTE_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('DEPUTE_CONSUMER_SECRET')

# Le reste du script reste IDENTIQUE à la version précédente
# (toutes les fonctions format_departement, read_excel_data, etc.)
