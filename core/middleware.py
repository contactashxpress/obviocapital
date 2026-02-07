"""
Middleware pour la détection automatique de la langue du visiteur basée sur sa devise.
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
    
    Ne redirige QUE lors de la première visite (pas de cookie 'obvio_lang_detected').
    Une fois que le visiteur navigue sur le site, il peut changer de langue librement.
    """
    
    COOKIE_NAME = 'obvio_lang_detected'
    
    # Mapping des devises vers les langues supportées
    # Devises arabes → Arabe
    # Devises francophones (EUR pour pays FR, XOF, XAF, etc.) → Français
    # Autres devises → Anglais
    CURRENCY_TO_LANGUAGE = {
        # Devises arabes → Arabe (ar)
        'AED': 'ar',  # Dirham des Émirats arabes unis
        'SAR': 'ar',  # Riyal saoudien
        'QAR': 'ar',  # Riyal qatari
        'KWD': 'ar',  # Dinar koweïtien
        'BHD': 'ar',  # Dinar bahreïni
        'OMR': 'ar',  # Rial omanais
        'JOD': 'ar',  # Dinar jordanien
        'LBP': 'ar',  # Livre libanaise
        'SYP': 'ar',  # Livre syrienne
        'IQD': 'ar',  # Dinar irakien
        'YER': 'ar',  # Riyal yéménite
        'EGP': 'ar',  # Livre égyptienne
        'SDG': 'ar',  # Livre soudanaise
        'LYD': 'ar',  # Dinar libyen
        'TND': 'ar',  # Dinar tunisien
        'DZD': 'ar',  # Dinar algérien
        'MAD': 'ar',  # Dirham marocain
        'MRU': 'ar',  # Ouguiya mauritanienne
        
        # Devises francophones → Français (fr)
        'XOF': 'fr',  # Franc CFA BCEAO (Sénégal, Côte d'Ivoire, Mali, Burkina Faso, etc.)
        'XAF': 'fr',  # Franc CFA BEAC (Cameroun, Gabon, Congo, Tchad, etc.)
        'KMF': 'fr',  # Franc comorien
        'DJF': 'fr',  # Franc djiboutien
        'GNF': 'fr',  # Franc guinéen
        'MGA': 'fr',  # Ariary malgache (Madagascar)
        'RWF': 'fr',  # Franc rwandais
        'BIF': 'fr',  # Franc burundais
        'HTG': 'fr',  # Gourde haïtienne
        'CFP': 'fr',  # Franc CFP (Polynésie française, Nouvelle-Calédonie)
        'XPF': 'fr',  # Franc CFP
        
        # Devises européennes/suisses → Français pour les pays francophones
        # Note: EUR sera traité spécialement par pays
        'CHF': 'fr',  # Franc suisse (Suisse a une partie francophone)
        
        # Devises anglophones → Anglais (en)
        'USD': 'en',  # Dollar américain
        'GBP': 'en',  # Livre sterling
        'AUD': 'en',  # Dollar australien
        'CAD': 'en',  # Dollar canadien
        'NZD': 'en',  # Dollar néo-zélandais
        'SGD': 'en',  # Dollar de Singapour
        'HKD': 'en',  # Dollar de Hong Kong
        'ZAR': 'en',  # Rand sud-africain
        'INR': 'en',  # Roupie indienne
        'PHP': 'en',  # Peso philippin
        'NGN': 'en',  # Naira nigérian
        'KES': 'en',  # Shilling kényan
        'GHS': 'en',  # Cedi ghanéen
        'ZMW': 'en',  # Kwacha zambien
        'BWP': 'en',  # Pula botswanais
        'MWK': 'en',  # Kwacha malawien
        'UGX': 'en',  # Shilling ougandais
        'TZS': 'en',  # Shilling tanzanien
        'JMD': 'en',  # Dollar jamaïcain
        'TTD': 'en',  # Dollar de Trinité-et-Tobago
        'BBD': 'en',  # Dollar barbadien
        'BSD': 'en',  # Dollar bahaméen
        'BZD': 'en',  # Dollar bélizien
        'GYD': 'en',  # Dollar guyanien
        'FJD': 'en',  # Dollar fidjien
        'LKR': 'en',  # Roupie srilankaise
        'PKR': 'en',  # Roupie pakistanaise
        'BDT': 'en',  # Taka bangladais
        'MMK': 'en',  # Kyat birman
        'MYR': 'en',  # Ringgit malaisien
    }
    
    # Pays utilisant l'EUR avec langue française
    EUR_FRENCH_COUNTRIES = {
        'FR',  # France
        'BE',  # Belgique
        'LU',  # Luxembourg
        'MC',  # Monaco
    }
    
    # Pays utilisant l'EUR avec langue anglaise (par défaut pour les autres pays EUR)
    # Tous les autres pays EUR → Anglais
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        path = request.path_info
        
        # Ne pas traiter les URLs admin, static, media, i18n
        if any(path.startswith(p) for p in ['/admin/', '/static/', '/media/', '/i18n/']):
            return self.get_response(request)
        
        # Si le cookie existe, l'utilisateur a déjà été redirigé une fois
        # Ne plus interférer avec ses choix de navigation
        if request.COOKIES.get(self.COOKIE_NAME):
            return self.get_response(request)
        
        # Première visite : détecter la langue via la devise et rediriger si nécessaire
        # Seulement sur la page d'accueil sans préfixe de langue
        if path == '/':
            detected_lang = self.detect_language_from_currency(request)
            
            # Créer la réponse avec redirection si langue différente du français
            if detected_lang != 'fr':
                response = redirect(f'/{detected_lang}/')
            else:
                response = self.get_response(request)
            
            # Définir le cookie pour ne plus rediriger automatiquement
            response.set_cookie(
                self.COOKIE_NAME, 
                'true', 
                max_age=365 * 24 * 60 * 60,  # 1 an
                httponly=True,
                samesite='Lax'
            )
            return response
        
        # Pour toutes les autres URLs, définir le cookie et continuer
        response = self.get_response(request)
        if not request.COOKIES.get(self.COOKIE_NAME):
            response.set_cookie(
                self.COOKIE_NAME, 
                'true', 
                max_age=365 * 24 * 60 * 60,
                httponly=True,
                samesite='Lax'
            )
        return response
    
    def get_client_ip(self, request):
        """
        Récupère l'adresse IP du client.
        Gère les cas de proxy/load balancer.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def get_country_and_currency_from_ip(self, ip):
        """
        Utilise l'API ip-api.com pour obtenir le pays et la devise à partir de l'IP.
        Retourne un tuple (country_code, currency_code) ou (None, None) en cas d'erreur.
        """
        # Ne pas faire de requête pour les IPs locales
        if ip in ('127.0.0.1', 'localhost', '::1') or ip.startswith('192.168.') or ip.startswith('10.'):
            return (None, None)
        
        try:
            # ip-api.com est gratuit pour un usage non-commercial (45 req/min)
            url = f'http://ip-api.com/json/{ip}?fields=status,countryCode,currency'
            with urlopen(url, timeout=2) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get('status') == 'success':
                    country_code = data.get('countryCode', '')
                    currency = data.get('currency', '')
                    return (country_code, currency)
        except (URLError, json.JSONDecodeError, TimeoutError) as e:
            logger.warning(f"Erreur lors de la géolocalisation IP {ip}: {e}")
        
        return (None, None)
    
    def detect_language_from_currency(self, request):
        """
        Détecte la langue du visiteur basée sur la devise de son pays.
        """
        ip = self.get_client_ip(request)
        country_code, currency = self.get_country_and_currency_from_ip(ip)
        
        # Si on n'a pas pu détecter la devise, fallback sur français
        if not currency:
            return 'fr'
        
        # Cas spécial pour l'EUR : dépend du pays
        if currency == 'EUR':
            if country_code in self.EUR_FRENCH_COUNTRIES:
                return 'fr'
            else:
                return 'en'
        
        # Chercher la devise dans le mapping
        if currency in self.CURRENCY_TO_LANGUAGE:
            return self.CURRENCY_TO_LANGUAGE[currency]
        
        # Devise non reconnue → Anglais par défaut
        return 'en'
