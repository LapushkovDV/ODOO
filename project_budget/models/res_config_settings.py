from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    tender_department_id = fields.Many2one('hr.department', string='tender department',
                                                      config_parameter='project_budget.tender_department_id')
