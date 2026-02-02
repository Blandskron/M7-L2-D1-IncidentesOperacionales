from django.core.management.base import BaseCommand
from django.utils import timezone

from incidents.models import Incident


class Command(BaseCommand):
    help = "Demostración CRUD del modelo Incident usando ORM (Create/Read/Update/Delete)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("== DEMO CRUD INCIDENTS =="))

        # ----------------------------
        # CREATE
        # ----------------------------
        self.stdout.write("\n[CREATE] creando incidente...")
        incident = Incident.objects.create(
            date=timezone.now(),
            incident_type=Incident.IncidentType.OPERACION,
            description="Se detecta interrupción intermitente en línea de proceso.",
            status=Incident.IncidentStatus.ABIERTO,
            responsible="Juan Pérez",
        )
        self.stdout.write(self.style.SUCCESS(f"Creado: {incident}"))

        # ----------------------------
        # READ (get / filter / all)
        # ----------------------------
        self.stdout.write("\n[READ] leyendo incidente por PK (get)...")
        found = Incident.objects.get(inc_id=incident.inc_id)
        self.stdout.write(self.style.SUCCESS(f"Encontrado: {found}"))

        self.stdout.write("\n[READ] filtrando por estado ABIERTO...")
        open_qs = Incident.objects.filter(status=Incident.IncidentStatus.ABIERTO).order_by("-date")
        self.stdout.write(self.style.SUCCESS(f"Total abiertos: {open_qs.count()}"))
        for i in open_qs[:5]:
            self.stdout.write(f" - {i.inc_id} | {i.incident_type} | {i.responsible} | {i.date}")

        # ----------------------------
        # UPDATE
        # ----------------------------
        self.stdout.write("\n[UPDATE] actualizando estado a EN_PROCESO...")
        found.status = Incident.IncidentStatus.EN_PROCESO
        found.save(update_fields=["status", "updated_at"])
        self.stdout.write(self.style.SUCCESS(f"Actualizado: {found}"))

        # También podemos actualizar con queryset
        self.stdout.write("\n[UPDATE] update por queryset (marcar is_active=False)...")
        Incident.objects.filter(inc_id=found.inc_id).update(is_active=False)
        found.refresh_from_db()
        self.stdout.write(self.style.SUCCESS(f"Actualizado is_active: {found.is_active}"))

        # ----------------------------
        # DELETE (físico)
        # ----------------------------
        self.stdout.write("\n[DELETE] eliminando registro (delete físico)...")
        deleted_count, _ = Incident.objects.filter(inc_id=found.inc_id).delete()
        self.stdout.write(self.style.SUCCESS(f"Eliminados: {deleted_count}"))

        self.stdout.write(self.style.SUCCESS("\n== FIN DEMO CRUD =="))
