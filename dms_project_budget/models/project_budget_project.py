from odoo import api, fields, models


class Project(models.Model):
    _name = 'project_budget.projects'
    _inherit = ['project_budget.projects', 'dms.document.mixin']

    directory_id = fields.Many2one('dms.directory', string='Directory', ondelete='set null')
    document_count = fields.Integer(related='directory_id.document_total_count', string='Documents Count',
                                    readonly=True)

    # TODO: сделать настройку с дефолтным каталогом в модуле?
    def _get_document_directory(self):
        return self.directory_id or self.env.ref('dms_project_budget.dms_directory_project_directory')

    @api.model
    def _init_project_document_directory(self):
        self.search([('directory_id', '=', False), ('budget_state', '=', 'work')])._create_project_directory()

    @api.model_create_multi
    def create(self, vals_list):
        # т.к. project_id не сгенерирован перед записью, сначала дергаем метод создания. Мб precompute?
        records = super().create(vals_list)

        [project._create_project_directory() for project in
         records.filtered(lambda pr: not pr.directory_id and pr.budget_state == 'work')]

        return records

    def write(self, values):
        if not values.get('directory_id'):
            [project._create_project_directory() for project in
             self.filtered(lambda pr: not pr.directory_id and pr.budget_state == 'work')]
        return super(Project, self).write(values)

    def _create_project_directory(self):
        for project in self:
            # TODO: сделать настройку с дефолтным каталогом в модуле?
            directory = self.env['dms.directory'].create({
                'name': project.project_id,
                'parent_id': self.env.ref('dms_project_budget.dms_directory_project_directory').id
            })
            project.with_context(form_fix_budget=True).write({'directory_id': directory.id})
