from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta

PROCESS_TYPES = [
    ('review', _('Review')),
    ('agreement', _('Agreement')),
    ('execution', _('Execution')),
    ('complex', _('Complex'))
]

PROCESS_STATES = [
    ('on_registration', _('On Registration'))
]


# todo: необходима возможность выбора роли, возможно каких-то предопределенных методов
def selection_executor_model():
    return [('res.users', _('User'))]


class Process(models.Model):
    _name = 'document_flow.process'
    _description = 'Process'

    @api.model
    def _selection_executor_model(self):
        return selection_executor_model()

    name = fields.Char(string='Name', required=True, copy=True)
    description = fields.Html(string='Description', copy=True)
    type = fields.Selection(PROCESS_TYPES, required=True, default='review', index=True, string='Type')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    template_id = fields.Many2one('document_flow.process.template', string='Template',
                                  domain="[('type', '=', type)]")
    parent_id = fields.Many2one('document_flow.process', string='Parent Process', ondelete='cascade', index=True)
    executor_ids = fields.One2many('document_flow.process.executor', 'process_id', string='Executors')

    is_started = fields.Boolean(string='Is Started', default=False)
    is_closed = fields.Boolean(string='Is Closed', default=False)
    date_start = fields.Datetime(string='Date Start', default=fields.Datetime.now())
    date_end = fields.Datetime(string='Date End')
    date_deadline = fields.Datetime(string='Date Deadline')

    reviewer_ref = fields.Reference(string='Reviewer', selection='_selection_executor_model', store=True)
    reviewer_ref_id = fields.Integer(string='Reviewer Id', index=True, copy=False)
    reviewer_ref_type = fields.Char(string='Reviewer Type', index=True, copy=False)

    controller_ref = fields.Reference(string='Controller', selection='_selection_executor_model', store=True)
    controller_ref_id = fields.Integer(string="Controller Id", index=True, copy=False)
    controller_ref_type = fields.Char(string="Controller Type", index=True, copy=False)

    process_ids = fields.One2many('document_flow.process', 'parent_id', string='Processes')
    task_ids = fields.One2many('task.task', 'parent_ref_id', string='Tasks',
                               domain=lambda self: [('parent_ref_type', '=', 'document_flow.process')])
    sequence = fields.Integer(string='Sequence')

    # task_ids = fields.One2many('task.task', 'parent_ref_id', string='Tasks', compute='_compute_task_ids', readonly=True,
    #                            store=True)

    @api.depends('reviewer_ref_type', 'reviewer_ref_id')
    def _compute_reviewer_ref(self):
        for process in self:
            if process.reviewer_ref_type and process.reviewer_ref_type in self.env:
                process.reviewer_ref = '%s,%s' % (process.reviewer_ref_type, process.reviewer_ref_id or 0)
            else:
                process.reviewer_ref = False

    @api.depends('controller_ref_type', 'controller_ref_id')
    def _compute_controller_ref(self):
        for process in self:
            if process.controller_ref_type and process.controller_ref_type in self.env:
                process.controller_ref = '%s,%s' % (process.controller_ref_type, process.controller_ref_id or 0)
            else:
                process.controller_ref = False

    @api.onchange('template_id')
    def _onchange_template(self):
        if self.template_id and not self.executor_ids:
            self.name = self.template_id.name
            self.description = self.template_id.description
            self.type = self.template_id.type
            self.reviewer_ref = self.template_id.reviewer_ref
            self.date_deadline = fields.Datetime.now() + timedelta(self.template_id.deadline)

            for executor in self.template_id.executor_ids:
                self.env['document_flow.process.executor'].create({
                    'process_id': self.id,
                    'executor_ref': '%s,%s' % (type(executor.executor_ref).__name__, executor.executor_ref.id),
                    'date_deadline': fields.Datetime.now() + timedelta(executor.deadline)
                })

    def action_start_process(self):
        if not self.is_started:
            if self.type == 'complex':
                self.start_complex_process()
            elif self.type == 'review':
                self.start_review_process()
            elif self.type == 'agreement':
                self.start_agreement_process()
            elif self.type == 'execution':
                self.start_execution_process()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': _("Tasks were created for the following user(s)"),
                # 'message': _("Tasks were created for the following user(s): %s",
                #              ', '.join(self.executor_ids.mapped('executor_ref.name'))),
            }
        }

    def start_review_process(self):
        if self.executor_ids:
            for executor in self.executor_ids:
                task = self.env['task.task'].create({
                    'name': self.name,
                    'type': self.type,
                    'description': self.description,
                    'parent_ref': '%s,%s' % (self._name, self.id),
                    'parent_ref_type': self._name,
                    'parent_ref_id': self.id,
                    'date_deadline': executor.date_deadline,
                    'user_ids': [(4, executor.executor_ref.id)]
                })
                # TODO: создание активности необходимо перенести в таски, при создании/изменении исполнителя
                task.action_create_activity()

    # TODO: разобраться с reviewer, нужен ли и какой процесс
    def start_agreement_process(self):
        if self.executor_ids:
            for executor in self.executor_ids:
                task = self.env['task.task'].create({
                    'name': self.name,
                    'type': self.type,
                    'description': self.description,
                    'parent_ref': '%s,%s' % (self._name, self.id),
                    'parent_ref_type': self._name,
                    'parent_ref_id': self.id,
                    'date_deadline': executor.date_deadline,
                    'user_ids': [(4, executor.executor_ref.id)]
                })
                task.action_create_activity()
            self.write({'is_started': True})

    def start_execution_process(self):
        if self.executor_ids:
            for executor in self.executor_ids:
                task = self.env['task.task'].create({
                    'name': self.name,
                    'type': self.type,
                    'description': self.description,
                    'parent_ref': '%s,%s' % (self._name, self.id),
                    'parent_ref_type': self._name,
                    'parent_ref_id': self.id,
                    'date_deadline': executor.date_deadline,
                    'user_ids': [(4, executor.executor_ref.id)]
                })
                task.action_create_activity()
            self.write({'is_started': True})

    def start_complex_process(self):
        min_sequence = self.process_ids.search([
            ('parent_id', '=', self.id)
        ], order='sequence, id', limit=1).sequence or 0
        for process in self.process_ids.search([
            ('parent_id', '=', self.id),
            ('sequence', '=', min_sequence)
        ], order='id'):
            process.action_start_process()
        self.write({'is_started': True})

    def process_task_result(self, date_closed):
        if self.parent_id:
            next_sequence = self.parent_id.process_ids.search([
                ('parent_id', '=', self.parent_id.id),
                ('sequence', '>', self.sequence)
            ], order='sequence, id', limit=1).sequence or False
            if not next_sequence:
                if not self.parent_id.process_ids.search([
                    ('id', '!=', self.id),
                    ('parent_id', '=', self.parent_id.id),
                    ('sequence', '=', self.sequence),
                    ('is_closed', '=', False)
                ]):
                    self.parent_id.write({'is_closed': True, 'date_end': date_closed})
            else:
                for process in self.process_ids.search([
                    ('parent_id', '=', self.parent_id.id),
                    ('sequence', '=', next_sequence)
                ], order='id'):
                    process.action_start_process()
        self.write({'is_closed': True, 'date_end': date_closed})


class ProcessExecutor(models.Model):
    _name = 'document_flow.process.executor'
    _description = 'Process Executor'

    @api.model
    def _selection_executor_model(self):
        return selection_executor_model()

    process_id = fields.Many2one('document_flow.process', string='Process', ondelete='cascade', index=True,
                                 required=True)
    description = fields.Html(string='Description')
    executor_ref = fields.Reference(string='Executor', selection='_selection_executor_model', store=True)
    executor_ref_id = fields.Integer(string='Executor Id', index=True, copy=False)
    executor_ref_type = fields.Char(string='Executor Type', index=True, copy=False)
    date_deadline = fields.Date(string='Deadline')
    sequence = fields.Integer(string='Sequence')

    @api.depends('executor_ref_type', 'executor_ref_id')
    def _compute_executor_ref(self):
        for executor in self:
            if executor.executor_ref_type and executor.executor_ref_type in self.env:
                executor.executor_ref = '%s,%s' % (executor.executor_ref_type, executor.executor_ref_id or 0)
            else:
                executor.executor_ref = False


class ProcessTemplate(models.Model):
    _name = 'document_flow.process.template'
    _description = 'Process Template'

    @api.model
    def _selection_executor_model(self):
        return selection_executor_model()

    name = fields.Char(string='Name', required=True)
    description = fields.Html(string='Description')
    type = fields.Selection(PROCESS_TYPES, required=True, default='review', index=True, string='Type')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    executor_ids = fields.One2many('document_flow.process.template.executor', 'template_id', string='Executors')

    reviewer_ref = fields.Reference(string='Reviewer', selection='_selection_executor_model', store=True)
    reviewer_ref_id = fields.Integer(string='Reviewer Id', index=True, copy=False)
    reviewer_ref_type = fields.Char(string='Reviewer Type', index=True, copy=False)
    deadline = fields.Integer(string='Deadline')

    @api.depends('reviewer_ref_type', 'reviewer_ref_id')
    def _compute_executor_ref(self):
        for template in self:
            if template.reviewer_ref_type and template.reviewer_ref_type in self.env:
                template.reviewer_ref = '%s,%s' % (template.reviewer_ref_type, template.reviewer_ref_id or 0)
            else:
                template.reviewer_ref = False


class ProcessTemplateExecutor(models.Model):
    _name = 'document_flow.process.template.executor'
    _description = 'Process Template Executor'

    @api.model
    def _selection_executor_model(self):
        return selection_executor_model()

    template_id = fields.Many2one('document_flow.process.template', string='Template')
    executor_ref = fields.Reference(string='Executor', selection='_selection_executor_model', store=True)
    executor_ref_id = fields.Integer(string='Executor Id', index=True, copy=False)
    executor_ref_type = fields.Char(string='Executor Type', index=True, copy=False)
    deadline = fields.Integer(string='Deadline')

    @api.depends('executor_ref_type', 'executor_ref_id')
    def _compute_executor_ref(self):
        for executor in self:
            if executor.executor_ref_type and executor.executor_ref_type in self.env:
                executor.executor_ref = '%s,%s' % (executor.executor_ref_type, executor.executor_ref_id or 0)
            else:
                executor.executor_ref = False


class ProcessTask(models.Model):
    _inherit = "task.task"

    @api.model
    def _selection_parent_model(self):
        types = super(ProcessTask, self)._selection_parent_model()
        types.append(('document_flow.process', _('Process')))
        return types
