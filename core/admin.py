from django.contrib import admin
from .models import (Document, UE, ECUE, Student, StudentStat, Prize, QuizQuestion, QuizAnswer,
                     QuizAttempt, JIEdition, JIPayment, JIPhoto)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'semester', 'ecue', 'upload_date')
    list_filter = ('category', 'level', 'semester', 'ecue')
    search_fields = ('title', 'description', 'ecue__name', 'ecue__ue__name')
    date_hierarchy = 'upload_date'
    ordering = ('-upload_date',)


@admin.register(UE)
class UEAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level', 'semester')
    list_filter = ('level', 'semester')
    search_fields = ('code', 'name')
    prepopulated_fields = { 'slug': ('name',) }


@admin.register(ECUE)
class ECUEAdmin(admin.ModelAdmin):
    list_display = ('name', 'ue')
    list_filter = ('ue__level', 'ue__semester', 'ue')
    search_fields = ('name', 'ue__name', 'ue__code')
    prepopulated_fields = { 'slug': ('name',) }


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'level', 'created_at')
    list_filter = ('level',)
    search_fields = ('first_name', 'last_name', 'student_id')
    # Champ mot de passe en écriture seule : haché automatiquement à l'enregistrement
    readonly_fields = ('password_display',)
    fields = ('first_name', 'last_name', 'level', 'student_id', 'password', 'password_display')

    @admin.display(description='Mot de passe (état)')
    def password_display(self, obj):
        if obj.password:
            from django.contrib.auth.hashers import identify_hasher
            try:
                identify_hasher(obj.password)
                return '✓ Haché'
            except ValueError:
                return '⚠️ En clair (sera haché au prochain enregistrement)'
        return '—'

    def save_model(self, request, obj, form, change):
        raw = form.cleaned_data.get('password')
        if raw:
            obj.set_password(raw)
        super().save_model(request, obj, form, change)


@admin.register(StudentStat)
class StudentStatAdmin(admin.ModelAdmin):
    list_display = ('student', 'month', 'visits', 'seconds', 'score')
    list_filter = ('month',)
    search_fields = ('student__first_name', 'student__last_name', 'student__student_id')


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ('student', 'month', 'label', 'amount', 'awarded_at')
    list_filter = ('month',)
    search_fields = ('student__first_name', 'student__last_name')


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 3


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'ue', 'difficulty', 'created_at')
    list_filter = ('ue__level', 'ue', 'difficulty')
    search_fields = ('question', 'explanation')
    inlines = [QuizAnswerInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'ue', 'note', 'correct', 'total', 'difficulty', 'created_at')
    list_filter = ('ue', 'difficulty', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'student__student_id', 'ue__name')
    date_hierarchy = 'created_at'


# ===== Journée d'Intégration (JI-MIAGE) =====

class JIPhotoInline(admin.TabularInline):
    model = JIPhoto
    extra = 1
    fields = ('image_url', 'image', 'caption', 'order')


class JIPaymentInline(admin.TabularInline):
    model = JIPayment
    extra = 1
    fields = ('label', 'number', 'holder', 'link', 'instructions', 'is_active', 'order')


@admin.register(JIEdition)
class JIEditionAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'event_date', 'location', 'status', 'price', 'is_featured', 'order')
    list_filter = ('status', 'is_featured')
    search_fields = ('year', 'title', 'location')
    list_editable = ('is_featured', 'order')
    inlines = [JIPaymentInline, JIPhotoInline]
    fieldsets = (
        ('Identité', {'fields': ('year', 'title', 'subtitle', 'status', 'is_featured', 'order')}),
        ('Événement', {'fields': ('event_date', 'event_time', 'location', 'price', 'description')}),
        ('Affiche', {
            'fields': ('poster_url', 'poster'),
            'description': "Collez une URL d'image (recommandé : lien permanent) ou téléversez un fichier "
                           "(le fichier peut être perdu lors d'un redéploiement sur l'hébergement gratuit).",
        }),
    )


@admin.register(JIPayment)
class JIPaymentAdmin(admin.ModelAdmin):
    list_display = ('edition', 'label', 'number', 'holder', 'is_active', 'order')
    list_filter = ('is_active', 'edition')
    search_fields = ('label', 'number', 'holder')
    list_editable = ('is_active', 'order')


@admin.register(JIPhoto)
class JIPhotoAdmin(admin.ModelAdmin):
    list_display = ('edition', 'caption', 'image_url', 'order')
    list_filter = ('edition',)
    search_fields = ('caption',)
    list_editable = ('order',)
