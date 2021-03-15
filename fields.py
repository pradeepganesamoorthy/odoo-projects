from odoo import api, fields, models
from datetime import datetime
import dateutil.parser
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class Fieldcreate(models.Model):
    _name = "create.field"


    sq_name = fields.Char(string="Service Number", readonly=True, required=True, copy=False, default='New')
    name = fields.Char(string='Name', required=True, default="test")
    age = fields.Integer(string='Age', compute="set_age", store=True)
    date = fields.Date(string="Date", default=datetime.today())
    address = fields.Text(string='Address')
    average_mark = fields.Float(string='Average mark', readonly="1")
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female')], string='Gender')
    description = fields.Html(string='Description')
    form_create_date = fields.Datetime(string='Date of Create')
    file_for_import = fields.Binary(string='File for upload')
    active = fields.Boolean(string="Active", default=True)
    vehicle = fields.Many2one('vehicle.names', string='Vehicle')
    departments = fields.Many2many("departments.name",string="Departments")
    image_small = fields.Binary(string="Image",attachment=True)
    vehicle_list = fields.One2many("create.field.line", "multi_name", string="Lists")
    subtotal_amount = fields.Integer(string="Total amount",compute="compute_line_price")
    total_amount = fields.Float(string="Total",compute="compute_line_price")
    currency_id = fields.Many2one("res.currency")
    state = fields.Selection([('draft','Draft'),('processing','Processing'),('completed','Completed'),('cancel','Cancelled')],string='Status', readonly=True, default="draft")

    def action_processing(self):
        self.state= 'processing'

    def action_complete(self):
        self.state= 'completed'

    def action_cancel(self):
        if self.state == 'completed':
            raise UserError(('The %s record could not be deleted.Because the process was completed.'%(self.name)))
        else:
            self.state= 'cancel'

    def action_reset(self):
        self.state= 'draft'

    @api.multi
    def name_get(self):
        res=[]
        for rec in self:
            res.append((rec.id,'%s-%s'%(rec.sq_name,rec.name)))
        return res

    @api.model
    def create(self, values):
        if values.get('sq_name', 'New') == 'New':
            values['sq_name'] = self.env['ir.sequence'].next_by_code(
                'create.field') or 'New'
        result = super(Fieldcreate, self).create(values)
        return result


    @api.multi
    def write(self, values):
        return super(Fieldcreate, self).write(values)

    @api.multi
    def copy(self,values):
        return super(Fieldcreate,self).copy(values)

    @api.multi
    def unlink(self):
        return super(Fieldcreate, self).unlink()

    @api.depends("date")
    def set_age(self):
        for r in self:
            date_l = datetime.strptime(r.date, '%Y-%M-%d')
            today = datetime.today()
            age = today.year - date_l.year
            r.age = age

    @api.onchange("gender")
    def onchange_vehicle(self):
        self.vehicle = self.env['vehicle.names'].search([('gender', '=', self.gender)])

    @api.depends("vehicle_list.price")
    def compute_line_price(self):
        sub_total=0
        for i in self.vehicle_list:
            sub_total += i.price
        grand_total = sub_total + sub_total*(self.vehicle_list.gst_amount/100)
        self.subtotal_amount = sub_total
        self.total_amount = grand_total

class DepartMents(models.Model):
    _name = "departments.name"
    _rec_name = "dep_name"
    dep_name = fields.Char(string="Department Name")


class NameofVehicle(models.Model):
    _name = "vehicle.names"

    name = fields.Char(string='Name')
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female')], string='Gender')

    @api.multi
    def name_get(self):
        res=[]
        for rec in self:
            res.append((rec.id,'%s-%s'%(rec.name,rec.gender)))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args=[]
        domain = args + ['|',('name',operator,name),('gender',operator,name)]
        return super(NameofVehicle,self).search(domain,limit=limit).name_get()


class FieldLines(models.Model):
    _name="create.field.line"

    multi_name = fields.Many2one("create.field",string="Name")
    mobile_num = fields.Integer(string="Mobile Number")
    email_id_line = fields.Char(string="Email ID")
    price = fields.Integer(string="Price")
    gst_amount = fields.Float(string="GST%")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    mobile_id = fields.Many2one("mobile.business.store", string="Mobile Name")

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    mobile_id = fields.Many2one("mobile.business.store", string="Mobile Name")

