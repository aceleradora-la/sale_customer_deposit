# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class DepositContract(models.Model):
    """
    Contrato de Acopio de Materiales.

    Representa el acuerdo entre el cliente y la empresa donde el cliente
    paga por adelantado para congelar precios/cantidades y retirar
    materiales gradualmente en el futuro.
    """
    _name = 'deposit.contract'
    _description = 'Contrato de Acopio de Materiales'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # -------------------------------------------------------------------------
    # Tipos de acopio y estados
    # -------------------------------------------------------------------------
    DEPOSIT_TYPE_SELECTION = [
        ('fixed_pricelist', 'Lista de Precios Fija'),
        ('index_product', 'Producto Índice / Crédito Base'),
        ('fixed_quantities', 'Cantidades Fijas'),
    ]

    STATE_SELECTION = [
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En Progreso'),
        ('closed', 'Cerrado'),
        ('cancelled', 'Cancelado'),
    ]

    # -------------------------------------------------------------------------
    # Campos básicos
    # -------------------------------------------------------------------------
    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nuevo'),
        tracking=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
        ondelete='restrict',
    )
    date = fields.Date(
        string='Fecha',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    deposit_type = fields.Selection(
        selection=DEPOSIT_TYPE_SELECTION,
        string='Tipo de Acopio',
        required=True,
        default='fixed_pricelist',
        tracking=True,
    )
    state = fields.Selection(
        selection=STATE_SELECTION,
        string='Estado',
        default='draft',
        required=True,
        copy=False,
        tracking=True,
    )

    # -------------------------------------------------------------------------
    # Campos según tipo de acopio
    # -------------------------------------------------------------------------
    # Fixed Pricelist: saldo en dinero + tarifa congelada
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Lista de Precios',
        ondelete='restrict',
        help='Tarifa congelada para descuento de retiros (tipo Lista de Precios Fija)',
    )
    amount_total = fields.Monetary(
        string='Monto Total',
        currency_field='currency_id',
        help='Saldo inicial en dinero (tipos Lista de Precios Fija y Producto Índice)',
    )
    amount_remaining = fields.Monetary(
        string='Saldo Restante',
        currency_field='currency_id',
        compute='_compute_amount_remaining',
        store=True,
        help='Saldo disponible para retiros',
    )

    # Index Product: producto base para conversión
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Producto Índice',
        ondelete='restrict',
        domain=[('type', '=', 'product')],
        help='Producto base para conversión de saldo a cantidades (tipo Producto Índice)',
    )
    quantity_index = fields.Float(
        string='Cantidad Índice',
        digits='Product Unit of Measure',
        help='Cantidades equivalentes del producto índice (tipo Producto Índice)',
    )
    quantity_index_remaining = fields.Float(
        string='Cantidad Índice Restante',
        digits='Product Unit of Measure',
        compute='_compute_quantity_index_remaining',
        store=True,
    )

    # Fixed Quantities: líneas de productos (se implementará en pasos posteriores)
    # deposit_line_ids = fields.One2many(...)

    # -------------------------------------------------------------------------
    # Campos contables y referencias
    # -------------------------------------------------------------------------
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        store=True,
    )
    advance_invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Factura de Anticipo',
        readonly=True,
        copy=False,
        help='Factura de cliente que fondea la cuenta de Pasivo (Anticipo de Clientes)',
    )

    # -------------------------------------------------------------------------
    # Relación con libro mayor (inmutable)
    # -------------------------------------------------------------------------
    ledger_line_ids = fields.One2many(
        comodel_name='deposit.ledger',
        inverse_name='contract_id',
        string='Movimientos del Libro Mayor',
        readonly=True,
    )

    # -------------------------------------------------------------------------
    # Computed
    # -------------------------------------------------------------------------
    @api.depends('amount_total', 'ledger_line_ids.amount')
    def _compute_amount_remaining(self):
        """Calcula el saldo restante en dinero según movimientos del ledger."""
        for contract in self:
            if contract.deposit_type in ('fixed_pricelist', 'index_product'):
                total_movements = sum(contract.ledger_line_ids.mapped('amount'))
                contract.amount_remaining = contract.amount_total + total_movements
            else:
                contract.amount_remaining = 0.0

    @api.depends('quantity_index', 'ledger_line_ids.quantity')
    def _compute_quantity_index_remaining(self):
        """Calcula la cantidad índice restante (tipo Producto Índice)."""
        for contract in self:
            if contract.deposit_type == 'index_product':
                total_qty = sum(contract.ledger_line_ids.mapped('quantity'))
                contract.quantity_index_remaining = contract.quantity_index + total_qty
            else:
                contract.quantity_index_remaining = 0.0

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        """Genera secuencia para name si no se proporciona."""
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'deposit.contract'
                ) or _('Nuevo')
        return super().create(vals_list)
