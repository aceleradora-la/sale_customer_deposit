# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # -------------------------------------------------------------------------
    # Parámetros de configuración (config_parameter para Selection)
    # -------------------------------------------------------------------------
    deposit_default_type = fields.Selection(
        selection=[
            ('fixed_pricelist', 'Lista de Precios Fija'),
            ('index_product', 'Producto Índice / Crédito Base'),
            ('fixed_quantities', 'Cantidades Fijas'),
        ],
        string='Tipo de Acopio por Defecto',
        config_parameter='sale_customer_deposit.deposit_default_type',
        default='fixed_pricelist',
    )
    deposit_default_index_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Producto Índice por Defecto',
        domain=[('type', '=', 'product')],
        help='Producto base para acopios tipo Índice (se usa al crear nuevos contratos)',
    )
    deposit_service_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Producto Consumo de Acopio',
        domain=[('type', '=', 'service')],
        help='Producto de servicio para la línea negativa de consumo. Debe tener Cuenta de Ingresos = Anticipo de Clientes.',
    )
    deposit_liability_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta Anticipo de Clientes',
        domain="[('deprecated', '=', False)]",
        help='Cuenta de pasivo para anticipos. Se asigna al producto Consumo de Acopio como Cuenta de Ingresos.',
    )

    # -------------------------------------------------------------------------
    # get_default_ para Many2one (config_parameter no soporta Many2one directo)
    # -------------------------------------------------------------------------
    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        index_product_id = ICP.get_param('sale_customer_deposit.deposit_default_index_product_id', default='0')
        service_product_id = ICP.get_param('sale_customer_deposit.deposit_service_product_id', default='0')
        liability_account_id = ICP.get_param('sale_customer_deposit.deposit_liability_account_id', default='0')
        res.update(
            deposit_default_index_product_id=int(index_product_id) if index_product_id.isdigit() else False,
            deposit_service_product_id=int(service_product_id) if service_product_id.isdigit() else False,
            deposit_liability_account_id=int(liability_account_id) if liability_account_id.isdigit() else False,
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param(
            'sale_customer_deposit.deposit_default_index_product_id',
            str(self.deposit_default_index_product_id.id) if self.deposit_default_index_product_id else '0',
        )
        ICP.set_param(
            'sale_customer_deposit.deposit_service_product_id',
            str(self.deposit_service_product_id.id) if self.deposit_service_product_id else '0',
        )
        ICP.set_param(
            'sale_customer_deposit.deposit_liability_account_id',
            str(self.deposit_liability_account_id.id) if self.deposit_liability_account_id else '0',
        )
        # Asignar cuenta de pasivo al producto Consumo de Acopio
        if self.deposit_service_product_id and self.deposit_liability_account_id:
            self._set_deposit_product_income_account()

    def _set_deposit_product_income_account(self):
        """Asigna la cuenta de pasivo (Anticipo) como Cuenta de Ingresos del producto."""
        product = self.deposit_service_product_id
        account = self.deposit_liability_account_id
        if not product or not account:
            return
        company = self.company_id or self.env.company
        # property_account_income_id es por compañía; al facturar, la línea negativa
        # debitada esta cuenta reduciendo el pasivo (Anticipo de Clientes)
        product.product_tmpl_id.with_company(company).write({
            'property_account_income_id': account.id,
        })
