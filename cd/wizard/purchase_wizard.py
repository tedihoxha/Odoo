from odoo import fields, models


class PurchaseWizard(models.TransientModel):
    _name = 'purchase_wizard'
    _description = 'Purchase Wizard'

    vehicle_id = fields.Many2one(comodel_name='cd.vehicle', string='Vehicle', required=True)
    quantity = fields.Integer(string='Quantity', required=True, default=1)

    def create_purchase_order(self):
        purchase = self.env['cd.purchase'].create({
            'code': self.env['ir.sequence'].next_by_code('cd.purchase') or '/',
            'date': fields.Date.today(),
            'vehicle_id': self.vehicle_id.id,
            'quantity': self.quantity,
            'unit_price': self.vehicle_id.purchase_price,
        })
        if purchase.vehicle_id:
            purchase.vehicle_id.write({'unit': purchase.vehicle_id.unit + purchase.quantity})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cd.purchase',
            'view_mode': 'form',
            'res_id': purchase.id,
        }

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}