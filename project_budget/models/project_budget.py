from odoo import models, fields, api
from odoo.exceptions import ValidationError

class commercial_budget(models.Model):
    _name = 'project_budget.commercial_budget'

    name = fields.Char(string="commercial_budget name", required=True)
    budget_state = fields.Selection([('work', 'Working'), ('fixed', 'Fixed')], required=True, index=True, default='work', copy = False)
    date_actual = fields.Date(string="Actuality date", index=True)
    year = fields.Integer(string="Budget year", required=True, index=True,default=2023)
    currency_id = fields.Many2one('res.currency', string='Account Currency', tracking=True)
    descr = fields.Text( string='Description', default="")
    commercial_budget_spec_ids = fields.One2many(
        comodel_name='project_budget.commercial_budget_spec',
        inverse_name='commercial_budget_id',
        string="commercial_budget specification",
        copy=True, auto_join=True)

    def isuseradmin(self):
        self.ensure_one()
        return self.env.ref('project_budget.project_budget_admin')

    @api.constrains('year')
    def _check_date_end(self):
        for record in self:
            if record.year < 2022 or record.year > 2030:
                raise ValidationError("The year must be between 2022-2030")

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = 'Copy_'+self.name
        return super(commercial_budget, self).copy(default)



class commercial_budget_spec(models.Model):
    def _get_supervisor_list(self):
        domain = []
        supervisor_access = self.env['project_budget.project_supervisor_access'].search([('user_id.id', '=', self.env.user.id)])
        supervisor_list = []
        for each in supervisor_access:
            supervisor_list.append(each.project_supervisor_id.id)
        if supervisor_list:
            domain = [('id', 'in', supervisor_list)]
            return domain
        return domain

    def _get_manager_list(self):
        domain = []
        manager_access = self.env['project_budget.project_manager_access'].search([('user_id.id', '=', self.env.user.id)])
        manager_list = []
        for each in manager_access:
            manager_list.append(each.project_manager_id.id)
        if manager_list:
            domain = [('id', 'in', manager_list)]
            return domain
        return domain

    _name = 'project_budget.commercial_budget_spec'
    project_id = fields.Char(string="Project_ID", required=True, index=True, copy=True, default="new")
    specification_state = fields.Selection([('prepare', 'Prepare'), ('production', 'Production'), ('cancel','Canceled')], required=True, index=True, default='prepare', store=True)
    currency_id = fields.Many2one('res.currency', string='Account Currency', tracking=True, compute='_compute_reference', store=True)
    commercial_budget_id = fields.Many2one('project_budget.commercial_budget', string='commercial_budget-',required=True, ondelete='cascade', index=True, copy=False)
    budget_state = fields.Selection([('work', 'Working'), ('fixed', 'Fixed')], required=True, index=True, default='work', copy = False, compute='_compute_reference', store=True)
    project_office_id = fields.Many2one('project_budget.project_office', string='project_office', required=True,
                                        copy=True)
    project_supervisor_id = fields.Many2one('project_budget.project_supervisor', string='project_supervisor',
                                            required=True, copy=True, domain=_get_supervisor_list)

    project_manager_id = fields.Many2one('project_budget.project_manager', string='project_manager', required=True,
                                         copy=True, domain=_get_manager_list)
    customer_organization_id = fields.Many2one('project_budget.customer_organization', string='customer_organization',
                                               required=True, copy=True)
    customer_status_id = fields.Many2one('project_budget.customer_status', string='customer_status', required=True,
                                         copy=True)
    industry_id = fields.Many2one('project_budget.industry', string='industry', required=True, copy=True)
    essence_project = fields.Text(string='essence_project', default = "")
    end_presale_project_quarter = fields.Char(string='End date of the Presale project(quarter)', compute='_compute_quarter', store=True)
    end_presale_project_month = fields.Date(string='Date of transition to the Production Budget(MONTH)', required=True, default=fields.datetime.now())
    end_sale_project_quarter = fields.Char(string='End date of the Sale project(quarter)', compute='_compute_quarter',store=True)
    end_sale_project_month = fields.Date(string='The period of shipment or provision of services to the Client(MONTH)', required=True,default=fields.datetime.now())
    vat_attribute_id = fields.Many2one('project_budget.vat_attribute', string='vat_attribute', copy=True)
    total_amount_of_revenue = fields.Monetary(string='total_amount_of_revenue', compute='_compute_spec_totals', store=True)
    revenue_from_the_sale_of_works =fields.Monetary(string='revenue_from_the_sale_of_works(services)')
    revenue_from_the_sale_of_goods = fields.Monetary(string='revenue_from the sale of goods')
    cost_price = fields.Monetary(string='cost_price', compute='_compute_spec_totals', store=True)
    cost_of_goods = fields.Monetary(string='cost_of_goods')
    own_works_fot = fields.Monetary(string='own_works_fot')
    third_party_works = fields.Monetary(string='third_party_works(subcontracting)')
    awards_on_results_project = fields.Monetary(string='Awards based on the results of the project')
    transportation_expenses = fields.Monetary(string='transportation_expenses')
    travel_expenses = fields.Monetary(string='travel_expenses')
    representation_expenses = fields.Monetary(string='representation_expenses')
    taxes_fot_premiums = fields.Monetary(string='taxes_FOT and premiums')
    warranty_service_costs = fields.Monetary(string='Warranty service costs')
    rko_other = fields.Monetary(string='rko_other')
    other_expenses = fields.Monetary(string='other_expenses')
    margin_income = fields.Monetary(string='Margin income', compute='_compute_spec_totals', store=True)
    profitability = fields.Float(string='Profitability(share of Sale margin in revenue)', compute='_compute_spec_totals', store=True)
    estimated_probability = fields.Selection([('30', '30'), ('50', '50'),('75', '75'), ('100', '100')], required=True, string='estimated_probability of project implementation',
                                         default='0.3', copy=True)
    legal_entity_signing_id = fields.Many2one('project_budget.legal_entity_signing', string='legal_entity_signing a contract from the NCC', required=True, copy=True)
    project_type_id = fields.Many2one('project_budget.project_type',
                                              string='project_type', required=True,
                                              copy=True)
    comments  = fields.Text(string='comments project', default = "")
    technological_direction_id = fields.Many2one('project_budget.technological_direction',
                                              string='technological_direction', required=True,copy=True)

    @ api.onchange("revenue_from_the_sale_of_works", 'revenue_from_the_sale_of_goods', 'cost_of_goods', 'own_works_fot',
    'third_party_works', "awards_on_results_project", 'transportation_expenses', 'travel_expenses', 'representation_expenses',
    'taxes_fot_premiums', "warranty_service_costs", 'rko_other', 'other_expenses')
    def _compute_spec_totals(self):
        for budget_spec in self:
            budget_spec.total_amount_of_revenue = budget_spec.revenue_from_the_sale_of_works + budget_spec.revenue_from_the_sale_of_goods
            budget_spec.cost_price = budget_spec.cost_of_goods + budget_spec.own_works_fot+ budget_spec.third_party_works +budget_spec.awards_on_results_project
            budget_spec.cost_price = budget_spec.cost_price + budget_spec.transportation_expenses+budget_spec.travel_expenses+budget_spec.representation_expenses
            budget_spec.cost_price = budget_spec.cost_price + budget_spec.taxes_fot_premiums+budget_spec.warranty_service_costs+budget_spec.rko_other+budget_spec.other_expenses
            budget_spec.margin_income = budget_spec.total_amount_of_revenue - budget_spec.cost_price
            if budget_spec.total_amount_of_revenue == 0 :
                budget_spec.profitability = 0
            else:
                budget_spec.profitability = budget_spec.margin_income / budget_spec.total_amount_of_revenue * 100

    @ api.depends('commercial_budget_id.currency_id','commercial_budget_id.budget_state')
    def _compute_reference(self):
        for budget_spec in self:
            budget_spec.currency_id = budget_spec.commercial_budget_id.currency_id
            budget_spec.budget_state = budget_spec.commercial_budget_id.budget_state

    @api.depends('end_presale_project_month','end_sale_project_month')
    def _compute_quarter(self):
        for fieldquarter in self:
            if fieldquarter.end_presale_project_month == False:
                continue
            tmp_date = fieldquarter.end_presale_project_month
            month = tmp_date.month
            year = tmp_date.year
            if 0 <= int(month) <= 3:
                fieldquarter.end_presale_project_quarter = 'Q1 ' + str(year)
            elif 4 <= int(month) <= 6:
                fieldquarter.end_presale_project_quarter = 'Q2 ' + str(year)
            elif 7 <= int(month) <= 9:
                fieldquarter.end_presale_project_quarter = 'Q3 ' + str(year)
            elif 10 <= int(month) <= 12:
                fieldquarter.end_presale_project_quarter = 'Q4 ' + str(year)
            else:
                fieldquarter.end_presale_project_quarter = 'NA'
            tmp_date = fieldquarter.end_sale_project_month
            month = tmp_date.month
            year = tmp_date.year
            if 0 <= int(month) <= 3:
                fieldquarter.end_sale_project_quarter = 'Q1 ' + str(year)
            elif 4 <= int(month) <= 6:
                fieldquarter.end_sale_project_quarter = 'Q2 ' + str(year)
            elif 7 <= int(month) <= 9:
                fieldquarter.end_sale_project_quarter = 'Q3 ' + str(year)
            elif 10 <= int(month) <= 12:
                fieldquarter.end_sale_project_quarter = 'Q4 ' + str(year)
            else:
                fieldquarter.end_sale_project_quarter = 'NA'

    def create(self,vals):
        vals["project_id"]=self.env['ir.sequence'].next_by_code()

    def open_record(self):
        self.ensure_one()
        # first you need to get the id of your record
        # you didn't specify what you want to edit exactly
        rec_id = self.id
        # then if you have more than one form view then specify the form id
        form_id = self.env.ref('project_budget.show_comercial_budget_spec_form')
        # then open the form
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Project',
            'res_model': 'project_budget.commercial_budget_spec',
            'res_id': rec_id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_id.id,
            'context': {},
            # if you want to open the form in edit mode direclty
            'flags': {'initial_mode': 'edit'},
            'target': 'new',
        }
