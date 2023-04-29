from odoo import models, fields


class SaleReportWizard(models.TransientModel):
    _name = 'sale.report'
    _description = 'Sales Report'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def print_report(self):
        self.ensure_one()
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env.ref('cd.action_report_sale').report_action(self, data=data)

