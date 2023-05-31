from odoo import _, models, fields, api


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

    def action_send_for_execution(self):
        pass

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

    event_id = fields.Many2one('document_flow.event', string='Event', copy=False, tracking=True)
