from odoo import fields, models


class DocumentFlowProcessingWizardResume(models.TransientModel):
    _name = 'document_flow.processing.wizard.resume'
    _description = 'Document Flow Processing Wizard: Resume'

    process_id = fields.Many2one('document_flow.process', string='Process', required=True, ondelete='cascade')
    comment = fields.Html(string='Comment')

    def action_resume_processing(self):
        self.ensure_one()

        if self.process_id:
            self.process_id.resume_from_last_stage(description=self.comment)

        return None
