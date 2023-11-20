from odoo import api, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def check_user_has_subordinates(self):
        return any(self.env.user.employee_id.child_ids)

    @api.model
    def get_subordinate_ids(self):
        return self.env.user.employee_id.subordinate_ids.user_id.ids
