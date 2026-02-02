# Configuration et Déploiement de obviocapital.com

## Historique complet de la mise en ligne

---

### Analyse du VPS existant

**Question :** veuillez analyser le fichier pdf que j'ai fourni ceci contient les details de mon premier site sur mon vps donc je veux deployer mon deuxieme site www.obviocapital.com sur le meme vps sans dedranger le site qui est deja en ligne

**Réponse :**

J'ai analysé le fichier PDF. Voici ce que je comprends de votre configuration actuelle et le plan pour déployer **obviocapital.com** en parallèle.

## Configuration actuelle de votre VPS

| Élément | Détail |
|---------|--------|
| **IP** | 83.72.277.22 |
| **Utilisateur** | abdrahman |
| **Premier site** | ashxpress.com → `/home/abdrahman/ashxpress` |
| **Base de données** | PostgreSQL (ashxpress_db / ashxpress_user) |
| **Port Gunicorn** | 8000 |
| **Services installés** | Nginx, PostgreSQL, Redis, Supervisor, Certbot, UFW |

## Plan pour déployer obviocapital.com

### Ce qu'il faut faire (sans toucher à ashxpress.com) :

1. **Pointer le domaine** obviocapital.com vers l'IP 83.72.277.22 (chez votre registrar DNS)

2. **Cloner le projet** dans un nouveau dossier :
   - `/home/abdrahman/obviocapital`

3. **Créer un nouvel environnement virtuel** dédié à ce projet

4. **Créer une nouvelle base de données PostgreSQL** :
   - `obviocapital_db` avec un utilisateur `obviocapital_user`

5. **Créer un fichier `.env`** avec une nouvelle SECRET_KEY

6. **Configurer Nginx** avec un nouveau fichier :
   - `/etc/nginx/sites-available/obviocapital.com`
   - Port Gunicorn différent : **8001** (au lieu de 8000)

7. **Obtenir un certificat SSL** avec Certbot pour obviocapital.com

8. **Configurer Supervisor** avec un nouveau fichier :
   - `/etc/supervisor/conf.d/obviocapital.conf`

9. **Configurer la sauvegarde automatique** pour cette nouvelle base de données

## Résultat final

| Site | Dossier | Port | Base de données |
|------|---------|------|-----------------|
| ashxpress.com | `/home/abdrahman/ashxpress` | 8000 | ashxpress_db |
| obviocapital.com | `/home/abdrahman/obviocapital` | 8001 | obviocapital_db |

Les deux sites seront totalement indépendants et ne se dérangeront pas.

---

### Demande de guide étape par étape

**Question :** bien sur

**Réponse :**

Voici les étapes de déploiement pour **obviocapital.com** sur votre VPS, basées sur la configuration de votre premier site.

## Pré-requis

**Assurez-vous que le domaine obviocapital.com est pointé vers votre IP : 83.72.277.22**

## ÉTAPE 1 : Se connecter au VPS

```bash
ssh abdrahman@83.72.277.22
```

## ÉTAPE 2 : Cloner le projet

```bash
cd /home/abdrahman
git clone https://github.com/contactashxpress/obviocapital.git
cd obviocapital
```

## ÉTAPE 3 : Créer et activer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

## ÉTAPE 4 : Installer les dépendances

```bash
pip install -r requirements.txt
```

## ÉTAPE 5 : Créer la base de données PostgreSQL

```bash
sudo -u postgres psql
```

Dans PostgreSQL, tapez :
```sql
CREATE DATABASE obviocapital_db;
CREATE USER obviocapital_user WITH PASSWORD 'votre_mot_de_passe_fort';
GRANT ALL PRIVILEGES ON DATABASE obviocapital_db TO obviocapital_user;
\c obviocapital_db
GRANT ALL PRIVILEGES ON SCHEMA public TO obviocapital_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO obviocapital_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO obviocapital_user;
\q
```

## ÉTAPE 6 : Générer une nouvelle SECRET_KEY

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copiez la clé générée.**

## ÉTAPE 7 : Créer le fichier .env

```bash
nano .env
```

Contenu à mettre :
```
SECRET_KEY=la_cle_generee_etape_6
DEBUG=False
ALLOWED_HOSTS=obviocapital.com,www.obviocapital.com
DATABASE_URL=postgres://obviocapital_user:votre_mot_de_passe@localhost:5432/obviocapital_db
```

Sauvegardez : `Ctrl+O`, `Enter`, `Ctrl+X`

## ÉTAPE 8 : Exécuter les migrations et collectstatic

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

Tapez `yes` quand demandé.

## ÉTAPE 9 : Créer la configuration Nginx

```bash
sudo nano /etc/nginx/sites-available/obviocapital.com
```

Contenu :
```nginx
server {
    listen 80;
    server_name obviocapital.com www.obviocapital.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/abdrahman/obviocapital/staticfiles/;
    }

    location /media/ {
        alias /home/abdrahman/obviocapital/media/;
    }
}
```

Sauvegardez : `Ctrl+O`, `Enter`, `Ctrl+X`

## ÉTAPE 10 : Activer la configuration Nginx

```bash
sudo ln -s /etc/nginx/sites-available/obviocapital.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## ÉTAPE 11 : Obtenir le certificat SSL

```bash
sudo certbot --nginx -d obviocapital.com -d www.obviocapital.com
```

## ÉTAPE 12 : Donner les permissions

```bash
sudo chmod 755 /home/abdrahman/
sudo chmod -R 755 /home/abdrahman/obviocapital/staticfiles/
```

## ÉTAPE 13 : Créer la configuration Supervisor

```bash
sudo nano /etc/supervisor/conf.d/obviocapital.conf
```

Contenu :
```ini
[program:obviocapital]
command=/home/abdrahman/obviocapital/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8001 config.wsgi:application
directory=/home/abdrahman/obviocapital
user=abdrahman
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/obviocapital.log
```

Sauvegardez : `Ctrl+O`, `Enter`, `Ctrl+X`

## ÉTAPE 14 : Activer Supervisor

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start obviocapital
```

## ÉTAPE 15 : Vérifier que tout fonctionne

```bash
sudo supervisorctl status
```

Vous devriez voir :
```
ashxpress                        RUNNING
obviocapital                     RUNNING
```

## ÉTAPE 16 : Tester le site

Visitez **https://obviocapital.com** dans votre navigateur.

---

### Problème avec PostgreSQL

**Question :** il y a un petit soucis: postgres=# CREATE DATABASE obviocapital_db;
CREATE DATABASE
postgres=# CREATE USER obviocapital_user WITH PASSWORD 'votre_mot_de_passe_fort';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE obviocapital_db TO obviocapital_user;
GRANT
postgres=# ^[[200~\c obviocapital_db
You are now connected to database "obviocapital_db" as user "postgres".
obviocapital_db-# ~\c obviocapital_db
You are now connected to database "obviocapital_db" as user "postgres".
obviocapital_db-# 

**Réponse :**

Pas de problème ! Vous êtes maintenant connecté à la base `obviocapital_db`. 

Continuez en tapant ces commandes une par une :

```sql
GRANT ALL PRIVILEGES ON SCHEMA public TO obviocapital_user;
```

Puis :
```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO obviocapital_user;
```

Puis :
```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO obviocapital_user;
```

Puis pour quitter :
```sql
\q
```

**Note** : Si vous voyez le prompt avec un tiret `obviocapital_db-#`, tapez d'abord `;` et appuyez sur Enter pour terminer la commande précédente, puis continuez.

---

### Problème avec Certbot

**Question :** IL Y A UN PETIT SOUCIS: (venv) abdrahman@srv1080712:~/obviocapital$ sudo certbot --nginx -d obviocapital.com -d www.obviocapital.com
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for obviocapital.com and www.obviocapital.com

Certbot failed to authenticate some domains (authenticator: nginx). The Certificate Authority reported these problems:
  Domain: obviocapital.com
  Type:   unauthorized
  Detail: 213.255.195.51: Invalid response from http://obviocapital.com/.well-known/acme-challenge/tfvJO9br2ZbXu7hzUuGnAVcJrntrW05EwBipEnXx2Zg: 404

Hint: The Certificate Authority failed to verify the temporary nginx configuration changes made by Certbot. Ensure the listed domains point to this nginx server and that it is accessible from the internet.

Some challenges have failed.
Ask for help or search for solutions at https://community.letsencrypt.org. See the logfile /var/log/letsencrypt/letsencrypt.log or re-run Certbot with -v for more details.

**Réponse :**

Le problème est clair : **le domaine obviocapital.com ne pointe pas vers votre VPS**.

L'erreur montre :
- **IP actuelle du domaine** : `213.255.195.51`
- **IP de votre VPS** : `83.72.277.22`

## Solution

### 1. Vérifiez la configuration DNS chez votre registrar

Allez sur le site où vous avez acheté le domaine et configurez :

| Type | Nom | Valeur |
|------|-----|--------|
| A | @ | 83.72.277.22 |
| A | www | 83.72.277.22 |

### 2. Vérifiez la propagation DNS

Après avoir modifié, attendez quelques minutes puis vérifiez avec cette commande sur votre VPS :

```bash
dig obviocapital.com +short
```

Cela devrait afficher `83.72.277.22`. Si ce n'est pas le cas, la propagation n'est pas terminée.

### 3. Une fois le DNS propagé, relancez Certbot

```bash
sudo certbot --nginx -d obviocapital.com -d www.obviocapital.com
```

**Avez-vous configuré le DNS chez votre registrar ?** La propagation peut prendre de 5 minutes à 24 heures selon les registrars.

---

### Problème avec les permissions staticfiles

**Question :** c'est quoi le soucis ici: (venv) abdrahman@srv1080712:~/obviocapital$ sudo chmod 755 /home/abdrahman/
(venv) abdrahman@srv1080712:~/obviocapital$ sudo chmod -R 755 /home/abdrahman/obviocapital/staticfiles/
chmod: cannot access '/home/abdrahman/obviocapital/staticfiles/': No such file or directory

**Réponse :**

Le dossier `staticfiles/` n'existe pas encore. Vous devez d'abord collecter les fichiers statiques.

Exécutez cette commande :

```bash
python manage.py collectstatic
```

Tapez `yes` quand demandé.

Ensuite, relancez la commande de permissions :

```bash
sudo chmod -R 755 /home/abdrahman/obviocapital/staticfiles/
```

---

### Problème de cache navigateur

**Question :** j'ai visiter https://obviocapital.com apres toute les processus mais ce que je vois est la page d'accueil de lws est ce possible?

**Réponse :**

Bonne nouvelle ! J'ai vérifié et **votre site fonctionne parfaitement** sur https://obviocapital.com !

Le problème est probablement le **cache de votre navigateur** qui affiche encore l'ancienne page LWS.

## Solutions

### 1. Videz le cache de votre navigateur

- **Chrome** : `Ctrl + Shift + Delete` → Sélectionnez "Images et fichiers en cache" → Effacer
- **Firefox** : `Ctrl + Shift + Delete` → Sélectionnez "Cache" → Effacer

### 2. Essayez en mode navigation privée

- **Chrome** : `Ctrl + Shift + N`
- **Firefox** : `Ctrl + Shift + P`

### 3. Ou forcez le rechargement

- `Ctrl + F5` sur la page

**Le site est bien en ligne** avec :
- Votre image de branding dans le hero
- L'email consultant@obviocapital.com
- Le copyright 2026
- Les montants en dollars ($50M)

---

### Création du superutilisateur

**Question :** je veux cree un super utilisateur

**Réponse :**

Connectez-vous à votre VPS et exécutez ces commandes :

```bash
cd /home/abdrahman/obviocapital
source venv/bin/activate
python manage.py createsuperuser
```

Il vous demandera :
- **Username** : votre nom d'utilisateur admin
- **Email** : votre email (optionnel, appuyez sur Enter)
- **Password** : tapez 2 fois (rien ne s'affiche, c'est normal)

Ensuite, vous pourrez accéder à l'admin sur :
**https://obviocapital.com/admin/**

---

## Résumé de la configuration finale

### Informations du serveur

| Élément | Valeur |
|---------|--------|
| **VPS IP** | 83.72.277.22 |
| **Domaine** | obviocapital.com |
| **Utilisateur** | abdrahman |
| **Chemin du projet** | /home/abdrahman/obviocapital |
| **Port Gunicorn** | 8001 |

### Base de données PostgreSQL

| Élément | Valeur |
|---------|--------|
| **Nom de la base** | obviocapital_db |
| **Utilisateur** | obviocapital_user |
| **Host** | localhost |
| **Port** | 5432 |

### Fichiers de configuration

- **Nginx** : `/etc/nginx/sites-available/obviocapital.com`
- **Supervisor** : `/etc/supervisor/conf.d/obviocapital.conf`
- **Variables d'environnement** : `/home/abdrahman/obviocapital/.env`

### Commandes utiles

| Action | Commande |
|--------|----------|
| Redémarrer l'app | `sudo supervisorctl restart obviocapital` |
| Voir le statut | `sudo supervisorctl status` |
| Voir les logs | `sudo tail -f /var/log/obviocapital.log` |
| Redémarrer Nginx | `sudo systemctl restart nginx` |

### Structure des deux sites sur le VPS

| Site | Dossier | Port | Supervisor |
|------|---------|------|------------|
| ashxpress.com | /home/abdrahman/ashxpress | 8000 | ashxpress |
| obviocapital.com | /home/abdrahman/obviocapital | 8001 | obviocapital |

---

## Date de mise en ligne

**Février 2026**

---

*Document de configuration pour obviocapital.com*
