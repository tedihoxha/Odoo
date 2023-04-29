from odoo import fields, models, api
from odoo.exceptions import ValidationError


class CarDealershipStaff(models.Model):
    _name = 'cd.staff'
    _description = 'Car Dealership Staff'

    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age')
    job_title = fields.Char(string='Job Title', required=True)
    salary = fields.Float(string='Monthly Salary')
    previous_exp = fields.Text(string='Previous Experiences')
    hire_date = fields.Date(string='Hire Date')
    department = fields.Selection([
        ('sales', 'Sales'),
        ('finance', 'Finance'),
        ('service', 'Service')
    ], string='Department', required=True)
    contract_end_date = fields.Date(string='Contract End Date')
    manager = fields.Boolean(string='Is a manager?')

    salesperson_id = fields.Many2one(comodel_name='cd.salesperson', string='Salesperson', ondelete='restrict',
                                     copy=False)

    def year_payment(self):
        year_salary = 12 * self.salary
        return year_salary

    @api.model
    def create(self, vals):
        staff = super(CarDealershipStaff, self).create(vals)
        if vals.get('department') == 'sales' and not vals.get('manager'):
            salesperson_vals = {
                'name': vals.get('name'),
                'email': '',
                'phone': '',
                'commission_rate': 15.0,
            }
            salesperson = self.env['cd.salesperson'].create(salesperson_vals)
            staff.salesperson_id = salesperson.id
        return staff

    def unlink(self):
        res = super(CarDealershipStaff, self).unlink()
        return res

    @api.constrains('contract_end_date')
    def check_contract_end_date(self):
        for staff in self:
            if staff.contract_end_date and staff.contract_end_date < fields.Date.today():
                raise ValidationError('Contract has ended. Staff member will be unlinked.')
