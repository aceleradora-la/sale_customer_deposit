# -*- coding: utf-8 -*-

def post_init_hook_deposit(env):
    """Configura el producto Consumo de Acopio por defecto al instalar."""
    try:
        product = env.ref(
            'sale_customer_deposit.product_template_consumo_acopio',
            raise_if_not_found=False
        )
        if product and hasattr(product, 'product_variant_id'):
            variant = product.product_variant_id
            if variant:
                env['ir.config_parameter'].sudo().set_param(
                    'sale_customer_deposit.deposit_service_product_id',
                    str(variant.id),
                )
    except Exception:
        pass  # No fallar la instalación si hay error
