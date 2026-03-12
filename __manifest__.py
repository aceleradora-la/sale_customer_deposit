# -*- coding: utf-8 -*-
{
    'name': 'Acopios de Materiales (Customer Material Deposits)',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Gestión de acopios de materiales para tiendas de construcción',
    'description': """
Acopios de Materiales - Customer Material Deposits
==================================================

Permite gestionar contratos de acopio donde el cliente paga por adelantado
para congelar precios, cantidades o un valor de referencia, y retira los
materiales gradualmente en el futuro.

Tipos de acopio soportados:
- Lista de Precios Fija (Fixed Pricelist)
- Producto Índice / Crédito Base (Index Product)
- Cantidades Fijas (Fixed Quantities)
    """,
    'author': 'Aceleradora',
    'website': 'https://github.com/aceleradora-la/sale_customer_deposit',
    'license': 'LGPL-3',
    'depends': [
        'base_setup',
        'mail',
        'sale_management',
        'account',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/deposit_sequence.xml',
        'data/deposit_data.xml',
        'views/deposit_contract_views.xml',
        'views/deposit_ledger_views.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook_deposit',
}
