# Script pour obtenir un refresh token compatible avec pydrive2/oauth2client
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
import json

# Charger la configuration client
with open('client_secrets.json', 'r') as f:
    client_config = json.load(f)['installed']

CLIENT_ID = client_config['client_id']
CLIENT_SECRET = client_config['client_secret']
SCOPES = ['https://www.googleapis.com/auth/drive']

# Configuration du flow OAuth2
flow = OAuth2WebServerFlow(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=SCOPES,
    redirect_uri='http://localhost',
    access_type='offline',
    prompt='consent'
)

# Obtenir l'URL d'autorisation
auth_url = flow.step1_get_authorize_url()
print("Veuillez visiter cette URL pour autoriser l'application:")
print(auth_url)
print("\nAprès autorisation, copiez le code de retour ici:")

# Saisir le code d'autorisation
code = input().strip()

# Échanger le code contre les tokens
credentials = flow.step2_exchange(code)

# Sauvegarder les credentials dans le format attendu par pydrive2
storage = Storage('credentials.json')
storage.put(credentials)

print("✅ Refresh token sauvegardé dans credentials.json (format compatible pydrive2)")