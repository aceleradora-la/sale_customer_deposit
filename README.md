# sale_customer_deposit

Módulo Odoo para gestión de **Acopios de Materiales** (Customer Material Deposits) en tiendas de construcción.

## Versiones soportadas

| Rama   | Odoo |
|--------|------|
| 17.0   | Odoo 17 |
| 18.0   | Odoo 18 |
| 19.0   | Odoo 19 |

## Instalación

**Importante:** El módulo está dentro de una subcarpeta. Hay dos opciones:

### Opción A: Agregar la carpeta del repo al addons path
```bash
git clone -b 19.0 https://github.com/aceleradora-la/sale_customer_deposit.git
# Agregar la ruta del repo al addons_path en odoo.conf o --addons-path
# Ejemplo: addons_path = /ruta/odoo/addons,/ruta/sale_customer_deposit
```

### Opción B: Copiar solo el módulo (recomendado)
```bash
git clone -b 19.0 https://github.com/aceleradora-la/sale_customer_deposit.git
cp -r sale_customer_deposit/sale_customer_deposit /ruta/odoo/addons/
# O en Windows: xcopy sale_customer_deposit\sale_customer_deposit C:\odoo\addons\sale_customer_deposit /E /I
```

2. Reiniciar Odoo y en **Aplicaciones** → **Actualizar lista de aplicaciones**
3. Buscar e instalar "Acopios de Materiales (Customer Material Deposits)"

## Estructura

- **sale_customer_deposit/**: Módulo principal (Core)
  - `deposit.contract`: Contrato de acopio
  - `deposit.ledger`: Libro mayor inmutable

## Dependencias

- `mail`
- `sale_management`
- `account`
- `stock`

## Autor

Aceleradora - https://github.com/aceleradora-la
