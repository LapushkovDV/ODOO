from odoo import _, models, fields, api
from datetime import datetime, date, timedelta


class Event(models.Model):
    _name = 'document_flow.event'
    _description = 'Event'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    description = fields.Html(string='Description')
    date_start = fields.Datetime(string='Start Date', required=True, index=True, copy=False)
    date_end = fields.Datetime(string='End Date', required=True, index=True, copy=False)
    location = fields.Char(string='Location', index=False, copy=False)

    organizer_id = fields.Many2one('res.users', string='Organizer')
    member_ids = fields.Many2many('res.users', relation='event_user_rel', column1='event_id', column2='user_id',
                                  string='Members', tracking=True)
    question_ids = fields.One2many('document_flow.event.question', 'event_id', string='Questions')
    decision_ids = fields.One2many('document_flow.event.decision', 'event_id', string='Decisions')

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
            task.task_count = self.env['task.task'].search_count([
                ('parent_id', '=', False),
                ('parent_ref_type', '=', self._name),
                ('parent_ref_id', 'in', [ev.id for ev in self])
            ])

    def action_send_invite(self):
        pass
        # meeting = self.env['calendar.event'].create({
        #     'name': self.name,
        #     'description': self.description,
        #     'user_id': self.organizer_id,
        #     'location': self.location,
        #     'res_id': self.id,
        #     'partner_ids': [(6, 0, self.member_ids.ids)],
        #     'start': self.date_start,
        #     'stop': self.date_end
        # })

    def action_send_for_review(self):
        for member in self.member_ids:
            task = self.env['task.task'].search([
                ('type', '=', 'review'), ('parent_ref_type', '=', self._name),
                ('parent_ref_id', '=', self.id), ('user_ids', '=', member.id)
            ])
            if not task:
                task = self.env['task.task'].create({
                    'name': _('Review of result event %s', self.name),
                    'type': 'review',
                    'description': self.description,
                    'parent_ref': '%s,%s' % (self._name, self.id),
                    'parent_ref_type': self._name,
                    'parent_ref_id': self.id,
                    'date_deadline': self.date_end + timedelta(1),
                    'user_ids': [(4, member.id)]
                })
                activity = self.env['mail.activity'].create({
                        'display_name': _('You have new task'),
                        'summary': _('Review of result event %s', self.name),
                        'date_deadline': task.date_deadline,
                        'user_id': member.id,
                        'res_id': task.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'task.task')]).id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_email').id
                    })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': _("Tasks for review were created for the following user(s): %s",
                             ', '.join(self.member_ids.mapped('name'))),
            }
        }

    def action_send_for_execution(self):
        for decision in self.decision_ids:
            if decision.executor_ids:
                task = self.env['task.task'].search([
                    ('type', '=', 'execution'), ('parent_ref_type', '=', type(decision).__name__),
                    ('parent_ref_id', '=', decision.id), ('user_ids', 'in', [user.id for user in decision.executor_ids])
                ])
                if not task:
                    task = self.env['task.task'].create({
                        'name': _('To run an errand by event "%s"', self.name),
                        'type': 'execution',
                        'description': self.description,
                        'parent_ref': '%s,%s' % (type(decision).__name__, decision.id),
                        'date_deadline': decision.date_deadline,
                        'user_ids': decision.executor_ids
                    })
                    if task and len(decision.executor_ids) > 1:
                        for executor in decision.executor_ids:
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


class EventQuestion(models.Model):
    _name = 'document_flow.event.question'
    _description = 'Event Question'

    name = fields.Html(string='Agenda', required=True)
    time_start = fields.Float(string="From")
    time_end = fields.Float(string="To")
    event_id = fields.Many2one('document_flow.event', string='Event', copy=False)
    speaker_ids = fields.Many2many('res.users', relation='event_question_user_rel', column1='question_id',
                                   column2='speaker_id', string='Speakers', tracking=True)


class EventDecision(models.Model):
    _name = 'document_flow.event.decision'
    _description = 'Event Decision'

    name = fields.Html(string='Decided', required=True)
    event_id = fields.Many2one('document_flow.event', string='Event', copy=False)
    executor_ids = fields.Many2many('res.users', relation='event_decision_user_rel', column1='decision_id',
                                    column2='executor_id', string='Executors', tracking=True)
    date_deadline = fields.Date(string='Deadline', index=True)
    decision_state = fields.Char("Decision State", compute='_compute_decision_state')

    @api.depends('decision_state')
    def _compute_decision_state(self):
        for decision in self:
            decision.decision_state = self.env['task.task'].search([
                ('parent_id', '=', False),
                ('parent_ref_type', '=', self._name),
                ('parent_ref_id', '=', decision.id)
            ]).state


class EventTask(models.Model):
    _inherit = "task.task"

    @api.model
    def _selection_parent_model(self):
        types = super(EventTask, self)._selection_parent_model()
        types.append(('document_flow.event', _('Event')))
        types.append(('document_flow.event.decision', _('Decision')))
        return types
