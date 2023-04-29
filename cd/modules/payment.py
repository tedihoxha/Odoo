from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class Payment(models.Model):
    _name = 'cd.payment'

    contract_id = fields.Many2one(comodel_name='cd.contract', string='contract', required=True)
    amount = fields.Float(string='Amount paid', required=True)
    payment_date = fields.Date(string='Payment Date', required=True)
    client_id = fields.Many2one(comodel_name='cd.client', string='Client', store=True)
    left = fields.Float(string='Left to be paid', compute='_compute_left', readonly=True, store=True)

    approve = fields.Boolean(string='Are you sure you want to confirm this payment', default=False, required=True)

    @api.depends('contract_id.total_price', 'amount', 'contract_id.amount_paid')
    def _compute_left(self):
        for payment in self:
            if payment.amount < 0:
                raise ValidationError('Amount paid must be greater than 0')
            else:
                payment.left = payment.contract_id.total_price - payment.contract_id.amount_paid - payment.amount
                if payment.left < 0:
                    raise ValidationError('Amount paid exceeds the total price of the contract')

    def write(self, vals):
        res = super(Payment, self).write(vals)
        for payment in self.filtered(lambda p: 'amount' in vals and p.approve):
            contract = payment.contract_id
            contract.amount_paid += vals['amount'] - payment.amount
            contract.total_price -= vals['amount'] - payment.amount
            contract.write({'amount_paid': contract.amount_paid, 'total_price': contract.total_price})
        return res

    def unlink(self):
        if self.approve:
            raise UserError("Approved payments can not be deleted")
        else:
            for payment in self:
                payment.contract_id.amount_paid -= payment.amount
            super().unlink()

    @api.onchange('contract_id')
    def values(self):
        self.client_id = self.contract_id.client_id




