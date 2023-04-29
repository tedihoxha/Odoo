from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Vehicle(models.Model):
    _name = 'cd.vehicle'

    _description = 'Vehicle in the dealership'
    name = fields.Char(string='Name', required=True)
    _rec_name = 'name'
    image = fields.Image(string="Vehicle photo", reuqired=True)
    make = fields.Char(string='Make', required=True)
    model = fields.Char(string='Model', required=True)
    year = fields.Date(string='Year', required=True)
    price = fields.Float(string='Price in Euros', required=True)
    factory_id = fields.Many2one(comodel_name='cd.factory', string='Vehicle Factory', required=True)
    purchase_price = fields.Float(string='Buying Cost', required=True)
    sold = fields.Boolean(string='Sold', required=True, default=False)
    inventory_id = fields.Many2one(comodel_name='cd.inventory', string='Inventory', required=True)
    dealer_plates = fields.Char(string='Car plates', required=True)
    rate = fields.Selection(
        string='priority',
        selection=[('0', 'low'),
                   ('1', 'average'),
                   ('2', 'good'),
                   ('3', 'great'),
                   ('4', 'fantastic'), ], required=True, )
    unit = fields.Integer(string='Units', required=True, default=1)

    @api.depends('unit')
    def check_unit(self):
        if self.unit == 0:
            self.sold = True


class CdFactory(models.Model):
    _name = 'cd.factory'
    _description = 'Car Factory'

    name = fields.Char(string='Name', required=True)
    location = fields.Char(string='Location')
    vehicle_ids = fields.One2many(comodel_name='cd.vehicle', inverse_name='factory_id', string='Vehicles')
    inventory_ids = fields.One2many(comodel_name='cd.inventory', inverse_name='factory_id',
                                    string='Car destination', required=False)


class CdInventory(models.Model):
    _name = "cd.inventory"
    _description = "Car Dealership Inventory"

    name = fields.Char(string="Inventory Name")
    description = fields.Text(string="Description")
    location = fields.Char(string='Location', required=True)
    vehicle_ids = fields.One2many(comodel_name='cd.vehicle', inverse_name='inventory_id', string="vehicles",
                                  required=False)
    factory_id = fields.Many2one(comodel_name='cd.factory', string='Factories the car are coming from',
                                 required=False)
    capacity = fields.Integer(string='Inventory capacity', required=True)

    @api.model
    def remove_sold_vehicles(self):
        sold_vehicles = self.vehicle_ids.filtered([('sold', '=', True)])
        sold_vehicles.unlink()

    @api.depends('vehicle_ids.price')
    def _compute_total_value(self):
        for inventory in self:
            inventory.total_value = sum(vehicle.price for vehicle in inventory.vehicle_ids)
    total_value = fields.Float(string='Total Value', compute='_compute_total_value', store=True)

    @api.depends('vehicle_ids.price')
    def _compute_average_value(self):
        if self.total_quantity != 0:
            self.average_value = self.total_value / self.total_quantity
    average_value = fields.Float(string='Average Value', compute='_compute_average_value', store=True)

    @api.depends('vehicle_ids.unit')
    def _compute_total_quantity(self):
        for inventory in self:
            inventory.total_quantity = sum(vehicle.unit for vehicle in inventory.vehicle_ids)
    total_quantity = fields.Integer(string='Total Quantity', compute='_compute_total_quantity', store=True)

    @api.constrains('vehicle_ids')
    def _check_capacity(self):
        if self.total_quantity > self.capacity:
            raise ValidationError('Inventory capacity exceeded')


