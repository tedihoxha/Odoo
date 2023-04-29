from odoo import models, fields, api


class Purchase(models.Model):
    _name = 'cd.purchase'
    _description = 'Vehicle purchases made by the dealership'

    code = fields.Char(string='Purchase Order', required=True)
    date = fields.Date(string='Purchase Date', required=True)
    vehicle_id = fields.Many2one(comodel_name='cd.vehicle', string='Vehicle', required=True)
    quantity = fields.Integer(string='Quantity', required=True, default=1)
    unit_price = fields.Float(string='Unit Price', required=True)
    total_price = fields.Float(string='Total Price', required=True, compute='_compute_total_price')
    factory_id = fields.Many2one(comodel_name='cd.factory', string='Vehicle Factory', store=True)

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        self.unit_price = self.vehicle_id.purchase_price

    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.quantity * record.unit_price

    @api.model
    def create(self, vals):
        purchase = super(Purchase, self).create(vals)
        if purchase.vehicle_id:
            purchase.vehicle_id.write({'unit': purchase.vehicle_id.unit + purchase.quantity})
        return purchase