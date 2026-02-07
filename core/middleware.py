"""
Middleware pour la détection automatique de la langue du visiteur basée sur sa devise.
La détection principale se fait côté client (JavaScript) pour une meilleure performance.
Ce middleware sert de fallback si JavaScript est désactivé.
"""
import json
import logging
from urllib.request import urlopen
from urllib.error import URLError
from django.conf import settings
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


class AutoLanguageMiddleware:
    """
    Détecte automatiquement la langue du visiteur basée sur :
    1. La devise du pays du visiteur (détectée via IP géolocalisation)
    2. Redirige vers l'URL avec le préfixe de langue approprié
    
    IMPORTANT: La détection principale se fait côté client (JavaScript) pour éviter
    de bloquer le rendu de la page. Ce middleware sert de fallback pour les utilisateurs
    sans JavaScript.
    
    Ne redirige QUE lors de la première visite (pas de cookie 'obvio_lang_detected').
    Une fois que le visiteur navigue sur le site, il peut changer de langue librement.
    """
    
    COOKIE_NAME = 'obvio_lang_detected'
    
    # Mapping des devises vers les langues supportées
    CURRENCY_TO_LANGUAGE = {
        # Devises arabes → Arabe (ar)
        'AED': 'ar', 'SAR': 'ar', 'QAR': 'ar', 'KWD': 'ar', 'BHD': 'ar',
        'OMR': 'ar', 'JOD': 'ar', 'LBP': 'ar', 'SYP': 'ar', 'IQD': 'ar',
        'YER': 'ar', 'EGP': 'ar', 'SDG': 'ar', 'LYD': 'ar', 'TND': 'ar',
        'DZD': 'ar', 'MAD': 'ar', 'MRU': 'ar',
        
        # Devises francophones → Français (fr)
        'XOF': 'fr', 'XAF': 'fr', 'KMF': 'fr', 'DJF': 'fr', 'GNF': 'fr',
        'MGA': 'fr', 'RWF': 'fr', 'BIF': 'fr', 'HTG': 'fr', 'XPF': 'fr',
        'CFP': 'fr', 'CHF': 'fr',
        
        # Devises anglophones → Anglais (en)
        'USD': 'en', 'GBP': 'en', 'AUD': 'en', 'CAD': 'en', 'NZD': 'en',
        'SGD': 'en', 'HKD': 'en', 'ZAR': 'en', 'INR': 'en', 'PHP': 'en',
        'NGN': 'en', 'KES': 'en', 'GHS': 'en', 'ZMW': 'en', 'BWP': 'en',
        'MWK': 'en', 'UGX': 'en', 'TZS': 'en', 'JMD': 'en', 'TTD': 'en',
        'BBD': 'en', 'BSD': 'en', 'BZD': 'en', 'GYD': 'en', 'FJD': 'en',
        'LKR': 'en', 'PKR': 'en', 'BDT': 'en', 'MMK': 'en', 'MYR': 'en',
    }
    
    # Pays utilisant l'EUR avec langue française
    EUR_FRENCH_COUNTRIES = {'FR', 'BE', 'LU', 'MC'}
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        path = request.path_info
        
        # Ne pas traiter les URLs admin, static, media, i18n
        if any(path.startswith(p) for p in ['/admin/', '/static/', '/media/', '/i18n/']):
            return self.get_response(request)
        
        # Si le cookie existe, l'utilisateur a déjà été détecté (JS ou serveur)
        # Ne plus interférer avec ses choix de navigation
        if request.COOKIES.get(self.COOKIE_NAME):
            return self.get_response(request)
        
        # Fallback serveur : uniquement sur la page d'accueil sans préfixe de langue
        # Le JavaScript côté client gère la détection principale
        if path == '/':
            detected_lang = self.detect_language_from_currency(request)
            
            if detected_lang != 'fr':
                response = redirect(f'/{detected_lang}/')
            else:
                response = self.get_response(request)
            
            # Définir le cookie pour ne plus rediriger automatiquement
            response.set_cookie(
                self.COOKIE_NAME, 
                'true', 
                max_age=365 * 24 * 60 * 60,  # 1 an
                httponly=False,  # Accessible par JS pour synchronisation
                samesite='Lax'
            )
            return response
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """Récupère l'adresse IP du client (gère proxy/load balancer)."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
    
    def get_country_and_currency_from_ip(self, ip):
        """
        Utilise l'API ip-api.com pour obtenir le pays et la devise.
        Retourne (country_code, currency_code) ou (None, None) en cas d'erreur.
        """
        # Ne pas faire de requête pour les IPs locales
        if ip in ('127.0.0.1', 'localhost', '::1') or ip.startswith(('192.168.', '10.', '172.')):
            return (None, None)
        
        try:
            url = f'http://ip-api.com/json/{ip}?fields=status,countryCode,currency'
            with urlopen(url, timeout=2) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('status') == 'success':
                    return (data.get('countryCode', ''), data.get('currency', ''))
        except (URLError, json.JSONDecodeError, TimeoutError, Exception) as e:
            logger.warning(f"Erreur géolocalisation IP {ip}: {e}")
        
        return (None, None)
    
    def detect_language_from_currency(self, request):
        """Détecte la langue du visiteur basée sur la devise de son pays."""
        ip = self.get_client_ip(request)
        country_code, currency = self.get_country_and_currency_from_ip(ip)
        
        if not currency:
            return 'fr'  # Fallback français
        
        # Cas spécial EUR : dépend du pays
        if currency == 'EUR':
            return 'fr' if country_code in self.EUR_FRENCH_COUNTRIES else 'en'
        
        return self.CURRENCY_TO_LANGUAGE.get(currency, 'en')
