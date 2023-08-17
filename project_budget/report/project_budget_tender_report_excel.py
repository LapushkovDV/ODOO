from odoo import models
from xlsxwriter.utility import xl_col_to_name
# from HTMLParser import HTMLParser
# class MLStripper(HTMLParser):
#     def __init__(self):
#         self.reset()
#         self.fed = []
#     def handle_data(self, d):
#         self.fed.append(d)
#     def get_data(self):
#         return ''.join(self.fed)
#
# def strip_tags(html):
#     s = MLStripper()
#     s.feed(html)
#     return s.get_data()

class report_tender_excel(models.AbstractModel):
    _name = 'report.project_budget.report_tender_excel'
    _description = 'project_budget.report_tender_excel'
    _inherit = 'report.report_xlsx.abstract'

    strYEAR = '2023'
    YEARint = int(strYEAR)

    probabitily_list_KB = ['30','50','75']
    probabitily_list_PB = ['100','100(done)']
    probabitily_list_Otmena = ['0']
    array_col_itogi = [12, 13,14,15,16,17,18,19,20,21,22,23,24,252,6,27,28]

    def printworksheet(self,workbook, tenders):
        report_name = 'tenders'
            # One sheet by partner
        sheet = workbook.add_worksheet('tenders')
        bold = workbook.add_format({'bold': True})
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        head_format = workbook.add_format({
            'bold': True,
            'italic': True,
            'border': 1,
            'font_name': 'Arial',
            'font_size': 11,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#3265a5',
            'color': '#ffffff'
        })

        row_format_date_month = workbook.add_format({
            'border': 1,
            'font_size': 11,
            'font_name': 'Times New Roman'
            # 'num_format': 14
            #                'text_wrap' : True,
            #                'align': 'center',
            #                'valign': 'vcenter',
            #                'fg_color': '#3265a5',
        })

        row_format_date_month.set_num_format('mmmm yyyy')
        row_format = workbook.add_format({
            'border': 1,
            'font_size': 11,
            'font_name': 'Times New Roman'
            #                'text_wrap' : True,
            #                'align': 'center',
            #                'valign': 'vcenter',
            #                'fg_color': '#3265a5',
        })
        row_format_number = workbook.add_format({
            'border': 1,
            'font_size': 11,
            'num_format': '#,##0.00',
            'font_name': 'Times New Roman'
        })
        row_format_manager = workbook.add_format({
            'border': 1,
            'font_size': 11,
            "bold": True,
            "fg_color": '#D9D9D9',
            'font_name': 'Times New Roman'
        })
        row_format_manager.set_num_format('#,##0')

        row_format_itogo = workbook.add_format({
            'border': 1,
            'font_size': 11,
            "bold": True,
            "fg_color": '#bfbfbf',
            'font_name': 'Times New Roman'
        })
        row_format_itogo.set_num_format('#,##0.00')

        row_format_itogo_percent = workbook.add_format({
            'border': 1,
            'font_size': 11,
            "bold": True,
            "fg_color": '#bfbfbf',
            'font_name': 'Times New Roman'
        })
        row_format_itogo_percent.set_num_format('0%')


        row_format_office = workbook.add_format({
            'border': 1,
            'font_size': 11,
            "bold": True,
            "fg_color": '#60497a',
            "color": '#ffffff',
            'font_name': 'Times New Roman'
        })
        row_format_office.set_num_format('#,##0.00')


        row_format_office_percent = workbook.add_format({
            'border': 1,
            'font_size': 11,
            "bold": True,
            "fg_color": '#60497a',
            "color": '#ffffff',
            'font_name': 'Times New Roman'
        })
        row_format_office_percent.set_num_format('0%')

        row_format_itog_row = workbook.add_format({
            'border': 1,
            'font_size': 11,
            "bold": True,
            "color": '#244062',
            'font_name': 'Times New Roman'
        })
        row_format_itog_row.set_num_format('#,##0.00')

        row_format_percent_row = workbook.add_format({
            'border': 1,
            'font_size': 11,
            "bold": True,
            "color": '#244062',
            'font_name': 'Times New Roman'
        })
        row_format_percent_row.set_num_format('0%')


        date_format = workbook.add_format({'num_format': 'd mmmm yyyy'})
        row = 0
        column = 0
        sheet.write_string(row, column, 'Дата заполнения')
        column += 1
        sheet.write_string(row, column, 'Участник')
        column += 1
        sheet.write_string(row, column, '№ торгов')
        column += 1
        sheet.write_string(row, column, 'Ссылка')
        column += 1
        sheet.write_string(row, column, 'Заказчик')
        column += 1
        sheet.write_string(row, column, 'Контактная информация')
        column += 1
        sheet.write_string(row, column, 'Наименование закупки')
        column += 1
        sheet.write_string(row, column, 'НМЦК')
        column += 1
        sheet.write_string(row, column, 'Предложение Участника')
        column += 1
        sheet.write_string(row, column, 'Обеспечение заявки')
        column += 1
        sheet.write_string(row, column, 'Обеспечение контракта')
        column += 1
        sheet.write_string(row, column, 'Обеспечение ГО')
        column += 1
        sheet.write_string(row, column, 'Лицензии / СРО')
        column += 1
        sheet.write_string(row, column, 'РП')
        column += 1
        sheet.write_string(row, column, 'Текущий статус')
        column += 1
        sheet.write_string(row, column, 'Комментарии')
        column += 1
        sheet.write_string(row, column, 'Номер пресейла ОЗ')
        column += 1

        for tender in tenders:
            row += 1
            column = 0
            sheet.write_string(row, column, str(tender.date_of_filling_in))
            column += 1
            sheet.write_string(row, column,(tender.participant_id.name or '' ))
            column += 1
            sheet.write_string(row, column, (tender.auction_number or '' ))
            column += 1
            sheet.write_string(row, column,(tender.url_tender.striptags() or '' ))
            column += 1
            sheet.write_string(row, column, (tender.customer_organization_id.name or '' ))
            column += 1
            sheet.write_string(row, column, (tender.contact_information or '' ))
            column += 1
            sheet.write_string(row, column, (tender.name_of_the_purchase or '' ))
            column += 1
            sum_participants_offer = ''
            sum_initial_maximum_contract_price = ''
            sum_payment_for_the_victory = ''
            sum_securing_the_application = ''
            sum_contract_security = ''
            sum_provision_of_GO = ''
            sum_site_payment = ''
            for tendersum in tender.tender_sums_ids:
                sum_participants_offer += '\n' + tendersum.currency_id.symbol + ' ' +str(tendersum.participants_offer) + (tendersum.participants_offer_descr or '')
                sum_initial_maximum_contract_price +=  '\n' + tendersum.currency_id.symbol + ' ' + str(
                                                    tendersum.initial_maximum_contract_price) + (tendersum.initial_maximum_contract_price_descr or '')
                sum_payment_for_the_victory +=  '\n' + tendersum.currency_id.symbol + ' ' + str(
                                                tendersum.payment_for_the_victory) + (tendersum.payment_for_the_victory_descr or '')
                sum_securing_the_application +=  '\n' + tendersum.currency_id.symbol + ' ' + str(
                                                tendersum.securing_the_application) +  (tendersum.securing_the_application_descr or '')
                sum_contract_security +=  '\n' + tendersum.currency_id.symbol + ' ' + str(
                                                tendersum.contract_security) +  (tendersum.contract_security_descr or '')
                sum_provision_of_GO +=  '\n' + tendersum.currency_id.symbol + ' ' + str(
                                                tendersum.provision_of_GO) +  (tendersum.provision_of_GO_descr or '')
                sum_site_payment +=  '\n' + tendersum.currency_id.symbol + ' ' + str(
                                                tendersum.site_payment) +  (tendersum.site_payment_descr or '')

            if tender.is_need_initial_maximum_contract_price == True:
                sheet.write_string(row, column,sum_initial_maximum_contract_price)
            else : sheet.write_string(row, column,'НЕТ')
            column += 1
            sheet.write_string(row, column, sum_participants_offer)
            column += 1
            if tender.is_need_securing_the_application == True:
                sheet.write_string(row, column,sum_securing_the_application)
            else : sheet.write_string(row, column,'НЕТ')
            column += 1
            if tender.is_need_contract_security == True:
                sheet.write_string(row, column,sum_contract_security)
            else : sheet.write_string(row, column,'НЕТ')
            column += 1
            if tender.is_need_provision_of_GO == True:
                sheet.write_string(row, column, sum_provision_of_GO)
            else : sheet.write_string(row, column,'НЕТ')
            column += 1
            if tender.is_need_licenses_SRO == True:
                sheet.write_string(row, column, (tender.licenses_SRO or ''))
            else : sheet.write_string(row, column,'НЕТ')
            column += 1
            str_responsible = ''
            for responsible in tender.responsible_ids:
                print('responsible = ', responsible.name)
                str_responsible = str_responsible + '\n'+(responsible.name or '')
            print('str_responsible = ',str_responsible)
            sheet.write_string(row, column, str_responsible)
            column += 1
            sheet.write_string(row, column, (tender.current_status.name or ''))
            column += 1
            str_comment = ''
            for comment in tender.tender_comments_ids:
                str_comment  = str_comment + '\n' + str(comment.date_comment) + ' ' + (comment.type_comment_id.name or '') + ' ' + (comment.text_comment or '')
            sheet.write_string(row, column, str_comment)
            column += 1
            sheet.write_string(row, column, (tender.presale_number or ''))



    def generate_xlsx_report(self, workbook, data, tenders):
        self.printworksheet(workbook, tenders)
