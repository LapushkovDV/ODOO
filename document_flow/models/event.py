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
    venue = fields.Char(string='Venue', index=False, copy=False)

    organizer_id = fields.Many2one('res.users', string='Organizer')
    member_ids = fields.Many2many('res.users', relation='event_user_rel', column1='event_id', column2='user_id',
                                  string='Members', tracking=True)
    question_ids = fields.One2many('document_flow.event.question', 'event_id', string='Questions')
    decision_ids = fields.One2many('document_flow.event.decision', 'event_id', string='Decisions')

    task_count = fields.Integer(compute='_compute_task_count', string='Tasks')

    def _compute_task_count(self):
        self.task_count = self.env['task.task'].search_count([
            ('parent_id', '=', False),
            ('parent_ref_type', '=', self._name),
            ('parent_ref_id', 'in', [ev.id for ev in self])
        ])

    def action_send_for_review(self):
        for member in self.member_ids:
            tasks = self.env['task.task']
            task = tasks.search([
                ('type', '=', 'review'), ('parent_ref_type', '=', self._name),
                ('parent_ref_id', '=', self.id), ('user_ids', '=', member.id)
            ])
            if not task:
                task = self.env['task.task'].create({
                    'name': _('You have new task on review by event %s', self.name),
                    'type': 'review',
                    'description': _('You have new task on review by event %s' % self.description),
                    'parent_ref': '%s,%s' % (self._name, self.id),
                    'parent_ref_type': self._name,
                    'parent_ref_id': self.id,
                    'date_deadline': self.date_end + timedelta(1),
                    'user_ids': [(4, member.id)]
                })
                activity = self.env['mail.activity'].create({
                        'display_name': _('You have new task'),
                        'summary': _('You have new task on review by event %s', self.name),
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
        pass


class EventQuestion(models.Model):
    _name = 'document_flow.event.question'
    _description = 'Event Question'

    name = fields.Char(string='Name', required=True)
    time_start = fields.Float(string="From")
    time_end = fields.Float(string="To")
    event_id = fields.Many2one('document_flow.event', string='Event', copy=False)
    speaker_ids = fields.Many2many('res.users', relation='event_question_user_rel', column1='question_id',
                                   column2='speaker_id', string='Speakers', tracking=True)


class EventDecision(models.Model):
    _name = 'document_flow.event.decision'
    _description = 'Event Decision'

    name = fields.Char(string='Decided', required=True)
    event_id = fields.Many2one('document_flow.event', string='Event', copy=False)
    executor_ids = fields.Many2many('res.users', relation='event_decision_user_rel', column1='decision_id',
                                    column2='executor_id', string='Executors', tracking=True)
    date_deadline = fields.Date(string='Deadline', index=True)


class EventTask(models.Model):
    _inherit = "task.task"

    @api.model
    def _selection_parent_model(self):
        types = super(EventTask, self)._selection_parent_model()
        types.append(('document_flow.event', _('Event')))
        return types
