# -*- coding: utf-8 -*-

def post_init_hook_deposit(env):
    """Configura el producto Consumo de Acopio por defecto al instalar."""
    try:
        product = env.ref(
            'sale_customer_deposit.product_template_consumo_acopio',
            raise_if_not_found=False
        )
        if product:
            env['ir.config_parameter'].sudo().set_param(
                'sale_customer_deposit.deposit_service_product_id',
                str(product.product_variant_id.id),
            )
    except Exception:
        pass  # No fallar la instalación si hay error
