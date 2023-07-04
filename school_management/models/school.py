from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class SchoolManagement(models.Model):
    _name = 'school.management.student'
    _description = 'Student'
    _inherit = 'mail.thread'
    _rec_name = 'er_num'

    # Grade levels for the student
    GRADE_LEVELS = [
        ('jr_kg', 'Jr. KG'),
        ('sr_kg', 'Sr. KG'),
        ('1', '1st'),
        ('2', '2nd'),
        ('3', '3rd'),
        ('4', '4th'),
        ('5', '5th'),
        ('6', '6th'),
        ('7', '7th'),
        ('8', '8th'),
        ('9', '9th'),
        ('10', '10th'),
        ('11', '11th'),
        ('12', '12th'),
    ]

    # Division options for the student
    DIVISION_OPTIONS = [
        ('a', 'A'),
        ('b', 'B')
    ]

    # Stream options for the student
    STREAM_OPTIONS = [
        ('science', 'Science'),
        ('commerce', 'Commerce'),
        ('arts', 'Arts')
    ]

    # Fields for the student model
    name_in_previous_school = fields.Char(string='Name of Previous School')
    er_num = fields.Char(string='Enrollment Number')
    admission_date_of_last_school = fields.Date(string='Admission Date')
    leaving_date_of_last_school = fields.Date(string='Leaving Date')
    gender = fields.Selection([
        ('Male', 'male'),
        ('Female', 'female'),
        ('Other', 'other'),
    ], string='Gender')

    name = fields.Char(string='Name', required=True, tracking=True)
    standard = fields.Selection(selection=GRADE_LEVELS, string='Standard', tracking=True)
    class_teacher = fields.Many2one('school.management.teacher', compute='_depends_division', string='Class Teacher', store=True)
    division = fields.Selection(selection=DIVISION_OPTIONS, string='Division', tracking=True)
    roll_number = fields.Integer(string='Roll Number', tracking=True)
    enr_number = fields.Char(string='Unique Enrollment Number', compute='_compute_enr_number', store=True)

    country_id = fields.Many2one('res.country', default=lambda self: self.env.ref('base.in'), string='Country', readonly=True)
    state_id = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', country_id)]")
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    zip_code = fields.Char(string='ZIP Code')
    address = fields.Text(string='Address', compute='_compute_address', store=True)

    phone_number = fields.Char(string='Phone Number', required=True, tracking=True)
    dob = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    parent_name = fields.Char(string='Parent/Guardian Name')
    relation = fields.Selection(selection=[
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Relative', 'Relative'),
        ('Guardian', 'Guardian'),
        ('Sibling', 'Sibling')
    ], string='Relation with Student')
    parent_phone_number = fields.Char(string='Phone Number of Parent/Guardian')
    email = fields.Char(string='Email')
    stream = fields.Selection(selection=STREAM_OPTIONS, string='Stream')

    # Check the length of the roll number
    @api.constrains('roll_number')
    def _check_roll_number_length(self):
        for record in self:
            if record.roll_number and len(str(record.roll_number)) > 4:
                raise ValidationError("Roll number should not be more than 4 digits!")

    # Validate the phone number format and uniqueness
    @api.constrains('phone_number')
    def _check_phone_number(self):
        for record in self:
            phone_number = record.phone_number or ''

            if not phone_number.isdigit() or len(phone_number) > 10:
                raise ValidationError("Phone number should contain only numeric values and have a maximum length of 10 digits!")

            duplicate_records = self.search([('phone_number', '=', record.phone_number), ('id', '!=', record.id)])
            if duplicate_records:
                raise ValidationError("Phone number is already assigned to another student")

    # Validate the parent/guardian phone number format
    @api.constrains('parent_phone_number')
    def _check_parent_phone_number(self):
        for record in self:
            parent_phone_number = record.parent_phone_number or ''

            if not parent_phone_number.isdigit() or len(parent_phone_number) > 10:
                raise ValidationError("Phone number of parent/guardian should contain only numeric values and have a maximum length of 10 digits!")

    # Check the age of the student
    @api.constrains('age')
    def _check_age(self):
        for record in self:
            if record.age < 4:
                raise ValidationError("Age cannot be less than 4 years!")

    # Compute the age based on the date of birth
    @api.depends('dob')
    def _compute_age(self):
        for record in self:
            if record.dob:
                today = fields.Date.today()
                dob = fields.Date.from_string(record.dob)
                record.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                record.age = 0

    # Compute the enrollment number based on the name
    @api.depends('name')
    def _compute_enr_number(self):
        for record in self:
            if record.name:
                record.enr_number = 'ENR' + str(record.id).zfill(4)
            else:
                record.enr_number = ''

    # Check the format of the ZIP code
    @api.constrains('zip_code')
    def _check_zip_code_format(self):
        for record in self:
            zip_code = record.zip_code or ''
            if zip_code and (not zip_code.isdigit() or len(zip_code) != 6):
                raise ValidationError('Invalid ZIP code format!')

    # Compute the full address based on the individual address fields
    @api.depends('street', 'city', 'state_id', 'country_id', 'zip_code')
    def _compute_address(self):
        for record in self:
            address_parts = []
            if record.street:
                address_parts.append(record.street)
            if record.city:
                address_parts.append(record.city)
            if record.state_id:
                address_parts.append(record.state_id.name)
            if record.zip_code:
                address_parts.append(record.zip_code)
            record.address = ", ".join(address_parts)

    # Update the stream field based on the selected standard
    @api.onchange('standard')
    def _onchange_standard(self):
        if self.standard in ['11', '12']:
            self.stream = 'science'
        else:
            self.stream = False

    # Birth month field
    birth_month = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string='Birth Month', store=True)

    # Compute the class teacher based on division, stream, and standard
    @api.depends('division', 'stream', 'standard')
    def _depends_division(self):
        teacher = self.env['school.management.teacher'].search([
            ('standard', '=', self.standard), ('division', '=', self.division), ('stream', '=', self.stream)
        ], limit=1)
        if teacher:
            self.class_teacher = teacher.id
        else:
            self.class_teacher = False


class SchoolManagementTeacher(models.Model):
    _name = 'school.management.teacher'
    _description = 'Teacher'

    name = fields.Char(string='Teacher Name')
    student_id = fields.One2many('school.management.student', 'class_teacher', string="students")
    standard = fields.Selection(string='Standard assigned to teacher',
                                selection=[('jr_kg', 'Jr. KG'),
                                           ('sr_kg', 'Sr. KG'),
                                           ('1', '1st'),
                                           ('2', '2nd'),
                                           ('3', '3rd'),
                                           ('4', '4th'),
                                           ('5', '5th'),
                                           ('6', '6th'),
                                           ('7', '7th'),
                                           ('8', '8th'),
                                           ('9', '9th'),
                                           ('10', '10th'),
                                           ('11', '11th'),
                                           ('12', '12th')])
    DIVISION_OPTIONS = [
        ('a', 'A'),
        ('b', 'B')
    ]

    STREAM_OPTIONS = [
        ('science', 'Science'),
        ('commerce', 'Commerce'),
        ('arts', 'Arts')
    ]
    division = fields.Selection(selection=DIVISION_OPTIONS, string='Division')
    stream = fields.Selection(selection=STREAM_OPTIONS, string='Stream')
