from odoo import fields, models, api
from datetime import date
from odoo.exceptions import UserError


class CdContract(models.Model):

    _name = 'cd.contract'
    vehicle_id = fields.Many2one(comodel_name='cd.vehicle', string='Car', required=True)
    client_id = fields.Many2one(comodel_name='cd.client', string='Customer', required=True)
    start_date = fields.Date(string='Start Date', default=date.today())
    end_date = fields.Date(string='End Date', required=True)
    price = fields.Float(string='Price', required=True)
    payment_method = fields.Selection([('full', 'Full Price'),
                                       ('monthly', 'Monthly Payments')],
                                      string='Payment Method',
                                      default='full', required=True)
    interest_rate = fields.Float(string='Interest Rate', compute='_compute_interest_rate')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price')
    state = fields.Selection(string='State', required=True, default='draft',
                             selection=[('confirm', 'Confirm'),
                                        ('draft', 'Draft'),
                                        ('cancel', 'Chancel'),
                                        ])
    amount_paid = fields.Float(string='Amount payed', required=True, default=0.00)
    payed = fields.Boolean(string='Contract fully payed', required=True, default=False)
    is_used = fields.Boolean(default=False, required=True)
    contract_num = fields.Char(string='Contract Number', unique=True, required=False)
    payments = fields.One2many(comodel_name='cd.payment', inverse_name='contract_id', string='Payments')
    monthly_payment = fields.Float(string='Monthly Payment', compute='_compute_monthly_payment', required=True)

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        self.price = self.vehicle_id.price

    @api.model
    def generate_contract_num(self):
        sequence = self.env['ir.sequence'].next_by_code('cd.contract')
        return sequence

    @api.model
    def create(self, vals):
        if not vals.get('contract_num'):
            vals['contract_num'] = self.generate_contract_num()
        return super(CdContract, self).create(vals)

    def unlink(self):
        if self.state != 'draft':
            raise UserError("It can be deleted only in draft state")
        return super().unlink()

    @api.depends('payment_method', 'start_date', 'end_date', 'price')
    def _compute_interest_rate(self):
        for contract in self:
            if contract.payment_method == 'full':
                contract.interest_rate = 0.0
            else:
                start_date = fields.Date.from_string(contract.start_date)
                end_date = fields.Date.from_string(contract.end_date)
                duration = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

                if duration <= 6:
                    contract.interest_rate = 0.02
                elif duration <= 12:
                    contract.interest_rate = 0.03
                else:
                    contract.interest_rate = 0.04

    @api.depends('price', 'payment_method', 'interest_rate', 'end_date', 'start_date')
    def _compute_total_price(self):
        for contract in self:
            if contract.payment_method == 'full':
                contract.total_price = contract.price
            elif contract.payment_method == 'monthly':
                period = (contract.end_date.year - contract.start_date.year) + 1
                monthly_rate = (1 + contract.interest_rate) ** (1 / 12) - 1
                total_payments = period * 12
                annuity_factor = (monthly_rate * (1 + monthly_rate) ** total_payments) / (
                            (1 + monthly_rate) ** total_payments - 1)
                contract.total_price = contract.price * annuity_factor * total_payments

    def _contract_closure(self):
        if self.amount_paid >= self.total_price:
            self.payed = True

    def draft(self):
        self.state = "draft"

    def action_confirm(self):
        if self.state == "confirm":
            self.vehicle_id.unit -= 1

    @api.constrains('vehicle_id')
    def _check_vehicle_sold(self):
        if self.vehicle_id.sold:
            raise UserError("This vehicle has already been sold and cannot be added to a new contract.")

    @api.depends('total_price', 'end_date', 'start_date')
    def _compute_monthly_payment(self):
        for contract in self:
            if contract.payment_method == 'full':
                contract.monthly_payment = contract.total_price
            elif contract.payment_method == 'monthly':
                period = (contract.end_date.year - contract.start_date.year) + 1
                total_payments = period * 12
                contract.monthly_payment = contract.total_price / total_payments



