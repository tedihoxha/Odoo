from odoo import models, api


class SaleReport(models.AbstractModel):
    _name = 'report.cd.report_sale'
    _description = 'Sales Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        sales = self.env['cd.sales'].search([('sale_date', '>=', start_date), ('sale_date', '<=', end_date)])

        if not sales:
            return {'message': 'There are no sales done in this period'}
        else:
            report_data = []
            for sale in sales:
                sale_data = {
                    'date': sale.sale_date,
                    'salesperson_name': sale.salesperson_id.name,
                    'customer_name': sale.client_id.name,
                    'vehicle_name': sale.vehicle_id.name,
                    'sale_price': sale.price,
                    'purchase_price': sale.purchase_price,
                    'profit': sale.profit,
                }
                report_data.append(sale_data)

            return {
                'doc_ids': docids,
                'doc_model': 'cd.sales',
                'docs': sales,
                'report_data': report_data,
                'start_date': start_date,
                'end_date': end_date,
            }