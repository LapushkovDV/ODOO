from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date


class TaskType(models.Model):
    _name = 'task.task.type'
    _description = 'Task Type'

    name = fields.Char(string='Name', required=True)


class Task(models.Model):
    _name = "task.task"
    _description = "Task"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string='Title', tracking=True, required=True, index='trigram')
    description = fields.Html(string='Description')

    # type_id = fields.Many2one('task.task.type', index=True, required=True, copy=False, tracking=True)

    type = fields.Selection([
        ('review', 'Review'),
        ('approving', 'Approving'),
        ('execution', 'Execution')
    ], required=True, default='review', index=True, string='Type')

    user_ids = fields.Many2many('res.users', relation='task_task_user_rel', column1='task_id', column2='user_id',
                                string='Assignees', tracking=True)
    state = fields.Selection([
        ('to_do', 'To Do'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Canceled')
    ], required=True, index=True, string='Status', default='to_do', readonly=True, tracking=True)

    parent_ref = fields.Reference(string='Parent', selection="_selection_parent_model", compute="_compute_parent_ref",
                                  store=True)
    parent_ref_id = fields.Integer(string="Parent Id", index=True, copy=False)
    parent_ref_type = fields.Char(string="Parent Type", index=True, copy=False)

    date_deadline = fields.Date(string='Deadline', required="True", index=True, copy=False, tracking=True)
    parent_id = fields.Many2one('task.task', string='Parent Task', copy=True, tracking=True)
    child_ids = fields.One2many('task.task', 'parent_id', string="Sub-tasks")
    subtask_count = fields.Integer("Sub-task Count", compute='_compute_subtask_count')
    child_text = fields.Char(compute="_compute_child_text")
    is_closed = fields.Boolean(string="Closed", index=True)
    date_closed = fields.Date(string='Date Closed', index=True, copy=False)
    implementation_report = fields.Html(string='Report')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Documents')

    def _compute_attachment_count(self):
        for task in self:
            task.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', type(task).__name__),
                ('res_id', '=', task.id)
            ])

    @api.model
    def _selection_parent_model(self):
        return [('project_budget.projects', _('Project'))]

    @api.depends('parent_ref_type', 'parent_ref_id')
    def _compute_parent_ref(self):
        for task in self:
            if task.parent_ref_type and task.parent_ref_type in self.env:
                task.parent_ref = '%s,%s' % (task.parent_ref_type, task.parent_ref_id or 0)
            else:
                task.parent_ref = None

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('parent_ref'):
                vals['parent_ref_type'] = vals['parent_ref'].split(",")[0]
                vals['parent_ref_id'] = int(vals['parent_ref'].split(",")[1])
        return super().create(vals_list)

    @api.depends('child_ids')
    def _compute_subtask_count(self):
        for task in self:
            task.subtask_count = self.search_count([('parent_id', '=', self.id)])

    @api.depends('child_ids')
    def _compute_child_text(self):
        for task in self:
            if not task.subtask_count:
                task.child_text = False
            elif task.subtask_count == 1:
                task.child_text = _("(+ 1 task)")
            else:
                task.child_text = _("(+ %(child_count)s tasks)", child_count=task.subtask_count)

    # @api.onchange('user_ids')
    # def _onchange_user_ids(self):
    #     for task in self:
    #         if len(task.user_ids) == 1:
    #             self.env['mail.activity'].create({
    #                 'display_name': _('You have new task'),
    #                 'summary': _('You have been assigned new task "%s"', task.name),
    #                 'date_deadline': task.date_deadline,
    #                 'user_id': [(4, task.user_ids[0])],
    #                 'res_id': task.id,
    #                 'res_model_id': self.env['ir.model'].search([('model', '=', 'task.task')]).id,
    #                 'activity_type_id': self.env.ref('mail.mail_activity_data_email').id
    #             })

    def action_assign_to_user(self):
        self.write({'state': 'assigned'})
        for user in self.user_ids:
            self.env['mail.activity'].create({
                'display_name': _('You have new task'),
                'summary': _('You have new task by project %s' % self.project_id),
                'date_deadline': self.date_deadline,
                'user_id': user.id,
                'res_id': self.id,
                'res_model_id': self.env['ir.model'].search([('model', '=', 'task.task')]).id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id
            })

    def action_to_do(self):
        self.write({'state': 'to_do', 'is_closed': False, 'implementation_report': False})

    def action_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        if self.type == 'execution':
            if not self.implementation_report:
                raise ValidationError(_('Report on the implementation should be filled'))
        elif self.type == 'approving' and self.parent_ref_type == 'document_flow.event':
            event = self.env['document_flow.event'].search([
                ('id', '=', self.parent_ref_id)
            ], limit=1)
            if event:
                event.action_accept_approval()

        activities = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('res_model_id', '=', self.env['ir.model'].search([('model', '=', self._name)]).id),
            ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_email').id)
        ])
        for activity in activities:
            activity.action_done()
        self.write({'state': 'done', 'is_closed': True, 'date_closed': date.today()})

    def action_cancel(self):
        if self.type == 'approving' and self.parent_ref_type == 'document_flow.event':
            event = self.env['document_flow.event'].search([
                ('id', '=', self.parent_ref_id)
            ], limit=1)
            if event:
                event.action_decline_approval()
                if self.implementation_report:
                    event.message_post(
                        body=self.implementation_report,
                        message_type='comment',
                        subtype_xmlid='mail.mt_note')
        activities = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('res_model_id', '=', self.env['ir.model'].search([('model', '=', self._name)]).id),
            ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_email').id)
        ])
        for activity in activities:
            activity.unlink()
        self.write({'state': 'cancel', 'is_closed': True, 'date_closed': date.today()})

    def action_open_task(self):
        return {
            'view_mode': 'form',
            'res_model': 'task.task',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'context': self._context
        }

    def action_open_parent_task(self):
        return {
            'name': _('Parent Task'),
            'view_mode': 'form',
            'res_model': 'task.task',
            'res_id': self.parent_id.id,
            'type': 'ir.actions.act_window',
            'context': self._context
        }

    def action_open_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id),
            'help': """
                <p class="o_view_nocontent_smiling_face">%s</p>
                """ % _("Add attachments for this task")
        }


class ProjectBudgetTask(models.Model):
    _inherit = "project_budget.projects"

    task_count = fields.Integer(compute='_compute_task_count', string='Tasks')

    def _compute_task_count(self):
        self.task_count = self.env['task.task'].search_count([
            ('parent_id', '=', False),
            ('parent_ref_type', '=', self._name),
            ('parent_ref_id', 'in', [pr.id for pr in self])
        ])
