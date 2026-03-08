# sale_customer_deposit

Módulo Odoo para gestión de **Acopios de Materiales** (Customer Material Deposits) en tiendas de construcción.

## Versiones soportadas

| Rama   | Odoo |
|--------|------|
| 17.0   | Odoo 17 |
| 18.0   | Odoo 18 |
| 19.0   | Odoo 19 |

## Instalación

1. Clonar el repositorio en el directorio de addons de Odoo:
   ```bash
   git clone -b 17.0 https://github.com/aceleradora-la/sale_customer_deposit.git
   # o -b 18.0 / -b 19.0 según tu versión de Odoo
   ```
2. Actualizar la lista de aplicaciones.
3. Instalar el módulo "Acopios de Materiales (Customer Material Deposits)".

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
