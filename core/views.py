"""
Views pour le site vitrine OBVIO - Multi-page.
"""
import logging
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings

from .models import Contact

logger = logging.getLogger(__name__)


def home(request):
    """Page d'accueil."""
    return render(request, 'core/home.html')


def services(request):
    """Page Services."""
    return render(request, 'core/services.html')


def about(request):
    """Page À propos."""
    return render(request, 'core/about.html')


def contact(request):
    """
    Traite la soumission du formulaire de contact/demande de mise en relation.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', 'autre')
        message_text = request.POST.get('message', '').strip()

        # Validation des champs requis
        if not name:
            messages.error(request, "Veuillez fournir votre nom.", extra_tags="contact")
            return render(request, 'core/contact.html')
        
        if not email:
            messages.error(request, "Veuillez fournir une adresse e-mail valide.", extra_tags="contact")
            return render(request, 'core/contact.html')
        
        if not message_text:
            messages.error(request, "Veuillez décrire votre projet.", extra_tags="contact")
            return render(request, 'core/contact.html')

        try:
            # Vérifier si une demande récente existe déjà avec cet email
            recent_contact = Contact.objects.filter(
                email=email,
                status='new'
            ).first()
            
            if recent_contact:
                messages.warning(
                    request, 
                    "Vous avez déjà une demande en attente. Nous vous contacterons bientôt.", 
                    extra_tags="contact"
                )
                return redirect('core:contact')
            
            # Créer la nouvelle demande de contact
            contact_request = Contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message_text
            )
            
            # Envoyer un email de notification (si configuré)
            try:
                if settings.EMAIL_HOST:
                    send_mail(
                        subject=f'Nouvelle demande de contact - {contact_request.get_subject_display()}',
                        message=f"""
Nouvelle demande de mise en relation reçue:

Nom: {name}
Email: {email}
Téléphone: {phone}
Type de projet: {contact_request.get_subject_display()}

Message:
{message_text}

---
OBVIO Capital
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['info@obviocapital.com'],
                        fail_silently=True,
                    )
            except Exception as e:
                logger.warning(f"Erreur lors de l'envoi de l'email de notification: {e}")
            
            messages.success(
                request, 
                "Merci ! Votre demande a bien été reçue. Nous vous contacterons rapidement.", 
                extra_tags="contact"
            )
            return redirect('core:contact')
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la demande de contact: {e}")
            messages.error(
                request, 
                "Une erreur s'est produite. Veuillez réessayer ou nous contacter directement.", 
                extra_tags="contact"
            )

    return render(request, 'core/contact.html')