from django.db import models
from django.utils import timezone


class Incident(models.Model):
    """
    Entidad NO relacionada: Registro de incidentes operacionales.

    - PK simple: inc_id (AutoField) => llave primaria única.
    - "PK compuesta": Django NO soporta PK compuesta real.
      En su lugar, usamos una restricción de unicidad compuesta (UniqueConstraint)
      para representar una llave compuesta a nivel de reglas de negocio.
    """

    class IncidentType(models.TextChoices):
        FALLA = "FALLA", "Falla"
        SEGURIDAD = "SEGURIDAD", "Seguridad"
        OPERACION = "OPERACION", "Operación"
        OTRO = "OTRO", "Otro"

    class IncidentStatus(models.TextChoices):
        ABIERTO = "ABIERTO", "Abierto"
        EN_PROCESO = "EN_PROCESO", "En proceso"
        RESUELTO = "RESUELTO", "Resuelto"
        CERRADO = "CERRADO", "Cerrado"

    # 2.3 Llave primaria simple (explícita)
    inc_id = models.AutoField(primary_key=True)

    # 2.2 Campos, tipos y opciones
    date = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Fecha y hora del incidente (por defecto: ahora).",
    )

    incident_type = models.CharField(
        max_length=20,
        choices=IncidentType.choices,
        default=IncidentType.OTRO,
        db_index=True,
        help_text="Clasificación del incidente.",
    )

    description = models.TextField(
        help_text="Descripción detallada del incidente.",
    )

    status = models.CharField(
        max_length=20,
        choices=IncidentStatus.choices,
        default=IncidentStatus.ABIERTO,
        db_index=True,
        help_text="Estado del incidente.",
    )

    responsible = models.CharField(
        max_length=120,
        db_index=True,
        help_text="Persona responsable o asignada.",
    )

    # Opciones adicionales típicas
    is_active = models.BooleanField(
        default=True,
        help_text="Permite desactivar el registro sin eliminarlo (borrado lógico).",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación (automática).",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última modificación (automática).",
    )

    class Meta:
        db_table = "incidents"
        ordering = ["-date", "-inc_id"]

        # 2.3 "Llave compuesta" (en Django: restricción compuesta)
        # Ejemplo: No permitir dos incidentes del mismo tipo, misma fecha exacta y mismo responsable.
        constraints = [
            models.UniqueConstraint(
                fields=["date", "incident_type", "responsible"],
                name="uq_incident_date_type_responsible",
            )
        ]

    def __str__(self) -> str:
        return f"#{self.inc_id} {self.incident_type} - {self.status} ({self.responsible})"
