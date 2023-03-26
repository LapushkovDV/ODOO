from odoo import models
import datetime
import xlsxwriter

class report_budget_forecast_excel(models.AbstractModel):
    _name = 'report.project_budget.report_budget_forecast_excel'
    _description = 'project_budget.report_budget_forecast_excel'
    _inherit = 'report.report_xlsx.abstract'

    month_rus_name_contract_pds = ['Январь','Февраль','Март','Q1 итого','Апрель','Май','Июнь','Q2 итого','HY1/YEAR итого',
                                    'Июль','Август','Сентябрь','Q3 итого','Октябрь','Ноябрь','Декабрь','Q4 итого',
                                   'HY2/YEAR итого','YEAR итого']
    month_rus_name_revenue_margin = ['Q1','Q2','HY1/YEAR','Q3','Q4','HY2/YEAR','YEAR']

    dict_contract_pds = {
        1: {'name': 'Контрактование, с НДС', 'color': '#FFD966'},
        2: {'name': 'Поступление денежных средсв, с НДС', 'color': '#D096BF'}
    }

    dict_revenue_margin= {
        1: {'name': 'Валовая Выручка, без НДС', 'color': '#B4C6E7'},
        2: {'name': 'Валовая прибыль (Маржа 1), без НДС', 'color': '#F4FD9F'}
    }
    def print_month_head_contract_pds(self,workbook,sheet,row,column,YEAR):
        for x in self.dict_contract_pds.items():
            y = list(x[1].values())
            print(y[0])
            head_format_month = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                "bold" : True,
                "fg_color" : y[1],
                "font_size" : 11,
            })
            head_format_month_itogo = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                "bold": True,
                "fg_color": '#D9E1F2',
                "font_size": 12,
            })
            head_format_month_detail = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                "bold": False,
                "fg_color": '#E2EFDA',
                "font_size": 8,
            })
            head_format_month_detail_fact = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                "bold": True,
                "fg_color": '#C6E0B4',
                "font_size": 8,
            })

            colbeg = column
            colbegQ= column
            colbegH= column
            colbegY= column




            for elementone in self.month_rus_name_contract_pds:

                element = elementone.replace('YEAR',YEAR)
                if element.find('итого') != -1:
                    if elementone.find('Q') != -1:
                        sheet.set_column(column, column + 5, None, None, {'hidden': 1, 'level': 2})
                    if elementone.find('HY') != -1:
                        sheet.set_column(column, column + 5, None, None, {'hidden': 1, 'level': 1})
                    sheet.merge_range(row, column, row, column + 5, element, head_format_month)
                    sheet.merge_range(row + 1, column, row + 2, column, "План "+element.replace('итого',''), head_format_month_itogo)
                    column += 1
                else:
                    sheet.merge_range(row, column, row, column + 4, element, head_format_month)
                    sheet.set_column(column, column+4, None, None, {'hidden': 1, 'level': 3})
                sheet.merge_range(row+1, column, row+1, column + 1, 'Прогноз на начало периода (эталонный)', head_format_month_detail)
                sheet.write_string(row+2, column, 'Обязательство', head_format_month_detail)
                column += 1
                sheet.write_string(row + 2, column, 'Резерв', head_format_month_detail)
                column += 1
                sheet.merge_range(row+1, column, row+2, column, 'Факт', head_format_month_detail_fact)
                column += 1
                sheet.merge_range(row + 1, column, row + 1, column + 1, 'Прогноз до конца периода (на дату отчета)',head_format_month_detail)
                sheet.write_string(row + 2, column, 'Обязательство', head_format_month_detail)
                column += 1
                sheet.write_string(row + 2, column, 'Резерв', head_format_month_detail)
                column += 1
                if elementone.find('Q') != -1 or elementone.find('НY') != -1 or elementone.find('YEAR') != -1:
                    print('colbegQ = column = ',column)
                    colbegQ = column

                if elementone.find('НY') != -1 or elementone.find('YEAR') != -1:
                    print('colbegH = column = ',column)
                    colbegH = column

            # sheet.set_column(1, None, None, {'level': 1})
            print('colbeg=',colbeg,' column=',column)
            # sheet.set_column(colbeg, column - 1, 15)
            # sheet.set_column(colbeg, column - 1, 15)
            sheet.merge_range(row-1, colbeg, row-1, column - 1, y[0], head_format_month)

        return column

    def print_month_head_revenue_margin(self,workbook,sheet,row,column,YEAR):
        for x in self.dict_revenue_margin.items():
            y = list(x[1].values())
            print(y[0])
            head_format_month = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                "bold" : True,
                "fg_color" : y[1],
                "font_size" : 11,
            })
            head_format_month_itogo = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                "bold": True,
                "fg_color": '#D9E1F2',
                "font_size": 12,
            })
            head_format_month_detail = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                "bold": False,
                "fg_color": '#E2EFDA',
                "font_size": 8,
            })
            head_format_month_detail_fact = workbook.add_format({
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                "bold": True,
                "fg_color": '#C6E0B4',
                "font_size": 8,
            })

            colbeg = column
            for elementone in self.month_rus_name_revenue_margin:
                element = elementone.replace('YEAR', YEAR)
                if elementone.find('Q') != -1:
                    sheet.set_column(column, column + 5, None, None, {'hidden': 1, 'level': 2})
                if elementone.find('HY') != -1:
                    sheet.set_column(column, column + 5, None, None, {'hidden': 1, 'level': 1})

                sheet.merge_range(row, column, row, column + 5, element, head_format_month)
                sheet.merge_range(row + 1, column, row + 2, column, "План " + element.replace('итого', ''),
                                  head_format_month_itogo)
                # sheet.set_column(column, column, 15)
                column += 1
                sheet.merge_range(row + 1, column, row + 1, column + 1, 'Прогноз на начало периода (эталонный)',
                                  head_format_month_detail)
                sheet.write_string(row + 2, column, 'Обязательство', head_format_month_detail)
                # sheet.set_column(column, column, 15)
                column += 1
                sheet.write_string(row + 2, column, 'Резерв', head_format_month_detail)
                # sheet.set_column(column, column, 15)
                column += 1
                sheet.merge_range(row + 1, column, row + 2, column, 'Факт', head_format_month_detail_fact)
                # sheet.set_column(column, column, 15)
                column += 1
                sheet.merge_range(row + 1, column, row + 1, column + 1, 'Прогноз до конца периода (на дату отчета)',
                                  head_format_month_detail)
                sheet.write_string(row + 2, column, 'Обязательство', head_format_month_detail)
                # sheet.set_column(column, column, 15)
                column += 1
                sheet.write_string(row + 2, column, 'Резерв', head_format_month_detail)
                # sheet.set_column(column, column, 15)
                column += 1
            sheet.merge_range(row-1, colbeg, row-1, column - 1, y[0], head_format_month)
        return column

    def printworksheet(self,workbook,budget,namesheet):
        report_name = budget.name
            # One sheet by partner
        sheet = workbook.add_worksheet(namesheet)
        bold = workbook.add_format({'bold': True})
        money_format = workbook.add_format({'num_format': '#,##0'})
        head_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'font_size': 11,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#FFFF00'
        })
        head_format_1 = workbook.add_format({
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            "bold": False,
            "fg_color": '#C6E0B4',
            "font_size": 8,
        })
        row_format_date_month = workbook.add_format({
            'border': 1,
            'font_size': 10,
            # 'num_format': 14
            #                'text_wrap' : True,
            #                'align': 'center',
            #                'valign': 'vcenter',
            #                'fg_color': '#3265a5',
        })

        row_format_date_month.set_num_format('mmm yyyy')
        row_format = workbook.add_format({
            'border': 1,
            'font_size': 10
            #                'text_wrap' : True,
            #                'align': 'center',
            #                'valign': 'vcenter',
            #                'fg_color': '#3265a5',
        })
        row_format_number = workbook.add_format({
            'border': 1,
            'font_size': 10,
            'num_format': '# ##0,00'
        })

        date_format = workbook.add_format({'num_format': 'd mmmm yyyy'})
        row = 0
        sheet.merge_range(row,0,row,10, budget.name, bold)
        row = 6
        column = 0
        sheet.write_string(row, column, "Прогноз",head_format)
        sheet.write_string(row+1, column, "Проектный офис", head_format_1)
        # sheet.set_column(column, column, 21.5)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "КАМ", head_format_1)
        # sheet.set_column(column, column, 19.75)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Заказчик", head_format_1)
        # sheet.set_column(column, column, 25)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Наименование Проекта", head_format_1)
        # sheet.set_column(column, column, 12.25)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Номер этапа проекта", head_format_1)
        # sheet.set_column(column, column, 15)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Стадияпродажи", head_format_1)
        # sheet.set_column(column, column, 16.88)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Суммапроекта, вруб", head_format_1)
        # sheet.set_column(column, column, 14)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Валовая прибыльэкспертно, в руб", head_format_1)
        # sheet.set_column(column, column, 14)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Прибыльность, экспертно, %", head_format_1)
        # sheet.set_column(column, column, 9)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Номердоговора", head_format_1)
        # sheet.set_column(column, column, 11.88)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "НДС", head_format_1)
        # sheet.set_column(column, column, 7)
        column += 1
        column = self.print_month_head_contract_pds(workbook, sheet, row, column,  '2023')
        column = self.print_month_head_revenue_margin(workbook, sheet, row, column,  '2023')
        print(column)
        sheet.set_zoom(85)
        # for spec in budget.projects_ids:
        #     if spec.specification_state == stateproject:
        #         row += 1
        #         column = 0
        #         sheet.write_string(row, column, spec.project_id, row_format)


    def generate_xlsx_report(self, workbook, data, budgets):
        for budget in budgets:
            self.printworksheet(workbook, budget, 'Прогноз')
