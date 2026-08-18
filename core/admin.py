from django.contrib import admin
from .models import Document, UE, ECUE, Student, StudentStat, Prize, QuizQuestion, QuizAnswer, QuizAttempt

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
