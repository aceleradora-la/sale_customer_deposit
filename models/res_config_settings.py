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
        domain="[('account_type', 'in', ['liability_current', 'liability_non_current', 'liability_payable'])]",
        help='Cuenta de pasivo para anticipos. Se asigna al producto Consumo de Acopio como Cuenta de Ingresos.',
    )

    # -------------------------------------------------------------------------
    # get_default_/set_ para Many2one (patrón Odoo 19; config_parameter no soporta Many2one)
    # -------------------------------------------------------------------------
    @api.model
    def get_default_deposit_default_index_product_id(self):
        ICP = self.env['ir.config_parameter'].sudo()
        val = ICP.get_param('sale_customer_deposit.deposit_default_index_product_id', default='0')
        return {'deposit_default_index_product_id': int(val) if val and str(val).isdigit() else False}

    @api.model
    def get_default_deposit_service_product_id(self):
        ICP = self.env['ir.config_parameter'].sudo()
        val = ICP.get_param('sale_customer_deposit.deposit_service_product_id', default='0')
        return {'deposit_service_product_id': int(val) if val and str(val).isdigit() else False}

    @api.model
    def get_default_deposit_liability_account_id(self):
        ICP = self.env['ir.config_parameter'].sudo()
        val = ICP.get_param('sale_customer_deposit.deposit_liability_account_id', default='0')
        return {'deposit_liability_account_id': int(val) if val and str(val).isdigit() else False}

    def set_deposit_default_index_product_id(self):
        ICP = self.env['ir.config_parameter'].sudo()
        val = self.deposit_default_index_product_id
        ICP.set_param('sale_customer_deposit.deposit_default_index_product_id', str(val.id) if val else '0')

    def set_deposit_service_product_id(self):
        ICP = self.env['ir.config_parameter'].sudo()
        val = self.deposit_service_product_id
        ICP.set_param('sale_customer_deposit.deposit_service_product_id', str(val.id) if val else '0')
        if val and self.deposit_liability_account_id:
            self._set_deposit_product_income_account()

    def set_deposit_liability_account_id(self):
        ICP = self.env['ir.config_parameter'].sudo()
        val = self.deposit_liability_account_id
        ICP.set_param('sale_customer_deposit.deposit_liability_account_id', str(val.id) if val else '0')
        if self.deposit_service_product_id and val:
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
