from odoo import models, api


class PurchaseReport(models.AbstractModel):

    _name = 'report.cd.report_purchase'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['start_date']
        end_date = data['end_date']
        purchases = self.env['cd.purchase'].search([('date', '>=', start_date), ('date', '<=', end_date)])

        if not purchases:
            return {'message': 'There are no purchases done in this period'}
        else:
            vehicle_data = []
            for purchase in purchases:
                vehicle = {
                    'vehicle_name': purchase.vehicle_id.name,
                    'unit_number': purchase.quantity,
                    'price': purchase.unit_price,
                    'total_price': purchase.total_price,
                }
                vehicle_data.append(vehicle)

            return {
                'doc_ids': docids,
                'doc_model': 'cd.purchase',
                'docs': purchases,
                'start_date': start_date,
                'end_date': end_date,
                'vehicle_data': vehicle_data,
            }