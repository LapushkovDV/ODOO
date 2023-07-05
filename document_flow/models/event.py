from odoo import _, models, fields, api
from datetime import datetime, date, timedelta


class Event(models.Model):
    _name = 'document_flow.event'
    _description = 'Event'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, copy=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    description = fields.Html(string='Description')
    date_start = fields.Datetime(string='Start Date', required=True, index=True, copy=True)
    date_end = fields.Datetime(string='End Date', index=True, copy=False)
    location = fields.Char(string='Location')

    organizer_id = fields.Many2one('res.users', string='Organizer')
    agreed_id = fields.Many2one('res.users', string='Agreed')
    member_ids = fields.Many2many('res.users', relation='event_user_rel', column1='event_id', column2='user_id',
                                  string='Members')
    management_committee_id = fields.Many2one('document_flow.management_committee', string='Management Committee')
    question_ids = fields.One2many('document_flow.event.question', 'event_id', string='Questions')
    decision_ids = fields.One2many('document_flow.event.decision', 'event_id', string='Decisions', copy=True)
    annex_ids = fields.One2many('document_flow.event.annex', 'event_id', string='Annexes')

    state = fields.Selection([
        ('on_registration', 'On Registration'),
        ('on_approval', 'On Approval'),
        ('approved', 'Approved'),
        ('completed', 'Completed')
    ], required=True, index=True, string='Status', default='on_registration', readonly=True, tracking=True, copy=False)

    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Documents')
    task_count = fields.Integer(compute='_compute_task_count', string='Tasks')
    decision_count = fields.Integer(compute='_compute_decision_count')
    annex_count = fields.Integer(compute='_compute_annex_count')

    is_process_started = fields.Boolean(compute='_compute_is_process_started')

    @api.onchange('decision_ids')
    def _onchange_decisions(self):
        self._compute_decision_count()

    @api.onchange('annex_ids')
    def _onchange_decisions(self):
        self._compute_annex_count()

    @api.onchange('management_committee_id')
    def _onchange_management_committee(self):
        if self.management_committee_id and not self.member_ids:
            self.member_ids = self.management_committee_id.member_ids

    def _compute_attachment_count(self):
        for event in self:
            event.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', type(event).__name__),
                ('res_id', '=', event.id)
            ])

    def _compute_task_count(self):
        for task in self:
            task_count = self.env['task.task'].search_count([
                ('parent_id', '=', False),
                ('parent_ref_type', '=', self._name),
                ('parent_ref_id', 'in', [ev.id for ev in self])
            ])
            for decision in task.decision_ids:
                task_count = task_count + self.env['task.task'].search_count([
                    ('parent_id', '=', False),
                    ('parent_ref_type', '=', type(decision).__name__),
                    ('parent_ref_id', 'in', [d.id for d in decision])
                ])
            task.task_count = task_count

    def _compute_decision_count(self):
        for event in self:
            event.decision_count = len(self.decision_ids) + 1

    def _compute_annex_count(self):
        for event in self:
            event.annex_count = len(self.annex_ids) + 1

    def _compute_is_process_started(self):
        for event in self:
            event.is_process_started = self.env['document_flow.process.parent_object'].sudo().search_count([
                ('parent_ref_type', '=', self._name),
                ('parent_ref_id', '=', event.id),
                ('process_id', '!=', False),
                ('process_id.type', '=', 'complex'),
                ('process_id.state', 'in', ('on_registration', 'started', 'finished'))
            ]) > 0

    def action_send_for_approving(self):
        if self.agreed_id:
            complex_process = self.env['document_flow.process'].create({
                'name': _('Agree on a protocol of event "%s"', self.name),
                'type': 'complex',
                'description': self.description
            })

            link = self.env['document_flow.process.parent_object'].create({
                'process_id': complex_process.id,
                'parent_ref': '%s,%s' % (self._name, self.id),
                'parent_ref_id': self.id,
                'parent_ref_type': self._name
            })

            process_agreement = self.env['document_flow.process'].create({
                'name': _('Agree on a protocol of event "%s"', self.name),
                'type': 'agreement',
                'sequence': 0,
                'description': self.description,
                'parent_id': complex_process.id
            })
            process_agreement_executor = self.env['document_flow.process.executor'].create({
                'process_id': process_agreement.id,
                'executor_ref': '%s,%s' % (type(self.agreed_id).__name__, self.agreed_id.id),
                'date_deadline': datetime.now()
            })

            link = self.env['document_flow.process.parent_object'].create({
                'process_id': process_agreement.id,
                'parent_ref': '%s,%s' % (self._name, self.id),
                'parent_ref_id': self.id,
                'parent_ref_type': self._name
            })

            process_review = self.env['document_flow.process'].create({
                'name': _('Review a protocol of event "%s"', self.name),
                'type': 'review',
                'sequence': 1,
                'description': self.description,
                'parent_id': complex_process.id
            })
            for executor in list(set(self.member_ids) | set(self.management_committee_id.member_ids)):
                process_review_executor = self.env['document_flow.process.executor'].create({
                    'process_id': process_review.id,
                    'executor_ref': '%s,%s' % (type(executor).__name__, executor.id),
                    'date_deadline': datetime.now()
                })

            link = self.env['document_flow.process.parent_object'].create({
                'process_id': process_review.id,
                'parent_ref': '%s,%s' % (self._name, self.id),
                'parent_ref_id': self.id,
                'parent_ref_type': self._name
            })

            reviews = self.decision_ids.search([
                ('task_type', '=', 'review'),
                ('date_deadline', '!=', False),
                ('executor_ids', '!=', False)
            ])
            if reviews.ids:
                for decision in reviews:
                    process_review = self.env['document_flow.process'].create({
                        'name': _('Review with decision of event "%s"', self.name),
                        'type': 'review',
                        'sequence': 1,
                        'description': decision.name,
                        'parent_id': complex_process.id
                    })
                    for executor in decision.executor_ids:
                        process_review_executor = self.env['document_flow.process.executor'].create({
                            'process_id': process_review.id,
                            'executor_ref': '%s,%s' % (type(executor).__name__, executor.id),
                            'date_deadline': decision.date_deadline
                        })
                    link = self.env['document_flow.process.parent_object'].create({
                        'process_id': process_review.id,
                        'parent_ref': '%s,%s' % (type(decision).__name__, decision.id),
                        'parent_ref_id': decision.id,
                        'parent_ref_type': type(decision).__name__
                    })

            executions = self.decision_ids.search([
                "&", "&",
                ('task_type', '=', 'execution'),
                ('date_deadline', '!=', False),
                "|",
                ('executor_ids', '!=', False),
                ('responsible_id', '!=', False)
            ])
            if executions.ids:
                for decision in executions:
                    process_execution = self.env['document_flow.process'].create({
                        'name': _('Execute decision of event "%s"', self.name),
                        'type': 'execution',
                        'sequence': 1,
                        'description': decision.name,
                        'parent_id': complex_process.id
                    })
                    # TODO: свернуть в 1 запись
                    if decision.responsible_id and decision.executor_ids:
                        process_execution.write({
                            'reviewer_ref': '%s,%s' % (type(decision.responsible_id).__name__, decision.responsible_id.id)
                        })
                    if decision.executor_ids:
                        for executor in decision.executor_ids:
                            process_execution_executor = self.env['document_flow.process.executor'].create({
                                'process_id': process_execution.id,
                                'executor_ref': '%s,%s' % (type(executor).__name__, executor.id),
                                'date_deadline': decision.date_deadline
                            })
                    elif decision.responsible_id:
                        process_execution_executor = self.env['document_flow.process.executor'].create({
                            'process_id': process_execution.id,
                            'executor_ref': '%s,%s' % (type(decision.responsible_id).__name__, decision.responsible_id.id),
                            'date_deadline': decision.date_deadline
                        })
                    link = self.env['document_flow.process.parent_object'].create({
                        'process_id': process_execution.id,
                        'parent_ref': '%s,%s' % (type(decision).__name__, decision.id),
                        'parent_ref_id': decision.id,
                        'parent_ref_type': type(decision).__name__
                    })
            complex_process.action_start_process()

        self.write({'state': 'on_approval'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': _("The process of agreement a protocol were started"),
                'next': {'type': 'ir.actions.act_window_close'}
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
    event_id = fields.Many2one('document_flow.event', string='Event', ondelete='cascade', index=True, required=True)
    speaker_ids = fields.Many2many('res.users', relation='event_question_user_rel', column1='question_id',
                                   column2='speaker_id', string='Speakers')


class EventDecision(models.Model):
    _name = 'document_flow.event.decision'
    _description = 'Event Decision'
    _order = 'num, id'

    num = fields.Integer(string='№', required=True, copy=True)
    name = fields.Html(string='Decided', required=True, copy=True)
    event_id = fields.Many2one('document_flow.event', string='Event', ondelete='cascade', index=True, required=True)
    task_type = fields.Selection([
        ('review', 'Review'),
        ('execution', 'Execution')
    ], required=True, default='review', string='Type')
    responsible_id = fields.Many2one('res.users', string='Responsible')
    executor_ids = fields.Many2many('res.users', relation='event_decision_user_rel', column1='decision_id',
                                    column2='executor_id', string='Executors')
    date_deadline = fields.Date(string='Deadline', index=True)
    process_id = fields.Many2one('document_flow.process', string='Process', compute='_compute_process_id')
    date_execution = fields.Datetime(string='Execution Date', related='process_id.date_end', readonly=True)
    decision_state = fields.Selection(string="Decision State", related='process_id.state', readonly=True)

    deadline_type = fields.Selection([
        ('to_date', 'To Date'),
        ('after_decision', 'After Decision')
    ], required=True, default='to_date', string='Deadline Type')
    number_days = fields.Integer(string='Within')
    after_decision_id = fields.Many2one('document_flow.event.decision', string='After Decision',
                                        domain="[('id', 'in', parent.decision_ids), ('id', '!=', id)]")

    repeat_interval = fields.Selection([
        ('week', 'Weeks'),
        ('month', 'Months'),
        ('quarter', 'Quarter'),
        ('year', 'Years'),
    ], required=False, string='Repeat Interval')

    def name_get(self):
        decisions = []
        for decision in self:
            name = '%s %s' % (decision.num, decision.name.striptags())
            decisions.append((decision.id, name))
        return decisions

    @api.depends('process_id')
    def _compute_process_id(self):
        for decision in self:
            decision.process_id = self.env['document_flow.process.parent_object'].sudo().search([
                ('parent_ref_type', '=', self._name),
                ('parent_ref_id', '=', decision.id),
                ('process_id', '!=', False),
                ('process_id.state', '!=', 'break')
            ], limit=1).process_id

    @api.onchange('deadline_type', 'after_decision_id', 'number_days')
    def onchange_date_deadline(self):
        if self.deadline_type == 'to_date':
            self.after_decision_id = False
            self.number_days = False
        elif self.deadline_type == 'after_decision' and self.number_days:
            self.date_deadline = self._get_decision_date_deadline(self.after_decision_id) + timedelta(
                days=self.number_days)

    def _get_decision_date_deadline(self, decision):
        if decision.deadline_type == 'to_date':
            return decision.date_deadline
        elif decision.deadline_type == 'after_decision' and decision.prev_decision_id:
            return self._get_decision_date_deadline(decision.prev_decision_id) + timedelta(
                days=decision.number_days)
        else:
            return decision.date_deadline

    def unlink(self):
        self.mapped('process_id').unlink()
        return super(EventDecision, self).unlink()


class EventAnnex(models.Model):
    _name = 'document_flow.event.annex'
    _description = 'Event Annex'
    _order = 'num, id'

    num = fields.Integer(string='№', required=True)
    name = fields.Html(string='Name', required=True)
    event_id = fields.Many2one('document_flow.event', string='Event', ondelete='cascade', index=True, required=True)