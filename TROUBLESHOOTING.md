# Cómo encontrar el error en el log de Odoo

Cuando un módulo falla al instalarse, el mensaje de error aparece en el **log de Odoo**. Aquí cómo encontrarlo:

---

## Opción 1: Ejecutar Odoo desde la consola (recomendado)

Así ves el error en tiempo real:

```bash
# Windows (PowerShell o CMD)
cd C:\ruta\a\tu\odoo
python odoo-bin -c odoo.conf

# O si usás el ejecutable:
odoo-bin -c odoo.conf
```

Luego intentá instalar el módulo. El error aparecerá en la misma ventana de la consola.

---

## Opción 2: Buscar el archivo de log

El archivo de log suele estar en:

| Ubicación | Ruta típica |
|-----------|-------------|
| **odoo.conf** | Revisá el parámetro `logfile` en tu archivo de configuración |
| **Por defecto** | `~/.local/share/Odoo/filestore/NOMBRE_DB/` o en la carpeta del proyecto |
| **Docker** | `docker logs NOMBRE_CONTENEDOR` |
| **Windows** | `C:\Users\TU_USUARIO\AppData\Local\Odoo\` o donde indique odoo.conf |

### Buscar odoo.conf

```powershell
# Buscar en tu disco
Get-ChildItem -Path C:\ -Filter "odoo.conf" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
```

### Ver qué dice logfile en odoo.conf

```powershell
# Si encontraste odoo.conf:
Select-String -Path "C:\ruta\odoo.conf" -Pattern "logfile"
```

---

## Opción 3: Buscar errores en el log

Si tenés el archivo de log:

```powershell
# Ver las últimas 100 líneas (donde suele estar el error)
Get-Content "C:\ruta\odoo.log" -Tail 100

# Buscar líneas con "Error", "Traceback" o "sale_customer_deposit"
Select-String -Path "C:\ruta\odoo.log" -Pattern "Error|Traceback|sale_customer_deposit" -Context 0,5
```

---

## Opción 4: Modo debug en la interfaz web

1. Activar **modo desarrollador**: Ajustes → Activar modo desarrollador
2. Instalar el módulo
3. Si falla, a veces aparece un botón **"Ver error técnico"** o un mensaje más detallado

---

## Qué buscar en el error

- **`KeyError`** o **`xml_id not found`** → Referencia a un registro que no existe
- **`AttributeError`** → Cambio de API en la versión de Odoo
- **`ParseError`** o **`XML`** → Error en una vista o archivo de datos
- **`ImportError`** → Error en código Python del módulo

Copiá el mensaje de error completo (incluido el Traceback) para poder diagnosticarlo.
