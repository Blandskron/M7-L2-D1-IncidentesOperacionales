# Sistema de Registro de Incidentes Operacionales (Django + PostgreSQL + ORM)

Este documento explica **todo lo que implementamos** en el proyecto **Sistema de Registro de Incidentes Operacionales**, enfocado en el objetivo del módulo:

* **2.1** Configurar Django para conectarse a **PostgreSQL** usando los componentes requeridos (psycopg2).
* **2.2** Definir un **modelo** que representa una **entidad sin relaciones**, especificando campos, tipos de datos y opciones.
* **2.3** Definir **llave primaria simple** y representar una “llave compuesta” (en Django se modela como **restricción de unicidad compuesta**, no como PK real).
* **2.4** Implementar **CRUD** sobre el modelo usando el **ORM** (Create / Read / Update / Delete).

---

## 1) Estructura general del proyecto

* **Proyecto Django:** `config`
* **Aplicación:** `incidents`
* **Entidad única sin relaciones:** `Incident`
* **Base de datos:** PostgreSQL (`incidents_db`)
* **Variables sensibles/configuración:** `.env`
* **CRUD por ORM:** comando custom `incidents_crud_demo`

---

## 2) Dependencias del proyecto

### `requirements.txt`

```txt
Django>=5.0,<6.0
psycopg2-binary>=2.9
python-dotenv>=1.0
```

**Qué aporta cada dependencia:**

* **Django:** framework principal y ORM.
* **psycopg2-binary:** driver para conectar Django con PostgreSQL.
* **python-dotenv:** permite cargar variables desde un archivo `.env` al entorno de ejecución.

---

## 3) Archivo `.env` (configuración externa)

### `.env`

```env
DJANGO_SECRET_KEY=django-insecure-!a@1jv!7jlr=iwt2r_hw7o)pe#5uad54_^gxl6j@u=h3t#*ibd
DJANGO_DEBUG=1

DB_NAME=incidents_db
DB_USER=postgres
DB_PASSWORD=admin1234
DB_HOST=127.0.0.1
DB_PORT=5432
```

**Qué resolvemos con `.env`:**

* Evitamos hardcodear credenciales en `settings.py`.
* Centralizamos configuración de BD (host, puerto, usuario, clave).
* Podemos cambiar configuración sin tocar código (ideal para dev vs prod).

---

## 4) Configuración en `config/settings.py`

Este archivo es el núcleo de configuración de Django. Aquí hicimos **dos cosas clave**:

1. **Cargar `.env` de forma segura** desde la raíz del proyecto usando `BASE_DIR`.
2. Configurar **SECRET_KEY**, **DEBUG** y **DATABASES** leyendo variables con `os.getenv`.

### Fragmento usado (explicado por partes)

#### 4.1 BASE_DIR y carga del `.env`

```python
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
```

* `BASE_DIR` apunta a la carpeta raíz del proyecto (donde está `manage.py`).
* `load_dotenv(BASE_DIR / ".env")` fuerza a cargar **ese** `.env` exacto.

  * Esto evita el típico problema de Windows: “no encuentra el `.env`” si el comando se ejecuta desde otra ruta.

#### 4.2 SECRET_KEY y DEBUG desde `.env`

```python
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"
```

* `SECRET_KEY`: se toma desde `.env`. Si no existe, usa un valor fallback seguro para desarrollo.
* `DEBUG`: convertimos `"1"`/`"0"` a boolean (`True`/`False`) usando comparación.

✅ **Importante (bug que corregimos):**
Antes estaba esto:

```python
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", SECRET_KEY)
```

Eso rompe porque en ese punto `SECRET_KEY` **todavía no existía**.

#### 4.3 INSTALLED_APPS (registrar la app `incidents`)

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'incidents',
]
```

Agregar `'incidents'` permite que Django:

* detecte el modelo,
* genere migraciones,
* y gestione la app.

#### 4.4 Configuración de PostgreSQL en `DATABASES`

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "incidents_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
```

Esto cumple el **CE 2.1**:

* Django usa `ENGINE = django.db.backends.postgresql`
* Los datos reales salen del `.env`.

---

## 5) Modelo ORM: entidad sin relaciones

### `incidents/models.py`

El modelo `Incident` representa una entidad **independiente** (sin ForeignKeys ni ManyToMany). Cumple el **CE 2.2** y parte del **CE 2.3**.

**Qué incluye:**

* Campos con tipos correctos: `DateTimeField`, `CharField`, `TextField`, `BooleanField`.
* Opciones: `default`, `choices`, `db_index`, `help_text`, `auto_now_add`, `auto_now`.
* **PK simple explícita:** `inc_id = AutoField(primary_key=True)`

#### 5.1 Llave primaria simple (PK)

```python
inc_id = models.AutoField(primary_key=True)
```

Esto crea una PK numérica autoincremental: `inc_id`.

#### 5.2 “Llave compuesta” en Django (restricción compuesta)

Django **no soporta** llave primaria compuesta nativa. Para representar el concepto académico de “llave compuesta”, usamos una **restricción de unicidad compuesta**:

```python
constraints = [
    models.UniqueConstraint(
        fields=["date", "incident_type", "responsible"],
        name="uq_incident_date_type_responsible",
    )
]
```

Esto significa:

* No se permite guardar dos registros con **la misma combinación** de:

  * `date`
  * `incident_type`
  * `responsible`

✅ Cumple el espíritu del **CE 2.3** (llaves compuestas) dentro del enfoque correcto del ORM de Django.

#### 5.3 Choices (tipos y estados)

Usamos `TextChoices` para controlar valores permitidos:

* `IncidentType`: FALLA, SEGURIDAD, OPERACION, OTRO
* `IncidentStatus`: ABIERTO, EN_PROCESO, RESUELTO, CERRADO

Esto evita strings libres, hace el modelo más consistente y mejora admin.

---

## 6) Registro en Django Admin (inspección + gestión rápida)

### `incidents/admin.py`

```python
@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("inc_id", "date", "incident_type", "status", "responsible", "is_active")
    list_filter = ("incident_type", "status", "is_active")
    search_fields = ("description", "responsible")
    ordering = ("-date", "-inc_id")
```

Qué logramos:

* `list_display`: columnas principales visibles.
* `list_filter`: filtros por tipo/estado/activo.
* `search_fields`: búsqueda por texto.
* `ordering`: orden descendente.

Esto apoya el trabajo de CRUD y auditoría visual del modelo.

---

## 7) CRUD con ORM: comando `incidents_crud_demo`

Para demostrar el **CE 2.4 (CRUD)**, creamos un comando custom en:

`incidents/management/commands/incidents_crud_demo.py`

### ¿Qué hace?

Ejecuta CRUD completo:

1. **CREATE**: `Incident.objects.create(...)`
2. **READ**:

   * `Incident.objects.get(inc_id=...)`
   * `Incident.objects.filter(...).order_by(...)`
3. **UPDATE**:

   * `found.save(update_fields=[...])`
   * `Incident.objects.filter(...).update(...)`
4. **DELETE**:

   * `Incident.objects.filter(...).delete()`

### Diferencia entre `save()` y `update()`

* `save()`: trabaja con una instancia (objeto en memoria), ejecuta validaciones y actualiza `auto_now`.
* `update()`: actualiza directo en BD por query (más rápido, no llama `save()`).

---

## 8) Paso a paso de comandos usados

A continuación están **todos los comandos** típicos del flujo que usamos (y el orden recomendado).

### 8.1 Crear entorno virtual (Windows)

```bash
python -m venv venv
```

Activar:

* PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

* CMD:

```cmd
venv\Scripts\activate
```

### 8.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 8.3 Crear el proyecto Django

Desde la carpeta del proyecto (donde quedará `manage.py`):

```bash
django-admin startproject config .
```

### 8.4 Crear la app `incidents`

```bash
python manage.py startapp incidents
```

### 8.5 Configurar `settings.py`

* Agregar `incidents` en `INSTALLED_APPS`
* Configurar `load_dotenv(BASE_DIR / ".env")`
* Configurar `DATABASES` PostgreSQL

### 8.6 Crear la base de datos en PostgreSQL

Ejemplo (en consola SQL / pgAdmin):

```sql
CREATE DATABASE incidents_db;
```

### 8.7 Crear migraciones (detecta el modelo)

```bash
python manage.py makemigrations
```

### 8.8 Ejecutar migraciones (crea tablas en PostgreSQL)

```bash
python manage.py migrate
```

### 8.9 Probar CRUD por comando (ORM)

```bash
python manage.py incidents_crud_demo
```

### 8.10 Crear superusuario para admin

```bash
python manage.py createsuperuser
```

### 8.11 Levantar servidor

```bash
python manage.py runserver
```