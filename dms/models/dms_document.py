import logging

from odoo import api, fields, models, _
from odoo.tools import image_process
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


#TODO: реализовать контроллер для загрузки документа
# Необходимо отказаться от стандартного контроллера по загрузке вложения
class DmsDocument(models.Model):
    _name = 'dms.document'
    _description = 'DMS Document'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _order = 'id desc'

    attachment_id = fields.Many2one('ir.attachment', string='Attachment File', invisible=True, ondelete='cascade')
    attachment_name = fields.Char('Attachment Name', related='attachment_id.name', readonly=False)
    res_model = fields.Char(string='Resource Model', compute='_compute_res_record', inverse='_inverse_res_model',
                            store=True)
    res_id = fields.Integer(string='Resource ID', compute='_compute_res_record', inverse='_inverse_res_model',
                            store=True)
    datas = fields.Binary(related='attachment_id.datas', related_sudo=True, readonly=False)
    size = fields.Integer(related='attachment_id.file_size', store=True)
    checksum = fields.Char(related='attachment_id.checksum', store=True)
    mimetype = fields.Char(related='attachment_id.mimetype')
    index_content = fields.Text(related='attachment_id.index_content')
    description = fields.Text(related='attachment_id.description', string='Description', readonly=False)

    name = fields.Char(string='Name', compute='_compute_name', inverse='_inverse_name', copy=True, store=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    active = fields.Boolean(string='Archived', default=True,
                            help='If a document is set to archived, it is not displayed, but still exists.')

    directory_id = fields.Many2one('dms.directory', string='Directory', index='btree', ondelete='restrict',
                                   required=True)
    storage_id = fields.Many2one(related='directory_id.storage_id', prefetch=False, readonly=True, store=True)
    company_id = fields.Many2one(related='directory_id.company_id', string='Company', readonly=True)
    group_ids = fields.Many2many(related='directory_id.group_ids', string='Access Groups', readonly=True,
                                 help='This attachment will only be available for the selected user groups')
    is_hidden = fields.Boolean(related='storage_id.is_hidden', readonly=True, store=True)
    thumbnail = fields.Binary(compute='_compute_thumbnail', attachment=True, readonly=1, store=True)
    locker_id = fields.Many2one('res.users', string='Locked by')
    is_locked = fields.Boolean(compute='_compute_is_locked', string='Locked')

    @api.depends('attachment_id.name')
    def _compute_name(self):
        for record in self:
            if record.attachment_name:
                record.name = record.attachment_name

    def _inverse_name(self):
        for record in self:
            if record.attachment_id:
                record.attachment_name = record.name

    @api.depends('attachment_id', 'attachment_id.res_model', 'attachment_id.res_id')
    def _compute_res_record(self):
        for record in self:
            attachment = record.attachment_id
            if attachment:
                record.res_model = attachment.res_model
                record.res_id = attachment.res_id

    def _inverse_res_model(self):
        for record in self:
            attachment = record.attachment_id.with_context(without_document=True)
            if attachment:
                attachment.res_id = False
                attachment.res_model = record.res_model
                attachment.res_id = record.res_id

    @api.depends('checksum')
    def _compute_thumbnail(self):
        for record in self:
            try:
                record.thumbnail = image_process(record.datas, size=(80, 80), crop='center')
            except UserError:
                record.thumbnail = False

    def _compute_is_locked(self):
        for record in self:
            record.is_locked = record.locker_id and not (
                    self.env.user == record.locker_id or self.env.is_admin() or self.user_has_groups(
                        'dms.group_document_manager'))

    @api.model_create_multi
    def create(self, vals_list):
        records = super(DmsDocument, self).create(vals_list)

        for record in records:
            if record.attachment_id and not record.attachment_id.res_id and (
                    not record.attachment_id.res_model or record.attachment_id.res_model == self._name):
                record.attachment_id.with_context(without_document=True).write(
                    {'res_model': self._name, 'res_id': record.id})
        return records

    #TODO: не уверен, что при удалении документа нужно удалять и вложение
    def unlink(self):
        attachments = self.mapped('attachment_id')
        res = attachments.unlink()
        return res

    def get_dms_documents_from_attachments(self, attachment_ids=None):
        if not attachment_ids:
            raise UserError(_('No attachment was provided'))

        attachments = self.env['ir.attachment'].browse(attachment_ids)

        # if any(attachment.res_id or attachment.res_model != 'dms.document' for attachment in attachments):
        #     raise UserError(_('Invalid attachments!'))

        return [self.get_attachment_object(attachment) for attachment in attachments]

    @api.model
    def _get_search_domain(self, **kwargs):
        result = []
        search_domain = kwargs.get('search_domain', [])
        res_model = False
        res_id = False
        if search_domain and len(search_domain):
            for domain in search_domain:
                if domain[0] == 'res_model':
                    res_model = domain[2]
                elif domain[0] == 'res_id':
                    res_id = domain[2]
        if res_model and res_id:
            rec = self.env[res_model].search([
                ('id', '=', res_id)
            ])
            if rec and rec.directory_id:
                result = ['|', ['id', 'child_of', rec.directory_id.id], ['id', 'parent_of', rec.directory_id.id]]
        return result

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        if field_name == 'directory_id':
            search_domain = self._get_search_domain(**kwargs)
            comodel_records = self.env['dms.directory'].with_context(hierarchical_naming=False).search_read(
                search_domain, ['name', 'parent_id'])
            all_record_ids = [rec['id'] for rec in comodel_records]
            field_range = {}
            enable_counters = kwargs.get('enable_counters')
            for record in comodel_records:
                record_id = record['id']
                parent = record['parent_id']
                record_values = {
                    'id': record_id,
                    'display_name': record['name'],
                    'parent_id': parent[0] if parent and parent[0] in all_record_ids else False
                }
                if enable_counters:
                    record_values['__count'] = 0
                field_range[record_id] = record_values
            if enable_counters:
                res = super().search_panel_select_range(field_name, **kwargs)
                for item in res['values']:
                    field_range[item['id']]['__count'] = item['__count']
            return {
                'parent_field': 'parent_id',
                'values': list(field_range.values())
            }
        return super(DmsDocument, self).search_panel_select_range(field_name, **kwargs)

    def open_resource(self):
        self.ensure_one()
        if self.res_model and self.res_id:
            view_id = self.env[self.res_model].get_formview_id(self.res_id)
            return {
                'type': 'ir.actions.act_window',
                'res_id': self.res_id,
                'res_model': self.res_model,
                'views': [[view_id, 'form']],
                'target': 'current'
            }

    def get_attachment_object(self, attachment):
        return {
            'attachment_id': attachment.id
            # 'name': attachment.name,
            # 'datas': attachment.datas,
            # 'res_model': attachment.res_model
        }
