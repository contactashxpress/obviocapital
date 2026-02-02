"""
Middleware pour la détection automatique de la langue du visiteur.
"""
from django.conf import settings
from django.shortcuts import redirect


class AutoLanguageMiddleware:
    """
    Détecte automatiquement la langue du visiteur basée sur :
    1. L'en-tête Accept-Language du navigateur
    2. Redirige vers l'URL avec le préfixe de langue approprié
    
    Ne redirige QUE lors de la première visite (pas de cookie 'obvio_lang_detected').
    Une fois que le visiteur navigue sur le site, il peut changer de langue librement.
    """
    
    COOKIE_NAME = 'obvio_lang_detected'
    
    # Mapping des codes de langue Accept-Language vers nos langues supportées
    LANGUAGE_MAPPING = {
        # Arabe
        'ar': 'ar', 'ar-sa': 'ar', 'ar-ae': 'ar', 'ar-eg': 'ar', 'ar-ma': 'ar',
        'ar-dz': 'ar', 'ar-tn': 'ar', 'ar-kw': 'ar', 'ar-qa': 'ar', 'ar-bh': 'ar',
        'ar-om': 'ar', 'ar-jo': 'ar', 'ar-lb': 'ar', 'ar-sy': 'ar', 'ar-iq': 'ar',
        'ar-ly': 'ar', 'ar-sd': 'ar', 'ar-ye': 'ar',
        
        # Français
        'fr': 'fr', 'fr-fr': 'fr', 'fr-be': 'fr', 'fr-ch': 'fr', 'fr-ca': 'fr',
        'fr-lu': 'fr', 'fr-mc': 'fr', 'fr-sn': 'fr', 'fr-ci': 'fr', 'fr-ml': 'fr',
        'fr-cm': 'fr', 'fr-mg': 'fr', 'fr-cd': 'fr', 'fr-cg': 'fr', 'fr-ga': 'fr',
        'fr-bf': 'fr', 'fr-ne': 'fr', 'fr-tg': 'fr', 'fr-bj': 'fr', 'fr-gn': 'fr',
        'fr-ht': 'fr',
        
        # Anglais
        'en': 'en', 'en-us': 'en', 'en-gb': 'en', 'en-au': 'en', 'en-ca': 'en',
        'en-nz': 'en', 'en-ie': 'en', 'en-za': 'en', 'en-in': 'en', 'en-sg': 'en',
        'en-ph': 'en', 'en-ng': 'en', 'en-ke': 'en', 'en-gh': 'en',
    }
    
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
        
        # Première visite : détecter la langue et rediriger si nécessaire
        # Seulement sur la page d'accueil sans préfixe de langue
        if path == '/':
            detected_lang = self.detect_language(request)
            
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
    
    def detect_language(self, request):
        """
        Détecte la langue préférée du visiteur basée sur Accept-Language.
        """
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        
        if not accept_language:
            return 'fr'
        
        # Parser l'en-tête Accept-Language
        for part in accept_language.split(','):
            part = part.strip()
            if not part:
                continue
            
            # Extraire le code de langue (ignorer le q=)
            lang = part.split(';')[0].strip().lower()
            
            # Vérifier le mapping exact
            if lang in self.LANGUAGE_MAPPING:
                return self.LANGUAGE_MAPPING[lang]
            
            # Vérifier le code de base
            base_lang = lang.split('-')[0]
            if base_lang in self.LANGUAGE_MAPPING:
                return self.LANGUAGE_MAPPING[base_lang]
        
        return 'fr'
