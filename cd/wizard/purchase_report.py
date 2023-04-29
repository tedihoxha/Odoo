from odoo import fields, models
from odoo.exceptions import UserError


class PurchaseReportWizard(models.TransientModel):
    _name = 'purchase.report'

    _description = 'Purchase Report'
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    def print_report(self):
        self.ensure_one()
        if self.start_date > self.end_date:
            raise UserError('Start date must be before end date.')
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env.ref('cd.action_report_purchase').report_action(self, data=data)
