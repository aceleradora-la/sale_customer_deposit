# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    deposit_contract_id = fields.Many2one(
        comodel_name='deposit.contract',
        string='Contrato de Acopio',
        ondelete='set null',
        domain="[('partner_id', '=', partner_id), ('state', 'in', ('confirmed', 'in_progress'))]",
        help='Contrato de acopio activo del cliente para aplicar descuento',
    )

    def _get_consumo_acopio_product(self):
        """Obtiene el producto Consumo de Acopio (config o por defecto)."""
        ICP = self.env['ir.config_parameter'].sudo()
        product_id = ICP.get_param('sale_customer_deposit.deposit_service_product_id', default='0')
        if product_id and product_id != '0':
            product = self.env['product.product'].browse(int(product_id)).exists()
            if product:
                return product
        return self.env.ref(
            'sale_customer_deposit.product_template_consumo_acopio',
            raise_if_not_found=False
        ).product_variant_id

    def _compute_deposit_discount_amount(self, contract):
        """
        Calcula el monto a descontar según el tipo de contrato.
        Retorna (amount_to_discount, ledger_vals_list).
        ledger_vals_list: lista de dicts para crear deposit.ledger (para type 3).
        """
        self.ensure_one()
        ProductProduct = self.env['product.product']
        Ledger = self.env['deposit.ledger']

        if contract.deposit_type == 'fixed_pricelist':
            # Tipo 1: Descontar hasta el saldo en dinero
            order_total = self.amount_total
            balance = contract.amount_remaining
            amount = -min(order_total, balance)
            return amount, [{
                'contract_id': contract.id,
                'move_type': 'withdrawal',
                'amount': amount,
                'quantity': 0.0,
                'ref': self.name,
                'ref_order_id': self.id,
            }]

        if contract.deposit_type == 'index_product':
            # Tipo 2: Total / precio índice = cantidades a consumir
            order_total = self.amount_total
            if not contract.product_id:
                raise models.UserError(_('El contrato de tipo Índice no tiene producto índice definido.'))
            # Precio actual del producto índice (pricelist del pedido o list_price)
            product = contract.product_id.with_company(self.company_id)
            pricelist = self.pricelist_id or self.partner_id.property_product_pricelist
            if pricelist:
                try:
                    price = pricelist._get_product_price(product, 1.0, self.partner_id)
                except (TypeError, AttributeError):
                    price = product.list_price
            else:
                price = product.list_price
            if not price or price <= 0:
                raise models.UserError(
                    _('No se pudo obtener el precio del producto índice "%s".', contract.product_id.display_name)
                )
            qty_to_consume = order_total / price
            if qty_to_consume > contract.quantity_index_remaining:
                raise models.UserError(
                    _('Saldo índice insuficiente. Necesita %.2f, tiene %.2f.',
                      qty_to_consume, contract.quantity_index_remaining)
                )
            amount = -order_total
            return amount, [{
                'contract_id': contract.id,
                'move_type': 'withdrawal',
                'amount': amount,
                'quantity': -qty_to_consume,
                'ref': self.name,
                'ref_order_id': self.id,
            }]

        if contract.deposit_type == 'fixed_quantities':
            # Tipo 3: Validar cantidades por producto y sumar valor a descontar
            deposit_lines_by_product = {
                line.product_id: line
                for line in contract.deposit_line_ids
            }
            amount_to_discount = 0.0
            ledger_vals_list = []

            for order_line in self.order_line:
                if order_line.display_type or not order_line.product_id:
                    continue
                if order_line.product_id not in deposit_lines_by_product:
                    continue
                dep_line = deposit_lines_by_product[order_line.product_id]
                qty_order = order_line.product_uom_qty
                qty_avail = dep_line.quantity_remaining
                if qty_order > qty_avail:
                    raise models.UserError(
                        _('Producto "%s": cantidad solicitada %.2f excede saldo en acopio %.2f.',
                          order_line.product_id.display_name, qty_order, qty_avail)
                    )
                amount_to_discount += order_line.price_subtotal
                ledger_vals_list.append({
                    'contract_id': contract.id,
                    'move_type': 'withdrawal',
                    'amount': 0.0,
                    'quantity': -qty_order,
                    'product_id': order_line.product_id.id,
                    'ref': self.name,
                    'ref_order_id': self.id,
                })

            if amount_to_discount <= 0:
                raise models.UserError(_('No hay líneas del pedido que coincidan con el acopio de cantidades fijas.'))
            return -amount_to_discount, ledger_vals_list

        raise models.UserError(_('Tipo de acopio no soportado.'))

    def action_apply_deposit(self):
        """Aplica el descuento de acopio inyectando una línea negativa."""
        self.ensure_one()
        contract = self.deposit_contract_id
        if not contract:
            raise models.UserError(_('Seleccione un contrato de acopio.'))
        if self.state != 'draft':
            raise models.UserError(_('Solo se puede aplicar acopio en pedidos en borrador.'))

        # Validar saldo según tipo
        if contract.deposit_type in ('fixed_pricelist', 'index_product'):
            if contract.amount_remaining <= 0 and contract.deposit_type == 'fixed_pricelist':
                raise models.UserError(_('El contrato no tiene saldo disponible.'))
            if contract.deposit_type == 'index_product' and contract.quantity_index_remaining <= 0:
                raise models.UserError(_('El contrato no tiene cantidad índice disponible.'))

        if not self.order_line:
            raise models.UserError(_('El pedido no tiene líneas. Agregue productos antes de aplicar el acopio.'))

        # Eliminar línea de Consumo de Acopio previa si existe
        product_consumo = self._get_consumo_acopio_product()
        if not product_consumo:
            raise models.UserError(_('No se encontró el producto "Consumo de Acopio". Actualice el módulo.'))
        existing = self.order_line.filtered(lambda l: l.product_id == product_consumo)
        if existing:
            existing.unlink()

        amount, _ledger_vals = self._compute_deposit_discount_amount(contract)
        if amount >= 0:
            return True  # Nada que descontar

        # Crear línea negativa
        self.env['sale.order.line'].create({
            'order_id': self.id,
            'product_id': product_consumo.id,
            'name': product_consumo.display_name,
            'product_uom_qty': 1.0,
            'price_unit': amount,  # Ya es negativo
            'product_uom': product_consumo.uom_id.id,
            'tax_id': [(5, 0, 0)],  # Sin impuestos para no afectar tax_totals de forma incorrecta
        })
        return True

    def action_confirm(self):
        """Al confirmar, registrar en el ledger si hay consumo de acopio."""
        orders_with_deposit = self.filtered(
            lambda o: o.deposit_contract_id and o.state == 'draft'
        )
        Ledger = self.env['deposit.ledger']
        for order in orders_with_deposit:
            product_consumo = order._get_consumo_acopio_product()
            if not product_consumo:
                continue
            consumo_line = order.order_line.filtered(
                lambda l: l.product_id == product_consumo
            )
            if not consumo_line:
                continue
            contract = order.deposit_contract_id
            # Usar el monto de la línea de consumo (no recomputar, evita inconsistencia)
            amount_consumed = consumo_line.price_subtotal  # Ya es negativo
            if amount_consumed >= 0:
                continue
            if contract.deposit_type == 'fixed_pricelist':
                Ledger.create({
                    'contract_id': contract.id,
                    'move_type': 'withdrawal',
                    'amount': amount_consumed,
                    'quantity': 0.0,
                    'ref': order.name,
                    'ref_order_id': order.id,
                    'date': fields.Datetime.now(),
                })
            elif contract.deposit_type == 'index_product':
                product = contract.product_id.with_company(order.company_id)
                pricelist = order.pricelist_id or order.partner_id.property_product_pricelist
                if pricelist:
                    try:
                        price = pricelist._get_product_price(product, 1.0, order.partner_id)
                    except (TypeError, AttributeError):
                        price = product.list_price
                else:
                    price = product.list_price
                qty_consumed = abs(amount_consumed) / price if price else 0
                Ledger.create({
                    'contract_id': contract.id,
                    'move_type': 'withdrawal',
                    'amount': amount_consumed,
                    'quantity': -qty_consumed,
                    'ref': order.name,
                    'ref_order_id': order.id,
                    'date': fields.Datetime.now(),
                })
            elif contract.deposit_type == 'fixed_quantities':
                # Una entrada por producto consumido
                deposit_lines_by_product = {l.product_id: l for l in contract.deposit_line_ids}
                for order_line in order.order_line:
                    if order_line.display_type or not order_line.product_id:
                        continue
                    if order_line.product_id not in deposit_lines_by_product:
                        continue
                    Ledger.create({
                        'contract_id': contract.id,
                        'move_type': 'withdrawal',
                        'amount': 0.0,
                        'quantity': -order_line.product_uom_qty,
                        'product_id': order_line.product_id.id,
                        'ref': order.name,
                        'ref_order_id': order.id,
                        'date': fields.Datetime.now(),
                    })
        return super().action_confirm()
