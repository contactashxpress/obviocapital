from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Administration des demandes de contact."""
    
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Informations du demandeur', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Demande', {
            'fields': ('subject', 'message')
        }),
        ('Traitement', {
            'fields': ('status', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_contacted', 'mark_as_completed']
    
    @admin.action(description="Marquer comme contacté")
    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='contacted')
        self.message_user(request, f"{updated} demande(s) marquée(s) comme contacté(e)s.")
    
    @admin.action(description="Marquer comme traité")
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} demande(s) marquée(s) comme traitée(s).")
