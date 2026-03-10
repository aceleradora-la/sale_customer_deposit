# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class DepositContractLine(models.Model):
    """
    Línea de contrato para tipo Cantidades Fijas.

    Define los productos y cantidades compradas en el acopio
    que el cliente puede retirar gradualmente.
    """
    _name = 'deposit.contract.line'
    _description = 'Línea de Contrato de Acopio (Cantidades Fijas)'

    contract_id = fields.Many2one(
        comodel_name='deposit.contract',
        string='Contrato',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Producto',
        required=True,
        ondelete='restrict',
        domain=[('type', 'in', ('product', 'consu'))],
    )
    quantity = fields.Float(
        string='Cantidad Inicial',
        digits='Product Unit of Measure',
        required=True,
        default=1.0,
    )
    quantity_remaining = fields.Float(
        string='Cantidad Restante',
        digits='Product Unit of Measure',
        compute='_compute_quantity_remaining',
        store=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        related='product_id.uom_id',
        store=True,
    )

    @api.depends('quantity', 'contract_id.ledger_line_ids.quantity', 'contract_id.ledger_line_ids.product_id')
    def _compute_quantity_remaining(self):
        """Cantidad restante = inicial + suma de movimientos ledger para este producto."""
        for line in self:
            if line.contract_id.deposit_type != 'fixed_quantities':
                line.quantity_remaining = 0.0
                continue
            consumed = sum(
                ledger.quantity
                for ledger in line.contract_id.ledger_line_ids
                if ledger.product_id == line.product_id and ledger.quantity < 0
            )
            line.quantity_remaining = line.quantity + consumed  # consumed is negative
