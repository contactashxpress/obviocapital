"""
Context processors pour OBVIO.
"""

from django.conf import settings
from django.utils.translation import get_language
from .translations import get_translations


def translations(request):
    """
    Injecte les traductions dans tous les templates.
    Usage: {{ t.key_name }}
    """
    lang_code = get_language() or settings.LANGUAGE_CODE
    return {
        't': get_translations(lang_code),
        'current_lang': lang_code,
        'is_rtl': lang_code == 'ar',
        'available_languages': settings.LANGUAGES,
    }
