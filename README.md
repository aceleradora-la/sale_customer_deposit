# sale_customer_deposit

Módulo Odoo para gestión de **Acopios de Materiales** (Customer Material Deposits) en tiendas de construcción.

## Versiones soportadas

| Rama   | Odoo |
|--------|------|
| 17.0   | Odoo 17 |
| 18.0   | Odoo 18 |
| 19.0   | Odoo 19 |

## Instalación

1. Clonar en el directorio de addons de Odoo:
   ```bash
   cd /ruta/odoo/addons
   git clone -b 19.0 https://github.com/aceleradora-la/sale_customer_deposit.git
   ```
   (Usar `-b 18.0` o `-b 17.0` según tu versión de Odoo)

2. Reiniciar Odoo

3. En **Aplicaciones** → **Actualizar lista de aplicaciones**

4. Buscar e instalar "Acopios de Materiales (Customer Material Deposits)"

## Dependencias

- `base_setup`
- `mail`
- `sale_management`
- `account`
- `stock`

## Estructura

- **deposit.contract**: Contrato de acopio
- **deposit.ledger**: Libro mayor inmutable
- **deposit.contract.line**: Líneas para tipo Cantidades Fijas

## Menú

- Ventas → Acopios → Contratos de Acopio
- Ajustes → Acopios (configuración)

## Solución de problemas

Si la instalación falla, revisar el log de Odoo:
```bash
# Con odoo-bin en terminal, el error aparece en consola
# O revisar el archivo de log configurado en odoo.conf
```

Errores comunes:
- **Dependencias no instaladas**: Asegurarse de tener Ventas, Contabilidad e Inventario instalados
- **base_setup**: El módulo "Configuración" debe estar instalado (viene con Odoo)
- **Compatibilidad**: El mismo XML funciona en Odoo 17, 18 y 19 (sin `uom_po_id` deprecado en v19)

## Autor

Aceleradora - https://github.com/aceleradora-la
