from odoo import _, models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta


class Event(models.Model):
    _name = 'document_flow.event'
    _description = 'Event'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    description = fields.Html(string='Description')
    date_start = fields.Datetime(string='Start Date', required=True, index=True, copy=False)
    date_end = fields.Datetime(string='End Date', index=True, copy=False)
    location = fields.Char(string='Location', index=False, copy=False)

    organizer_id = fields.Many2one('res.users', string='Organizer')
    agreed_id = fields.Many2one('res.users', string='Agreed')
    member_ids = fields.Many2many('res.users', relation='event_user_rel', column1='event_id', column2='user_id',
                                  string='Members', tracking=True)
    question_ids = fields.One2many('document_flow.event.question', 'event_id', string='Questions')
    decision_ids = fields.One2many('document_flow.event.decision', 'event_id', string='Decisions')

    state = fields.Selection([
        ('on_registration', 'On Registration'),
        ('on_approval', 'On Approval'),
        ('approved', 'Approved'),
        ('completed', 'Completed')
    ], required=True, index=True, string='Status', default='on_registration', readonly=True, tracking=True)

    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Documents')
    task_count = fields.Integer(compute='_compute_task_count', string='Tasks')

    def _compute_attachment_count(self):
        for event in self:
            event.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', type(event).__name__),
                ('res_id', '=', event.id)
            ])

    def _compute_task_count(self):
        for task in self:
            task_count = self.env['task.task'].sudo().search_count([
                ('parent_id', '=', False),
                ('parent_ref_type', '=', self._name),
                ('parent_ref_id', 'in', [ev.id for ev in self])
            ])
            for decision in task.decision_ids:
                task_count = task_count + self.env['task.task'].sudo().search_count([
                    ('parent_id', '=', False),
                    ('parent_ref_type', '=', type(decision).__name__),
                    ('parent_ref_id', 'in', [d.id for d in decision])
                ])
            task.task_count = task_count

    def action_send_for_approval(self):
        if self.agreed_id:
            task = self.env['task.task'].search([
                ('type', '=', 'approving'), ('parent_ref_type', '=', self._name),
                ('parent_ref_id', '=', self.id), ('user_ids', '=', self.agreed_id.id)
            ])
            if not task:
                task = self.env['task.task'].create({
                    'name': _('Approval on a protocol of event %s', self.name),
                    'type': 'approving',
                    'description': self.description,
                    'parent_ref': '%s,%s' % (self._name, self.id),
                    'parent_ref_type': self._name,
                    'parent_ref_id': self.id,
                    'date_deadline': datetime.now(),
                    'user_ids': [(4, self.agreed_id.id)]
                })
            else:
                task.action_to_do()
            activity = self.env['mail.activity'].create({
                'display_name': _('You have new request for approval'),
                'summary': _('Approval on a protocol of event %s', self.name),
                'date_deadline': datetime.now(),
                'user_id': self.agreed_id.id,
                'res_id': task.id,
                'res_model_id': self.env['ir.model'].search([('model', '=', 'task.task')]).id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id
            })
        self.write({'state': 'on_approval'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': _("Request for approval on a protocol was send for the user: %s") % self.agreed_id.name
            }
        }

    def action_decline_approval(self):
        self.write({'state': 'on_registration'})
        if self.organizer_id:
            self.env['mail.activity'].create({
                'display_name': _('Protocol was declined'),
                'summary': _('Protocol of event %s was declined', self.name),
                'date_deadline': datetime.now(),
                'user_id': self.organizer_id.id,
                'res_id': self.id,
                'res_model_id': self.env['ir.model'].search([('model', '=', self._name)]).id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id
            })

    def action_accept_approval(self):
        self.write({'state': 'approved'})
        if self.organizer_id:
            self.env['mail.activity'].create({
                'display_name': _('Protocol was approved'),
                'summary': _('Protocol of event %s was approved', self.name),
                'date_deadline': datetime.now(),
                'user_id': self.organizer_id.id,
                'res_id': self.id,
                'res_model_id': self.env['ir.model'].search([('model', '=', self._name)]).id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id
            })

    def action_send_for_execution(self):
        for decision in self.decision_ids:
            task = False
            if decision.responsible_id:
                task = self.env['task.task'].search([
                    ('type', '=', decision.task_type), ('parent_ref_type', '=', type(decision).__name__),
                    ('parent_ref_id', '=', decision.id), ('parent_id', '=', False),
                    ('user_ids', '=', decision.responsible_id.id)
                ])
                if not task:
                    task = self.env['task.task'].create({
                        'name': _('To run an errand by event "%s"', self.name),
                        'type': decision.task_type,
                        'description': decision.name,
                        'parent_ref': '%s,%s' % (type(decision).__name__, decision.id),
                        'date_deadline': decision.date_deadline,
                        'user_ids': decision.responsible_id
                    })
                    activity = self.env['mail.activity'].create({
                        'display_name': _('You have new task'),
                        'summary': _('To run an errand by event "%s"', self.name),
                        'date_deadline': task.date_deadline,
                        'user_id': decision.responsible_id.id,
                        'res_id': task.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'task.task')]).id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_email').id
                    })
            if decision.executor_ids:
                if not task:
                    task = self.env['task.task'].search([
                        ('type', '=', decision.task_type), ('parent_ref_type', '=', type(decision).__name__),
                        ('parent_ref_id', '=', decision.id), ('parent_id', '=', False),
                        ('user_ids', '=', decision.executor_ids.ids)
                    ])
                if not task:
                    task = self.env['task.task'].create({
                        'name': _('To run an errand by event "%s"', self.name),
                        'type': decision.task_type,
                        'description': decision.name,
                        'parent_ref': '%s,%s' % (type(decision).__name__, decision.id),
                        'date_deadline': decision.date_deadline,
                        'user_ids': decision.executor_ids
                    })
                if task and (decision.responsible_id or len(decision.executor_ids) > 1):
                    for executor in decision.executor_ids:
                        sub_task = self.env['task.task'].search([
                            ('type', '=', decision.task_type), ('parent_ref_type', '=', type(decision).__name__),
                            ('parent_ref_id', '=', decision.id), ('parent_id', '=', task.id),
                            ('user_ids', '=', executor.id)
                        ])
                        if not sub_task:
                            sub_task = self.env['task.task'].create({
                                'name': task.name,
                                'type': task.type,
                                'description': self.description,
                                'parent_id': task.id,
                                'parent_ref': '%s,%s' % (type(decision).__name__, decision.id),
                                'date_deadline': task.date_deadline,
                                'user_ids': [(4, executor.id)]
                            })
                            activity = self.env['mail.activity'].create({
                                'display_name': _('You have new task'),
                                'summary': _('To run an errand by event "%s"', self.name),
                                'date_deadline': task.date_deadline,
                                'user_id': executor.id,
                                'res_id': sub_task.id,
                                'res_model_id': self.env['ir.model'].search([('model', '=', 'task.task')]).id,
                                'activity_type_id': self.env.ref('mail.mail_activity_data_email').id
                            })
                activities = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('res_model_id', '=', self.env['ir.model'].search([('model', '=', self._name)]).id),
                    ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_email').id)
                ])
                for activity in activities:
                    activity.action_done()
        self.write({'state': 'completed'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': _("Tasks for execution were created for the following user(s): %s",
                             ', '.join(self.decision_ids.executor_ids.mapped('name'))),
            }
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
                """ % _("Add attachments for this event")
        }

    def action_open_tasks(self):
        self.ensure_one()
        task_ids = self.env['task.task'].sudo().search([
            ('parent_id', '=', False),
            ('parent_ref_type', '=', self._name),
            ('parent_ref_id', 'in', self.ids)
        ]).ids
        task_ids.extend(self.env['task.task'].sudo().search([
            ('parent_id', '=', False),
            ('parent_ref_type', '=', 'document_flow.event.decision'),
            ('parent_ref_id', 'in', self.decision_ids.ids)
        ]).ids)
        return {
            'name': _('Tasks'),
            'domain': [
                ('id', 'in', task_ids)
            ],
            'res_model': 'task.task',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form'
        }


class EventQuestion(models.Model):
    _name = 'document_flow.event.question'
    _description = 'Event Question'

    name = fields.Html(string='Agenda', required=True)
    time_start = fields.Float(string="From")
    time_end = fields.Float(string="To")
    event_id = fields.Many2one('document_flow.event', string='Event', copy=False)
    speaker_ids = fields.Many2many('res.users', relation='event_question_user_rel', column1='question_id',
                                   column2='speaker_id', string='Speakers')


class EventDecision(models.Model):
    _name = 'document_flow.event.decision'
    _description = 'Event Decision'
    _order = 'num, id'

    num = fields.Integer(string='№', required=True)
    name = fields.Html(string='Decided', required=True)
    event_id = fields.Many2one('document_flow.event', string='Event', copy=False)
    task_type = fields.Selection([
        ('review', 'Review'),
        ('execution', 'Execution')
    ], required=True, default='review', string='Type')
    responsible_id = fields.Many2one('res.users', string='Responsible')
    executor_ids = fields.Many2many('res.users', relation='event_decision_user_rel', column1='decision_id',
                                    column2='executor_id', string='Executors')
    date_deadline = fields.Date(string='Deadline', index=True)
    task_id = fields.Many2one('task.task', string='Task', compute='_compute_task_id')
    date_execution = fields.Date(string="Execution Date", related='task_id.date_closed')
    decision_state = fields.Selection(string="Decision State", related='task_id.state')

    deadline_type = fields.Selection([
        ('to_date', 'To Date'),
        ('after_decision', 'After Decision')
    ], required=True, default='to_date', string='Deadline Type')
    number_days = fields.Integer(string='Within')
    after_decision_id = fields.Many2one('document_flow.event.decision', string='After Decision',
                                        domain='[("event_id", "=", event_id), ("id", "!=", id)]')

    def name_get(self):
        decisions = []
        for decision in self:
            name = '%s %s' % (decision.num, decision.name.striptags())
            decisions.append((decision.id, name))
        return decisions

    @api.depends('task_id')
    def _compute_task_id(self):
        for decision in self:
            decision.task_id = self.env['task.task'].sudo().search([
                ('parent_id', '=', False),
                ('parent_ref_type', '=', self._name),
                ('parent_ref_id', '=', decision.id)
            ], limit=1)

    @api.depends('decision_state')
    def _compute_decision_state(self):
        for decision in self:
            decision.decision_state = self.env['task.task'].sudo().search([
                ('parent_id', '=', False),
                ('parent_ref_type', '=', self._name),
                ('parent_ref_id', '=', decision.id)
            ]).state

    @api.onchange('deadline_type', 'after_decision_id', 'number_days')
    def onchange_date_deadline(self):
        for decision in self:
            if decision.deadline_type == 'to_date':
                decision.after_decision_id = False
                decision.number_days = False
            elif decision.deadline_type == 'after_decision' and decision.number_days:
                decision.date_deadline = self._get_decision_date_deadline(decision.after_decision_id) + timedelta(
                    days=decision.number_days)

    def _get_decision_date_deadline(self, decision):
        if decision.deadline_type == 'to_date':
            return decision.date_deadline
        elif decision.deadline_type == 'after_decision' and decision.prev_decision_id:
            return self._get_decision_date_deadline(decision.prev_decision_id) + timedelta(
                days=decision.number_days)
        else:
            return decision.date_deadline

    def unlink(self):
        self.mapped('task_id').unlink()
        return super(EventDecision, self).unlink()


class EventTask(models.Model):
    _inherit = "task.task"

    @api.model
    def _selection_parent_model(self):
        types = super(EventTask, self)._selection_parent_model()
        types.append(('document_flow.event', _('Event')))
        types.append(('document_flow.event.decision', _('Decision')))
        return types
