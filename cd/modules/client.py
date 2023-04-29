from odoo import fields, models, api


class CdClient(models.Model):
    _name = 'cd.client'
    _description = 'Car Dealership Client'

    name = fields.Char(string='Name', required=True)
    image = fields.Image(string="Client photo", reuqired=False)
    phone = fields.Char(string='Phone', required=True)
    email = fields.Char(string='Email', required=True)
    address = fields.Char(string='Address', required=True)
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    zip_code = fields.Char(string='Zip Code')
    date_of_birth = fields.Date(string='Date of Birth')
    driver_license_num = fields.Char(string='Driver License Number', required=True)
    contract_ids = fields.One2many(comodel_name='cd.contract', inverse_name='client_id', string='Contracts',
                                   required=False)
    payment_ids = fields.One2many(comodel_name='cd.payment', inverse_name='client_id', string='Payments',
                                  required=False)
    total_payments = fields.Integer(string='Total Payments', compute='_compute_total_payments', store=True)
    is_late = fields.Boolean(string='Is Late?', compute='_compute_is_late', store=True)

    @api.depends('payment_ids')
    def _compute_total_payments(self):
        for rec in self:
            rec.total_payments = len(rec.payment_ids)

    @api.model
    def _compute_is_late(self):
        today = fields.Date.today()
        clients = self.env['cd.client'].search([])
        for client in clients:
            contracts = client.contract_ids.filtered(lambda c: not c.payed)
            for contract in contracts:
                payments_this_month = self.env['cd.payment'].search([
                    ('contract_id', '=', contract.id),
                    ('payment_date', '>=', fields.Date.today().replace(day=1)),
                    ('payment_date', '<=', today),
                    ('approve', '=', True)
                ])
                total_payments_this_month = sum(payment.amount for payment in payments_this_month)
                if total_payments_this_month < contract.monthly_payment:
                    client.is_late = True
                else:
                    client.is_late = False