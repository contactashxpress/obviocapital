from django.db import models


class Contact(models.Model):
    """
    Modèle pour stocker les demandes de contact/mise en relation avec les investisseurs.
    """
    SUBJECT_CHOICES = [
        ('startup', 'Startup & Entrepreneur'),
        ('pme', 'PME & ETI'),
        ('projet', 'Porteur de projet'),
        ('association', 'Association & ONG'),
        ('autre', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Nouvelle demande'),
        ('contacted', 'Contacté'),
        ('in_progress', 'En cours de traitement'),
        ('completed', 'Traité'),
        ('cancelled', 'Annulé'),
    ]
    
    name = models.CharField(
        max_length=255,
        verbose_name="Nom complet"
    )
    email = models.EmailField(
        verbose_name="Adresse e-mail"
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Téléphone"
    )
    subject = models.CharField(
        max_length=50,
        choices=SUBJECT_CHOICES,
        default='autre',
        verbose_name="Type de projet"
    )
    message = models.TextField(
        verbose_name="Message / Description du projet"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes internes"
    )
    
    class Meta:
        verbose_name = "Demande de contact"
        verbose_name_plural = "Demandes de contact"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%d/%m/%Y')})"
