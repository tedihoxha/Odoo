from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class Sales(models.Model):
    _name = 'cd.sales'

    _description = 'Sales'
    salesperson_id = fields.Many2one(comodel_name='cd.salesperson', string='Salesperson', required=True)
    client_id = fields.Many2one(comodel_name='cd.client', string='Client', required=True)
    purchase_price = fields.Float(string='Purchase price', readonly=True, required=True, default=0.0)
    price = fields.Float(string='Price', readonly=True, required=True, default=0.0)
    commission = fields.Float(string='Commission', default=0.00)
    sale_date = fields.Date(string='Sale Date', default=fields.Date.today())
    contract_id = fields.Many2one(comodel_name='cd.contract', string='Contract', required=True)
    state = fields.Boolean(string='Sale approved', required=True, default=False)
    vehicle_id = fields.Many2one(comodel_name='cd.vehicle', string='Vehicle', required=True)
    profit = fields.Float(string='Sale Profit', compute='_compute_profit', required=True)

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        self.purchase_price = self.vehicle_id.purchase_price
        self.price = self.contract_id.total_price
        self.vehicle_id = self.contract_id.vehicle_id
        self.client_id = self.contract_id.client_id

    @api.model
    def create(self, values):
        contract = self.env['cd.contract'].browse(values['contract_id'])
        if contract.is_used:
            raise UserError("The contract is already used")
        else:
            contract.write({'is_used': True})
        return super(Sales, self).create(values)

    def unlink(self):
        if self.state:
            raise ValidationError('Cannot delete an approved sale!')
        else:
            self.contract_id.write({'is_used': False})
            res = super(Sales, self).unlink()
            return res

    @api.depends('price', 'purchase_price')
    def _compute_profit(self):
        for rec in self:
            rec.profit = rec.price - rec.purchase_price


class Salesperson(models.Model):
    _name = 'cd.salesperson'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    commission_rate = fields.Float(string='Commission Rate', default=15.0)
    sales_ids = fields.One2many(comodel_name='cd.sales', inverse_name='salesperson_id',
                                string='Sales done by the agent', required=True)

    @api.depends('sales_ids.price', 'commission_rate')
    def _compute_commission_amount(self):
        for record in self:
            total_commission = sum(sale.price * record.commission_rate / 100.0 for sale in record.sales_ids)
            record.commission_amount = total_commission

    commission_amount = fields.Float(string='Commission Amount', compute='_compute_commission_amount', store=True)
