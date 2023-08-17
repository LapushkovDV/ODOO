from odoo import models, fields, _
from odoo.exceptions import UserError
from io import BytesIO

import xlsxwriter

class report_tender_wizard(models.TransientModel):
    _name = 'project_budget.tender.report.wizard'
    _description = 'Tender report Wizard'
    _inherit = 'report.report_xlsx.abstract'

    date_from = fields.Date(string='event date from', required=True)
    date_to   = fields.Date(string='event  date to', required=True)

    def action_print_report(self):
        self.ensure_one()

        tenders_list = self.env['project_budget.tenders'].search([('date_of_filling_in', '>=', self.date_from),('date_of_filling_in', '<=', self.date_to)], order='date_of_filling_in desc')

        if not tenders_list:
            raise UserError(_("Tenders with thet term not found!"))
        report = self.env['report.project_budget.report_tender_excel']
        # file_data = BytesIO()
        # rep_options = {"report_type":"xlsx","report_name":"project_budget_report_tender_excel","report_file":"project_budget_report_tender_excel"}
        # workbook = xlsxwriter.Workbook(file_data,rep_options)
        # print('workbook = ',workbook)

        workbook = xlsxwriter.Workbook('filename.xlsx')
        worksheet = workbook.add_worksheet()

        worksheet.write(0, 0, 'Hello Excel')

        workbook.close()

        report.generate_xlsx_report(workbook, {}, tenders_list)

        return None

