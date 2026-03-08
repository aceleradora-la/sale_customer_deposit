# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class DepositLedger(models.Model):
    """
    Libro Mayor de Acopios (inmutable).

    Registra cada movimiento del contrato de acopio de forma permanente.
    Los valores en dinero son negativos para retiros (descuentos de saldo)
    y positivos para fondos iniciales o ajustes.
    """
    _name = 'deposit.ledger'
    _description = 'Libro Mayor de Acopios'
    _order = 'date asc, id asc'
    _rec_name = 'display_name'

    # -------------------------------------------------------------------------
    # Tipos de movimiento
    # -------------------------------------------------------------------------
    MOVE_TYPE_SELECTION = [
        ('funding', 'Fondeo Inicial'),
        ('withdrawal', 'Retiro'),
        ('adjustment', 'Ajuste'),
        ('closure', 'Cierre'),
    ]

    # -------------------------------------------------------------------------
    # Campos
    # -------------------------------------------------------------------------
    contract_id = fields.Many2one(
        comodel_name='deposit.contract',
        string='Contrato',
        required=True,
        ondelete='cascade',
        index=True,
    )
    date = fields.Datetime(
        string='Fecha',
        default=fields.Datetime.now,
        required=True,
    )
    move_type = fields.Selection(
        selection=MOVE_TYPE_SELECTION,
        string='Tipo de Movimiento',
        required=True,
    )
    # Monto en moneda de la compañía (negativo = retiro, positivo = fondeo/ajuste)
    amount = fields.Monetary(
        string='Monto',
        currency_field='currency_id',
        default=0.0,
    )
    # Cantidad para tipo Index Product (negativo = consumo)
    quantity = fields.Float(
        string='Cantidad',
        digits='Product Unit of Measure',
        default=0.0,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='contract_id.currency_id',
        store=True,
    )
    # Referencia al documento origen (SO, factura, etc.)
    ref = fields.Char(
        string='Referencia',
        help='Referencia al documento que originó el movimiento',
    )
    ref_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Factura Relacionada',
        ondelete='set null',
    )
    ref_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Pedido Relacionado',
        ondelete='set null',
    )
    note = fields.Text(
        string='Notas',
    )
    display_name = fields.Char(
        string='Nombre',
        compute='_compute_display_name',
        store=True,
    )

    # -------------------------------------------------------------------------
    # Computed
    # -------------------------------------------------------------------------
    @api.depends('contract_id', 'date', 'move_type', 'amount', 'ref')
    def _compute_display_name(self):
        for ledger in self:
            parts = [
                ledger.contract_id.name or '?',
                ledger.move_type or '',
                f"{ledger.amount:.2f}" if ledger.amount else "",
            ]
            ledger.display_name = ' | '.join(filter(None, parts))

    # -------------------------------------------------------------------------
    # Restricciones (inmutabilidad)
    # -------------------------------------------------------------------------
    def write(self, vals):
        """El ledger es inmutable: no se permiten modificaciones."""
        # Permitir solo creación, no escritura
        if self:
            raise models.UserError(
                _('El Libro Mayor de Acopios es inmutable. No se pueden modificar registros existentes.')
            )
        return super().write(vals)

    def unlink(self):
        """El ledger no debe eliminarse (auditoría)."""
        raise models.UserError(
            _('No se pueden eliminar registros del Libro Mayor de Acopios.')
        )
