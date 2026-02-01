"""
Template tags pour l'internationalisation.
"""

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def get_path_without_lang(context):
    """
    Retourne le chemin URL sans le préfixe de langue.
    Exemple: /ar/contact/ -> /contact/
             /en/services/ -> /services/
             /contact/ -> /contact/
    """
    request = context.get('request')
    if not request:
        return '/'
    
    path = request.path
    
    # Liste des codes de langue (sauf la langue par défaut si prefix_default_language=False)
    lang_codes = [code for code, name in settings.LANGUAGES]
    
    # Retirer le préfixe de langue s'il existe
    for code in lang_codes:
        prefix = f'/{code}/'
        if path.startswith(prefix):
            return path[len(prefix) - 1:]  # Garde le / initial
        elif path == f'/{code}':
            return '/'
    
    return path


@register.simple_tag(takes_context=True)
def get_lang_url(context, lang_code):
    """
    Retourne l'URL complète pour une langue donnée.
    """
    request = context.get('request')
    if not request:
        return '/'
    
    # Obtenir le chemin sans préfixe de langue
    path = request.path
    lang_codes = [code for code, name in settings.LANGUAGES]
    
    for code in lang_codes:
        prefix = f'/{code}/'
        if path.startswith(prefix):
            path = path[len(prefix) - 1:]
            break
        elif path == f'/{code}':
            path = '/'
            break
    
    # Construire l'URL pour la nouvelle langue
    if lang_code == settings.LANGUAGE_CODE:
        # Langue par défaut : pas de préfixe
        return path
    else:
        # Autres langues : avec préfixe
        if path == '/':
            return f'/{lang_code}/'
        return f'/{lang_code}{path}'
