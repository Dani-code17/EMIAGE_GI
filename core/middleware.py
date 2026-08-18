"""Middleware de suivi d'activité des étudiants connectés.

Comptabilise :
- une visite par jour calendaire (StudentStat.visits),
- le temps passé (StudentStat.seconds) entre les requêtes (delta),
  avec un plafond de 10 min par intervalle et un flush par paquets de 60 s.

Le endpoint /espace/heartbeat/ (appelé par le JS) rafraîchit activity_last
pour affiner la mesure du temps passé même sans navigation.
"""
from datetime import datetime

from django.utils import timezone


class StudentActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._track(request)
        return response

    def _track(self, request):
        student_id = request.session.get('student_id')
        if not student_id:
            return
        try:
            from .models import StudentStat

            now = timezone.now()
            month = now.strftime('%Y-%m')
            session = request.session

            # --- Temps passé ---
            last_raw = session.get('activity_last')
            if last_raw:
                try:
                    last = datetime.fromisoformat(last_raw)
                    delta = (now - last).total_seconds()
                except (ValueError, TypeError):
                    delta = 0
                # Ignore les écarts anormaux (onglet fermé puis revenu, veille…)
                if 1 <= delta <= 600:
                    pending = session.get('activity_pending', 0) + delta
                    if pending >= 60:
                        stat, _ = StudentStat.objects.get_or_create(
                            student_id=student_id, month=month
                        )
                        stat.seconds += int(pending)
                        stat.save(update_fields=['seconds'])
                        pending = 0
                    session['activity_pending'] = pending

            session['activity_last'] = now.isoformat()

            # --- Visite : une par jour ---
            today = now.strftime('%Y-%m-%d')
            if session.get('activity_day') != today:
                stat, _ = StudentStat.objects.get_or_create(student_id=student_id, month=month)
                stat.visits += 1
                stat.save(update_fields=['visits'])
                session['activity_day'] = today
        except Exception:
            # Ne jamais casser une page pour un problème de stats
            pass
