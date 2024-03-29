from odoo import models, fields, api, exceptions, _


class TaskStageRoute(models.Model):
    _name = 'task.stage.route'
    _description = 'Task Stage Route'
    _order = 'sequence'

    name = fields.Char(translate=True)
    sequence = fields.Integer(default=5, index=True, required=True)
    stage_from_id = fields.Many2one('task.stage', string='From', ondelete='restrict', required=True, index=True)
    stage_to_id = fields.Many2one('task.stage', string='To', ondelete='restrict', required=True, index=True)
    task_type_id = fields.Many2one('task.type', 'Task Type', ondelete='cascade', required=True, index=True)
    close = fields.Boolean(related='stage_to_id.closed', store=True, index=True, readonly=True)
    result_type = fields.Selection(related='stage_to_id.result_type', store=True, readonly=True)

    require_comment = fields.Boolean(store=True, help='If set, then user will be asked for comment on this route')

    button_style = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('success', 'Success'),
        ('danger', 'Danger'),
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('link', 'Link'),
    ], required=True, default='primary', string='Button style')

    _sql_constraints = [
        ('stage_stage_from_to_type_uniq',
         'UNIQUE (task_type_id, stage_from_id, stage_to_id)',
         'Such route already present in this task type')
    ]

    def name_get(self):
        res = []
        for record in self:
            name = "%s -> %s" % (record.stage_from_id.name, record.stage_to_id.name)
            if record.name:
                name = "%s [%s]" % (name, record.name)

            if self.env.context.get('name_only', False) and record.name:
                name = record.name

            res += [(record.id, name)]
        return res

    # todo: по идее, нужно проверять имеет ли пользователь права двигать таску, пока заглушка
    def _check_can_move(self, task):
        pass

    @api.model
    def check_route(self, task, to_stage_id):
        route = self.search([
            ('task_type_id', '=', task.type_id.id),
            ('stage_from_id', '=', task.stage_id.id),
            ('stage_to_id', '=', to_stage_id)
        ])
        if not route:
            TaskStage = self.env['task.stage']
            stage = TaskStage.browse(to_stage_id) if to_stage_id else None
            raise exceptions.ValidationError(_(
                'Cannot move task to this stage: no route.\n'
                '\tTask: %(task)s\n'
                '\tTo stage id: %(to_stage_id)s\n'
                '\tTo stage name: %(to_stage_name)s\n'
                '\tFrom stage name: %(from_stage_name)s\n'
            ) % {
                'task': task.name,
                'to_stage_id': to_stage_id,
                'to_stage_name': stage.name if stage else None,
                'from_stage_name': (task.stage_id.name if task.stage_id else None)
            })

        return route
