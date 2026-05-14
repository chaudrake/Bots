# Bots

EVITER LES CRON À LA MEME HEURE : CA FAIT BUGUER LES INSCRIPTIONS DANS LES INDEX.
CA NE CONCERNE QUE LES BOTS AVEC INDEX.

FAIRE MARCHER LES CRON depuis cron-jobs.org :
url : https://api.github.com/repos/chaudrake/Bots/actions/workflows/motsrares.yml/dispatches

paramètres avancés :
en tetes :
clé : Authorization
value : token MON_TOKEN
méthode : POST
corps :
{
  "ref": "main"
}


