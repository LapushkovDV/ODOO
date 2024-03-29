from odoo import api, fields, models
from .document_flow_process import selection_parent_model


class Task(models.Model):
    _inherit = 'task.task'

    @api.model
    def _selection_parent_obj_model(self):
        return selection_parent_model()

    parent_obj_ref = fields.Reference(string='Parent Object', selection='_selection_parent_obj_model',
                                      compute='_compute_parent_obj', readonly=True)
    role_executor_id = fields.Many2one('document_flow.role_executor', string='Group', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(Task, self).create(vals_list)
        for record in records:
            if record.role_executor_id and not record.user_ids:
                record._send_message_notify('task.mail_template_task_assigned_notify',
                                            record.role_executor_id.member_ids)
        return records

    # TODO: Принять решение об архитектуре предметов согласования
    def _compute_parent_obj(self):
        for task in self:
            parent_ref = False
            if task.parent_ref_type and task.parent_ref_type == 'document_flow.process' and task.parent_ref:
                parent_ref = self.env['document_flow.processing'].search([
                    ('process_ids', 'in', task.parent_ref._get_mainprocess_id_by_process_id().get(task.parent_ref.id, None))
                ]).parent_ref
            task.parent_obj_ref = parent_ref

    # @api.model
    # def check_user_group(self):
    #     """Checking user group"""
    #     user = self.env.user
    #     if user.has_group('base.group_user'):
    #         return True
    #     else:
    #         return False
    #
    # @api.model
    # def get_tasks_count(self, allowed_company_ids):
    #     my_tasks_to_do_count = self.env['task.task'].search_count([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '>=', fields.Datetime.now()),
    #         '|', ('user_ids', '=', self.env.uid),
    #         ('user_ids', 'in', self.env.user.employee_ids.get_replaceable_user_ids()),
    #         '|', ('company_ids', '=', False), ('company_ids', 'in', allowed_company_ids)
    #     ])
    #     my_tasks_overdue_count = self.env['task.task'].search_count([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '<', fields.Datetime.now()),
    #         '|', ('user_ids', '=', self.env.uid),
    #         ('user_ids', 'in', self.env.user.employee_ids.get_replaceable_user_ids()),
    #         '|', ('company_ids', '=', False), ('company_ids', 'in', allowed_company_ids)
    #     ])
    #     by_me_tasks_to_do_count = self.env['task.task'].search_count([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '>=', fields.Datetime.now()),
    #         ('author_id', '=', self.env.uid),
    #         '|', ('company_ids', '=', False), ('company_ids', 'in', allowed_company_ids)
    #     ])
    #     by_me_tasks_overdue_count = self.env['task.task'].search_count([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '<', fields.Datetime.now()),
    #         ('author_id', '=', self.env.uid),
    #         '|', ('company_ids', '=', False), ('company_ids', 'in', allowed_company_ids)
    #     ])
    #
    #     roles = self.env['document_flow.role_executor'].search([
    #         ('member_ids', 'in', self.env.uid)
    #     ])
    #     group_tasks_to_do_count = self.env['task.task'].search_count([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '>=', fields.Datetime.now()),
    #         ('user_ids', '=', False),
    #         ('role_executor_id', 'in', roles.ids),
    #         '|', ('company_ids', '=', False), ('company_ids', 'in', allowed_company_ids)
    #     ])
    #     group_tasks_overdue_count = self.env['task.task'].search_count([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '<', fields.Datetime.now()),
    #         ('user_ids', '=', False),
    #         ('role_executor_id', 'in', roles.ids),
    #         '|', ('company_ids', '=', False), ('company_ids', 'in', allowed_company_ids)
    #     ])
    #     subordinates_tasks_to_do_count = self.env['task.task'].search_count([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '>=', fields.Datetime.now()),
    #         ('user_ids', 'in', self.env.user.employee_id.subordinate_ids.user_id.ids),
    #         '|', ('company_ids', '=', False), ('company_ids', 'in', allowed_company_ids)
    #     ])
    #     subordinates_tasks_overdue_count = self.env['task.task'].search_count([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '<', fields.Datetime.now()),
    #         ('user_ids', 'in', self.env.user.employee_id.subordinate_ids.user_id.ids),
    #         '|', ('company_ids', '=', False), ('company_ids', 'in', allowed_company_ids)
    #     ])
    #
    #     values = {
    #         'my_tasks_count': my_tasks_to_do_count + my_tasks_overdue_count,
    #         'my_to_do_count': my_tasks_to_do_count,
    #         'my_overdue_count': my_tasks_overdue_count,
    #         'by_me_tasks_count': by_me_tasks_to_do_count + by_me_tasks_overdue_count,
    #         'by_me_to_do_count': by_me_tasks_to_do_count,
    #         'by_me_overdue_count': by_me_tasks_overdue_count,
    #         'group_tasks_count': group_tasks_to_do_count + group_tasks_overdue_count,
    #         'group_to_do_count': group_tasks_to_do_count,
    #         'group_overdue_count': group_tasks_overdue_count,
    #         'subordinates_tasks_count': subordinates_tasks_to_do_count + subordinates_tasks_overdue_count,
    #         'subordinates_to_do_count': subordinates_tasks_to_do_count,
    #         'subordinates_overdue_count': subordinates_tasks_overdue_count
    #     }
    #     return values
    #
    # @api.model
    # def get_tasks_view(self):
    #     my_tasks_to_do = self.env['task.task'].search([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '>=', fields.Datetime.now()),
    #         ('user_id', '=', self.env.uid)
    #     ])
    #     my_tasks_overdue = self.env['task.task'].search([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '<', fields.Datetime.now()),
    #         ('user_id', '=', self.env.uid)
    #     ])
    #     by_me_tasks_to_do = self.env['task.task'].search([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '>=', fields.Datetime.now()),
    #         ('create_uid', '=', self.env.uid)
    #     ])
    #     by_me_tasks_overdue = self.env['task.task'].search_count([
    #         ('parent_ref_type', 'like', 'document_flow.%'),
    #         ('is_closed', '=', False),
    #         ('date_deadline', '<', fields.Datetime.now()),
    #         ('create_uid', '=', self.env.uid)
    #     ])
    #
    #     my_to_do_list = []
    #     my_overdue_list = []
    #     by_me_to_do_list = []
    #     by_me_overdue_list = []
    #
    #     for task in my_tasks_to_do:
    #         my_to_do_list.append(task.name)
    #     for task in my_tasks_overdue:
    #         my_overdue_list.append(task.name)
    #     for task in by_me_tasks_to_do:
    #         by_me_to_do_list.append(task.name)
    #     for task in by_me_tasks_overdue:
    #         by_me_overdue_list.append(task.name)
    #
    #     # tasks = self.env['task.task'].search[(
    #     #     'state', 'in', ['to_do', 'assigned']
    #     # )]
    #     # p_tasks = []
    #     # for task in tasks:
    #     #     p_tasks.append(task.name)
    #
    #     values = {
    #         'my_to_do_count': len(my_tasks_to_do),
    #         'my_overdue_count': len(my_tasks_overdue),
    #         'by_me_to_do_count': len(by_me_tasks_to_do),
    #         'by_me_overdue_count': len(by_me_tasks_overdue),
    #         'group_to_do_count': len(my_tasks_to_do),
    #         'group_overdue_count': len(my_tasks_overdue),
    #
    #         'my_to_do_tasks': my_to_do_list,
    #         'my_overdue_tasks': my_overdue_list,
    #         'by_me_to_do_tasks': by_me_to_do_list,
    #         'by_me_overdue_tasks': by_me_overdue_list,
    #         'group_to_do_tasks': my_to_do_list,
    #         'group_overdue_tasks': my_overdue_list
    #         # 'p_tasks': p_tasks
    #     }
    #     return values
    #
    # @api.model
    # def get_done_tasks_pie(self):
    #     result = []
    #     tasks_count = self.env['task.task'].search_count([])
    #     tasks_done_count = self.env['task.task'].search_count([
    #         ('is_closed', '=', True)
    #     ])
    #     result.append(tasks_done_count)
    #     result.append(tasks_count - tasks_done_count)
    #
    #     return result
