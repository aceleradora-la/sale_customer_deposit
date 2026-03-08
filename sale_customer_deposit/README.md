# sale_customer_deposit

Módulo Odoo 17 para gestión de **Acopios de Materiales** (Customer Material Deposits) en tiendas de construcción.

## Instalación

1. Copiar el módulo en el directorio `addons` de Odoo.
2. Actualizar la lista de aplicaciones.
3. Instalar el módulo "Acopios de Materiales (Customer Material Deposits)".

## Dependencias

- `mail`
- `sale_management`
- `account`
- `stock`

## Estructura (Paso 1)

- **deposit.contract**: Contrato de acopio con 3 tipos (Lista de Precios Fija, Producto Índice, Cantidades Fijas).
- **deposit.ledger**: Libro mayor inmutable de movimientos.

## Menú

Ventas → Acopios → Contratos de Acopio
