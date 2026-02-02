# Déploiement OBVIO Capital

## Informations du serveur

| Élément | Valeur |
|---------|--------|
| **VPS IP** | 83.72.277.22 |
| **Domaine** | obviocapital.com |
| **Utilisateur** | abdrahman |
| **Chemin du projet** | /home/abdrahman/obviocapital |
| **Port Gunicorn** | 8001 |

---

## Base de données PostgreSQL

| Élément | Valeur |
|---------|--------|
| **Nom de la base** | obviocapital_db |
| **Utilisateur** | obviocapital_user |
| **Mot de passe** | (votre mot de passe) |
| **Host** | localhost |
| **Port** | 5432 |

---

## Fichiers de configuration

### Nginx
```
/etc/nginx/sites-available/obviocapital.com
```

### Supervisor
```
/etc/supervisor/conf.d/obviocapital.conf
```

### Variables d'environnement
```
/home/abdrahman/obviocapital/.env
```

---

## Commandes utiles

### Redémarrer l'application
```bash
sudo supervisorctl restart obviocapital
```

### Voir le statut
```bash
sudo supervisorctl status
```

### Voir les logs
```bash
sudo tail -f /var/log/obviocapital.log
```

### Redémarrer Nginx
```bash
sudo systemctl restart nginx
```

---

## Mise à jour du site

### 1. Se connecter au VPS
```bash
ssh abdrahman@83.72.277.22
```

### 2. Aller dans le projet et activer l'environnement
```bash
cd /home/abdrahman/obviocapital
source venv/bin/activate
```

### 3. Récupérer les modifications
```bash
git pull origin main
```

### 4. Installer les nouvelles dépendances (si nécessaire)
```bash
pip install -r requirements.txt
```

### 5. Exécuter les migrations (si nécessaire)
```bash
python manage.py migrate
```

### 6. Collecter les fichiers statiques (si nécessaire)
```bash
python manage.py collectstatic --noinput
```

### 7. Redémarrer l'application
```bash
sudo supervisorctl restart obviocapital
```

---

## Accès admin

- **URL** : https://obviocapital.com/admin/
- **Créer un superuser** :
```bash
cd /home/abdrahman/obviocapital
source venv/bin/activate
python manage.py createsuperuser
```

---

## Certificat SSL

Le certificat SSL est géré par Certbot et se renouvelle automatiquement.

### Renouvellement manuel (si nécessaire)
```bash
sudo certbot renew
```

### Vérifier le renouvellement automatique
```bash
sudo certbot renew --dry-run
```

---

## Structure des deux sites sur le VPS

| Site | Dossier | Port | Supervisor |
|------|---------|------|------------|
| ashxpress.com | /home/abdrahman/ashxpress | 8000 | ashxpress |
| obviocapital.com | /home/abdrahman/obviocapital | 8001 | obviocapital |

---

## Sauvegardes

Les sauvegardes de la base de données ashxpress sont automatiques vers Google Drive.

Pour ajouter obviocapital à la sauvegarde, modifiez le script :
```bash
nano ~/backup_db.sh
```

---

## Contact & Support

- **Email** : info@obviocapital.com
- **Email consultant** : consultant@obviocapital.com
- **Téléphone** : +48 573 508 442

---

## Date de mise en ligne

**Février 2026**

---

*Document généré pour la mise en production de obviocapital.com*
