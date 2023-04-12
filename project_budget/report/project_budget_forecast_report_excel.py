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

    def get_months_from_quater(self,quater_name):
        months = False;
        if quater_name == 'Q1':
            months=(1,2,3)
        if quater_name == 'Q2':
            months=(4,5,6)
        if quater_name == 'Q3':
            months=(7,8,9)
        if quater_name == 'Q4':
            months=(10,11,12)
        return months

    def get_etalon_project(self,spec):
        etalon_project = self.env['project_budget.projects'].search([('etalon_budget', '=', True),('budget_state','=','fixed'),('project_id','=',spec.project_id)], limit=1, order='date_actual desc')
        # print('etalon_project.project_id = ',etalon_project.project_id)
        # print('etalon_project.date_actual = ',etalon_project.date_actual)
        return etalon_project

    def get_etalon_step(self,step):
        if step == None:
            return None
        etalon_step = self.env['project_budget.project_steps'].search([('etalon_budget', '=', True),('step_id','=',step.step_id),('id','!=',step.id)], limit=1, order='date_actual desc')
        # print('etalon_step.project_id = ', etalon_step.step_id)
        # print('etalon_step.date_actual = ', etalon_step.date_actual)
        return etalon_step

    def get_sum_fact_pds_project_step_month(self,project, step, YEARint, month):
        sum_cash = 0
        if month:
            if step:
                pds_list = self.env['project_budget.fact_cash_flow'].search([('project_steps_id', '=', step.id)])
            else:
                pds_list = self.env['project_budget.fact_cash_flow'].search([('projects_id', '=', project.id)])
            if pds_list:
                for pds in pds_list:
                    if pds.date_cash.month == month and pds.date_cash.year == YEARint:
                        sum_cash += pds.sum_cash
        return sum_cash

    def get_sum_plan_pds_project_step_month(self,project, step, YEARint, month):
        sum_cash = 0
        if month:
            if step:
                pds_list = self.env['project_budget.planned_cash_flow'].search([('project_steps_id', '=', step.id)])
            else:
                pds_list = self.env['project_budget.planned_cash_flow'].search([('projects_id', '=', project.id)])
            if pds_list:
                for pds in pds_list:
                    if pds.date_cash.month == month and pds.date_cash.year == YEARint:
                        sum_cash += pds.sum_cash
            # else: # если нихрена нет планового ПДС, то берем сумму общую по дате окончания sale или по дате этапа
            #     print('step = ',step)
            #     print('project = ',project)
            #     if step == None or step == False:
            #         if project:
            #             if project.end_sale_project_month.month == month and project.end_sale_project_month.year == YEARint:
            #                 sum_cash = project.total_amount_of_revenue_with_vat
            #     else:
            #         if step:
            #             if step.end_sale_project_month.month == month and step.end_sale_project_month.year == YEARint:
            #                 sum_cash = step.total_amount_of_revenue_with_vat
        return sum_cash

    def get_sum_plan_acceptance_step_month(self,project, step, month):
        sum_cash = 0
        if project.project_have_steps == False:
            acceptance_list = self.env['project_budget.planned_acceptance_flow'].search([('projects_id', '=', project.id)])
        if project.project_have_steps and step != None:
            acceptance_list = self.env['project_budget.planned_acceptance_flow'].search([('project_steps_id', '=', step.id)])
        for acceptance in acceptance_list:
            if acceptance.date_cash.month == month:
                sum_cash += acceptance.sum_cash
        return sum_cash



    def print_month_head_contract_pds(self,workbook,sheet,row,column,YEAR):
        for x in self.dict_contract_pds.items():
            y = list(x[1].values())
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
                    colbegQ = column

                if elementone.find('НY') != -1 or elementone.find('YEAR') != -1:
                    colbegH = column
            sheet.merge_range(row-1, colbeg, row-1, column - 1, y[0], head_format_month)

        return column

    def print_month_head_revenue_margin(self,workbook,sheet,row,column,YEAR):
        for x in self.dict_revenue_margin.items():
            y = list(x[1].values())
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
                column += 1
                sheet.merge_range(row + 1, column, row + 1, column + 1, 'Прогноз на начало периода (эталонный)',
                                  head_format_month_detail)
                sheet.write_string(row + 2, column, 'Обязательство', head_format_month_detail)
                column += 1
                sheet.write_string(row + 2, column, 'Резерв', head_format_month_detail)
                column += 1
                sheet.merge_range(row + 1, column, row + 2, column, 'Факт', head_format_month_detail_fact)
                column += 1
                sheet.merge_range(row + 1, column, row + 1, column + 1, 'Прогноз до конца периода (на дату отчета)',
                                  head_format_month_detail)
                sheet.write_string(row + 2, column, 'Обязательство', head_format_month_detail)
                column += 1
                sheet.write_string(row + 2, column, 'Резерв', head_format_month_detail)
                column += 1
            sheet.merge_range(row-1, colbeg, row-1, column - 1, y[0], head_format_month)
        return column

    def print_month_revenue_project(self, sheet, row, column, YEARint, month, project, step, row_format_number,row_format_number_color_fact):

        sum75tmpetalon = 0
        sum50tmpetalon = 0
        sum100tmp = 0
        sum75tmp = 0
        sum50tmp = 0
        if month:
            project_etalon = self.get_etalon_project(project)
            if step == None:
                if project_etalon:
                    if month == project_etalon.end_presale_project_month.month and YEARint == project_etalon.end_presale_project_month.year:
                        if project_etalon.estimated_probability_id.name == '75':
                            sheet.write_number(row, column + 0, project_etalon.total_amount_of_revenue_with_vat, row_format_number)
                            sum75tmpetalon += project_etalon.total_amount_of_revenue_with_vat
                        if project_etalon.estimated_probability_id.name == '50':
                            sheet.write_number(row, column + 1, project_etalon.total_amount_of_revenue_with_vat, row_format_number)
                            sum50tmpetalon += project_etalon.total_amount_of_revenue_with_vat

                if month == project.end_presale_project_month.month and YEARint == project.end_presale_project_month.year:
                    if project.estimated_probability_id.name == '100':
                        sheet.write_number(row, column + 2, project.total_amount_of_revenue_with_vat, row_format_number_color_fact)
                        sum100tmp += project.total_amount_of_revenue_with_vat
                    if project.estimated_probability_id.name == '75':
                        sheet.write_number(row, column + 3, project.total_amount_of_revenue_with_vat, row_format_number)
                        sum75tmp += project.total_amount_of_revenue_with_vat
                    if project.estimated_probability_id.name == '50':
                        sheet.write_number(row, column + 4, project.total_amount_of_revenue_with_vat, row_format_number)
                        sum50tmp += project.total_amount_of_revenue_with_vat
            else:
                step_etalon  = self.get_etalon_step(step)
                if step_etalon:
                    if month == step_etalon.end_presale_project_month.month and YEARint == step_etalon.end_presale_project_month.year:
                        if step_etalon.projects_id.estimated_probability_id.name == '75':
                            sheet.write_number(row, column + 0, step_etalon.total_amount_of_revenue_with_vat, row_format_number)
                            sum75tmpetalon = step_etalon.total_amount_of_revenue_with_vat
                        if step_etalon.projects_id.estimated_probability_id.name == '50':
                            sheet.write_number(row, column + 1, step_etalon.total_amount_of_revenue_with_vat, row_format_number)
                            sum50tmpetalon = step_etalon.total_amount_of_revenue_with_vat
                else:
                    if project_etalon: # если нет жталонного этапа, то данные берем из проекта, да это будет увеличивать сумму на количество этапов, но что делать я ХЗ
                        if month == project_etalon.end_presale_project_month.month and YEARint == project_etalon.end_presale_project_month.year:
                            if project_etalon.estimated_probability_id.name == '75':
                                sheet.write_number(row, column + 0, project_etalon.total_amount_of_revenue_with_vat,
                                                   row_format_number)
                                sum75tmpetalon += project_etalon.total_amount_of_revenue_with_vat
                            if project_etalon.estimated_probability_id.name == '50':
                                sheet.write_number(row, column + 1, project_etalon.total_amount_of_revenue_with_vat,
                                                   row_format_number)
                                sum50tmpetalon += project_etalon.total_amount_of_revenue_with_vat

                if month == step.end_presale_project_month.month and YEARint == step.end_presale_project_month.year:
                    if step.projects_id.estimated_probability_id.name == '100':
                        sheet.write_number(row, column + 2, step.total_amount_of_revenue_with_vat, row_format_number_color_fact)
                        sum100tmp = step.total_amount_of_revenue_with_vat
                    if step.projects_id.estimated_probability_id.name == '75':
                        sheet.write_number(row, column + 3, step.total_amount_of_revenue_with_vat, row_format_number)
                        sum75tmp = step.total_amount_of_revenue_with_vat
                    if step.projects_id.estimated_probability_id.name == '50':
                        sheet.write_number(row, column + 4, step.total_amount_of_revenue_with_vat, row_format_number)
                        sum50tmp = step.total_amount_of_revenue_with_vat

        return sum75tmpetalon, sum50tmpetalon, sum100tmp, sum75tmp, sum50tmp

    def print_month_pds_project(self, sheet, row, column, YEARint, month, project, step, row_format_number, row_format_number_color_fact):
        sum75tmpetalon = sum50tmpetalon = sum100tmp = sum75tmp = sum50tmp = 0
        if month:
                project_etalon = self.get_etalon_project(project)
                step_etalon = self.get_etalon_step(step)
                sum = self.get_sum_plan_pds_project_step_month(project_etalon, step_etalon, YEARint, month)
                if sum != 0:
                    if project_etalon.estimated_probability_id.name in('75','100'):
                        sheet.write_number(row, column + 0, sum,row_format_number)
                        sum75tmpetalon += sum
                    if project_etalon.estimated_probability_id.name == '50':
                        sheet.write_number(row, column + 1, sum, row_format_number)
                        sum50tmpetalon += sum

                sum100tmp = self.get_sum_fact_pds_project_step_month(project, step, YEARint, month)
                if sum100tmp:
                    sheet.write_number(row, column + 2, sum100tmp, row_format_number_color_fact)

                sum = self.get_sum_plan_pds_project_step_month(project, step, YEARint, month)
                print('----- project.id=',project.id)
                print('sum100tmp = ',sum100tmp)
                print('sum = ', sum)
                if sum100tmp >= sum:
                    sum = 0
                else:
                    sum = sum - sum100tmp
                print('after: sum = ', sum)

                if sum != 0:
                    if project.estimated_probability_id.name in('75','100'):
                        sheet.write_number(row, column + 3, sum,row_format_number)
                        sum75tmp += sum
                    if project.estimated_probability_id.name == '50':
                        sheet.write_number(row, column + 4, sum, row_format_number)
                        sum50tmp += sum
        return sum75tmpetalon, sum50tmpetalon, sum100tmp, sum75tmp, sum50tmp

    def get_sum_fact_acceptance_project_step_quater(self, project, step, YEARint, element_name):
        sum_cash = 0
        months = self.get_months_from_quater(element_name)
        if months:
            vatpercent = 0
            acceptance_list = None
            if step == None or step == False:
                acceptance_list = self.env['project_budget.fact_acceptance_flow'].search([('projects_id', '=', project.id)])
                vatpercent = project.vat_attribute_id.percent
            else:
                acceptance_list = self.env['project_budget.fact_acceptance_flow'].search([('project_steps_id', '=', step.id)])
                vatpercent = step.vat_attribute_id.percent
            if acceptance_list:
                for acceptance in acceptance_list:
                    if acceptance.date_cash.month in months and acceptance.date_cash.year == YEARint:
                        sum_cash += acceptance.sum_cash/(1+vatpercent/100)
        return sum_cash

    def get_sum_planned_acceptance_project_step_quater(self, project, step, YEARint, element_name):
        sum_acceptance = 0

        months = self.get_months_from_quater(element_name)

        if months:
            vatpercent = 0
            acceptance_list = None
            if step == None or step == False:
                acceptance_list = self.env['project_budget.planned_acceptance_flow'].search([('projects_id', '=', project.id)])
                vatpercent = project.vat_attribute_id.percent
            else:
                acceptance_list = self.env['project_budget.planned_acceptance_flow'].search([('project_steps_id', '=', step.id),('projects_id', '=', project.id)])
                vatpercent = step.vat_attribute_id.percent

            if acceptance_list:
                for acceptance in acceptance_list:
                    if acceptance.date_cash.month in months and acceptance.date_cash.year == YEARint:
                        sum_acceptance += acceptance.sum_cash_without_vat
                        # sum_acceptance += acceptance.sum_cash / (1 + vatpercent / 100)

        return sum_acceptance

    def print_quater_planned_acceptance_project(self, sheet, row, column, YEARint, element_name, project, step, row_format_number, row_format_number_color_fact):
        sum75tmpetalon = sum50tmpetalon = sum100tmp = sum75tmp = sum50tmp = 0
        if element_name in ('Q1','Q2','Q3','Q4'):
            project_etalon = self.get_etalon_project(project)
            step_etalon = self.get_etalon_step(step)

            if step == None or step == False:
                profitability = project.profitability
            else:
                profitability = step.profitability

            sum = 0
            sum = self.get_sum_planned_acceptance_project_step_quater(project_etalon, step_etalon, YEARint, element_name)

            if sum != 0:
                if project_etalon.estimated_probability_id.name in('75','100'):
                    sheet.write_number(row, column + 0, sum, row_format_number)
                    sheet.write_number(row, column + 0 + 42, sum*profitability/100, row_format_number)
                    sum75tmpetalon += sum
                if project_etalon.estimated_probability_id.name == '50':
                    sheet.write_number(row, column + 1, sum, row_format_number)
                    sheet.write_number(row, column + 1 + 42 , sum*profitability/100, row_format_number)
                    sum50tmpetalon += sum

            sum100tmp = self.get_sum_fact_acceptance_project_step_quater(project, step, YEARint, element_name)

            if sum100tmp:
                sheet.write_number(row, column + 2, sum100tmp, row_format_number_color_fact)
                sheet.write_number(row, column + 2 + 42, sum100tmp*profitability/100, row_format_number_color_fact)


            sum = 0
            sum = self.get_sum_planned_acceptance_project_step_quater(project, step, YEARint, element_name)
            if sum100tmp >= sum:
                sum = 0
            else:
                sum = sum - sum100tmp

            if sum != 0:
                if project.estimated_probability_id.name in('75','100'):
                    sheet.write_number(row, column + 3, sum, row_format_number)
                    sheet.write_number(row, column + 3 + 42, sum*profitability/100, row_format_number)
                    sum75tmp += sum
                if project.estimated_probability_id.name == '50':
                    sheet.write_number(row, column + 4, sum, row_format_number)
                    sheet.write_number(row, column + 4 + 42, sum*profitability/100, row_format_number)
                    sum50tmp += sum
        return sum75tmpetalon, sum50tmpetalon, sum100tmp, sum75tmp, sum50tmp


    def get_month_number_rus(self, monthNameRus):
        if monthNameRus == 'Январь': return 1
        if monthNameRus == 'Февраль': return 2
        if monthNameRus == 'Март' : return 3
        if monthNameRus == 'Апрель' : return 4
        if monthNameRus == 'Май' : return 5
        if monthNameRus == 'Июнь' : return 6
        if monthNameRus == 'Июль' : return 7
        if monthNameRus == 'Август' : return 8
        if monthNameRus == 'Сентябрь' : return 9
        if monthNameRus == 'Октябрь' : return 10
        if monthNameRus == 'Ноябрь' : return 11
        if monthNameRus == 'Декабрь' : return 12
        return False

    def print_row_Values(self, workbook, sheet, row, column,  YEAR, project, step):
        row_format_number = workbook.add_format({
            'border': 1,
            'font_size': 10,
        })
        row_format_number.set_num_format('#,##0.00')
        row_format_number_color_fact = workbook.add_format({
            "fg_color": '#C6E0B4',
            'border': 1,
            'font_size': 10,
        })
        row_format_number_color_fact.set_num_format('#,##0.00')
        head_format_month_itogo = workbook.add_format({
            'border': 1,
            "fg_color": '#D9E1F2',
            'diag_type': 3
        })

        YEARint = int(YEAR)

        sumQ100etalon =0
        sumQ75etalon = 0
        sumQ50etalon = 0
        sumQ100 =0
        sumQ75 = 0
        sumQ50 = 0
        sumHY100etalon =0
        sumHY75etalon = 0
        sumHY50etalon = 0
        sumHY100 =0
        sumHY75 = 0
        sumHY50 = 0
        sumYear100etalon =0
        sumYear75etalon = 0
        sumYear50etalon = 0
        sumYear100 =0
        sumYear75 = 0
        sumYear50 = 0
        # печать Контрактование, с НДС
        for element in self.month_rus_name_contract_pds:
            column += 1
            sumQ75tmpetalon = sumQ50tmpetalon = sumQ100tmp = sumQ75tmp = sumQ50tmp = 0

            if element.find('итого') != -1:
                sheet.write_string(row, column, "", head_format_month_itogo)
                column += 1
            sheet.write_string(row, column + 0, "", row_format_number)
            sheet.write_string(row, column + 1, "", row_format_number)
            sheet.write_string(row, column + 2, "", row_format_number_color_fact)
            sheet.write_string(row, column + 3, "", row_format_number)
            sheet.write_string(row, column + 4, "", row_format_number)

            sumQ75tmpetalon, sumQ50tmpetalon, sumQ100tmp, sumQ75tmp, sumQ50tmp = self.print_month_revenue_project(sheet, row, column, YEARint, self.get_month_number_rus(element),
                                                                                    project,step, row_format_number,row_format_number_color_fact)
            sumQ75etalon += sumQ75tmpetalon
            sumQ50etalon += sumQ50tmpetalon
            sumQ100 += sumQ100tmp
            sumQ75 += sumQ75tmp
            sumQ50 += sumQ50tmp
            if element.find('Q') != -1: #'Q1 итого' 'Q2 итого' 'Q3 итого' 'Q4 итого'
                if sumQ75etalon != 0 : sheet.write_number(row, column + 0, sumQ75etalon, row_format_number)
                if sumQ50etalon != 0 : sheet.write_number(row, column + 1, sumQ50etalon, row_format_number)
                if sumQ100 != 0 :      sheet.write_number(row, column + 2, sumQ100, row_format_number_color_fact)
                if sumQ75 != 0 :       sheet.write_number(row, column + 3, sumQ75, row_format_number)
                if sumQ50 != 0 :       sheet.write_number(row, column + 4, sumQ50, row_format_number)
                sumHY100etalon += sumQ100etalon
                sumHY75etalon += sumQ75etalon
                sumHY50etalon += sumQ50etalon
                sumHY100 += sumQ100
                sumHY75 += sumQ75
                sumHY50 += sumQ50
                sumQ100etalon = sumQ75etalon = sumQ50etalon = sumQ100 = sumQ75  = sumQ50  = 0

            if element.find('HY') != -1:  # 'HY1/YEAR итого' 'HY2/YEAR итого'
                if sumHY75etalon != 0: sheet.write_number(row, column + 0, sumHY75etalon, row_format_number)
                if sumHY50etalon != 0: sheet.write_number(row, column + 1, sumHY50etalon, row_format_number)
                if sumHY100 != 0:      sheet.write_number(row, column + 2, sumHY100, row_format_number_color_fact)
                if sumHY75 != 0:       sheet.write_number(row, column + 3, sumHY75, row_format_number)
                if sumHY50 != 0:       sheet.write_number(row, column + 4, sumHY50, row_format_number)
                sumYear100etalon += sumHY100etalon
                sumYear75etalon += sumHY75etalon
                sumYear50etalon += sumHY50etalon
                sumYear100 += sumHY100
                sumYear75 += sumHY75
                sumYear50 += sumHY50
                sumHY100etalon = sumHY75etalon = sumHY50etalon = sumHY100 = sumHY75 = sumHY50 = 0

            if element == 'YEAR итого':  # 'YEAR итого'
                if sumYear75etalon != 0: sheet.write_number(row, column + 0, sumYear75etalon, row_format_number)
                if sumYear50etalon != 0: sheet.write_number(row, column + 1, sumYear50etalon, row_format_number)
                if sumYear100 != 0:      sheet.write_number(row, column + 2, sumYear100, row_format_number_color_fact)
                if sumYear75 != 0:       sheet.write_number(row, column + 3, sumYear75, row_format_number)
                if sumYear50 != 0:       sheet.write_number(row, column + 4, sumYear50, row_format_number)
            column += 4
        #end печать Контрактование, с НДС
        # Поступление денежных средсв, с НДС
        sumYear100etalon = sumYear75etalon = sumYear50etalon = sumYear100 = sumYear75 = sumYear50 = 0
        sumQ100etalon = sumQ75etalon = sumQ50etalon = sumQ100 = sumQ75 = sumQ50 = 0
        sumHY100etalon = sumHY75etalon = sumHY50etalon = sumHY100 = sumHY75 = sumHY50 = 0

        for element in self.month_rus_name_contract_pds:
            column += 1
            sumQ75tmpetalon = sumQ50tmpetalon = sumQ100tmp = sumQ75tmp = sumQ50tmp = 0

            if element.find('итого') != -1:
                sheet.write_string(row, column, "", head_format_month_itogo)
                column += 1
            sheet.write_string(row, column + 0, "", row_format_number)
            sheet.write_string(row, column + 1, "", row_format_number)
            sheet.write_string(row, column + 2, "", row_format_number_color_fact)
            sheet.write_string(row, column + 3, "", row_format_number)
            sheet.write_string(row, column + 4, "", row_format_number)


            sumQ75tmpetalon, sumQ50tmpetalon, sumQ100tmp, sumQ75tmp, sumQ50tmp = self.print_month_pds_project(sheet, row, column, YEARint, self.get_month_number_rus(element)
                                                                                        ,project, step, row_format_number, row_format_number_color_fact)

            sumQ75etalon += sumQ75tmpetalon
            sumQ50etalon += sumQ50tmpetalon
            sumQ100 += sumQ100tmp
            sumQ75 += sumQ75tmp
            sumQ50 += sumQ50tmp

            if element.find('Q') != -1:  # 'Q1 итого' 'Q2 итого' 'Q3 итого' 'Q4 итого'
                if sumQ75etalon != 0: sheet.write_number(row, column + 0, sumQ75etalon, row_format_number)
                if sumQ50etalon != 0: sheet.write_number(row, column + 1, sumQ50etalon, row_format_number)
                if sumQ100 != 0:      sheet.write_number(row, column + 2, sumQ100, row_format_number_color_fact)
                if sumQ75 != 0:       sheet.write_number(row, column + 3, sumQ75, row_format_number)
                if sumQ50 != 0:       sheet.write_number(row, column + 4, sumQ50, row_format_number)
                sumHY100etalon += sumQ100etalon
                sumHY75etalon += sumQ75etalon
                sumHY50etalon += sumQ50etalon
                sumHY100 += sumQ100
                sumHY75 += sumQ75
                sumHY50 += sumQ50
                sumQ100etalon = sumQ75etalon = sumQ50etalon = sumQ100 = sumQ75 = sumQ50 = 0

            if element.find('HY') != -1:  # 'HY1/YEAR итого' 'HY2/YEAR итого'
                if sumHY75etalon != 0: sheet.write_number(row, column + 0, sumHY75etalon, row_format_number)
                if sumHY50etalon != 0: sheet.write_number(row, column + 1, sumHY50etalon, row_format_number)
                if sumHY100 != 0:      sheet.write_number(row, column + 2, sumHY100, row_format_number_color_fact)
                if sumHY75 != 0:       sheet.write_number(row, column + 3, sumHY75, row_format_number)
                if sumHY50 != 0:       sheet.write_number(row, column + 4, sumHY50, row_format_number)
                sumYear100etalon += sumHY100etalon
                sumYear75etalon += sumHY75etalon
                sumYear50etalon += sumHY50etalon
                sumYear100 += sumHY100
                sumYear75 += sumHY75
                sumYear50 += sumHY50
                sumHY100etalon = sumHY75etalon = sumHY50etalon = sumHY100 = sumHY75 = sumHY50 = 0

            if element == 'YEAR итого':  # 'YEAR итого'
                if sumYear75etalon != 0: sheet.write_number(row, column + 0, sumYear75etalon, row_format_number)
                if sumYear50etalon != 0: sheet.write_number(row, column + 1, sumYear50etalon, row_format_number)
                if sumYear100 != 0:      sheet.write_number(row, column + 2, sumYear100, row_format_number_color_fact)
                if sumYear75 != 0:       sheet.write_number(row, column + 3, sumYear75, row_format_number)
                if sumYear50 != 0:       sheet.write_number(row, column + 4, sumYear50, row_format_number)
            column += 4
        # end Поступление денежных средсв, с НДС

        # Валовая Выручка, без НДС
        sumYear100etalon = sumYear75etalon = sumYear50etalon = sumYear100 = sumYear75 = sumYear50 = 0
        sumHY100etalon = sumHY75etalon = sumHY50etalon = sumHY100 = sumHY75 = sumHY50 = 0

        if step == None or step == False:
            profitability = project.profitability
        else:
            profitability = step.profitability

        for element in self.month_rus_name_revenue_margin:
            column += 1
            sheet.write_string(row, column, "", head_format_month_itogo)
            sheet.write_string(row, column + 42, "", head_format_month_itogo)
            column += 1
            sheet.write_string(row, column + 0, "", row_format_number)
            sheet.write_string(row, column + 1, "", row_format_number)
            sheet.write_string(row, column + 2, "", row_format_number_color_fact)
            sheet.write_string(row, column + 3, "", row_format_number)
            sheet.write_string(row, column + 4, "", row_format_number)
            sheet.write_string(row, column + 0 + 42, "", row_format_number)
            sheet.write_string(row, column + 1 + 42, "", row_format_number)
            sheet.write_string(row, column + 2 + 42, "", row_format_number_color_fact)
            sheet.write_string(row, column + 3 + 42, "", row_format_number)
            sheet.write_string(row, column + 4 + 42, "", row_format_number)

            sumQ75etalon, sumQ50etalon, sumQ100, sumQ75, sumQ50 = self.print_quater_planned_acceptance_project(sheet,row,column,YEARint,element
                                                                                                              ,project,step,row_format_number,row_format_number_color_fact)

            sumHY100etalon += sumQ100etalon
            sumHY75etalon += sumQ75etalon
            sumHY50etalon += sumQ50etalon
            sumHY100 += sumQ100
            sumHY75 += sumQ75
            sumHY50 += sumQ50

            if element.find('HY') != -1:  # 'HY1/YEAR итого' 'HY2/YEAR итого'
                if sumHY75etalon != 0:
                    sheet.write_number(row, column + 0, sumHY75etalon, row_format_number)
                    sheet.write_number(row, column + 0 + 42, sumHY75etalon*profitability / 100, row_format_number)
                if sumHY50etalon != 0:
                    sheet.write_number(row, column + 1, sumHY50etalon, row_format_number)
                    sheet.write_number(row, column + 1 + 42, sumHY50etalon*profitability / 100, row_format_number)
                if sumHY100 != 0:
                    sheet.write_number(row, column + 2, sumHY100, row_format_number_color_fact)
                    sheet.write_number(row, column + 2 + 42, sumHY100*profitability / 100, row_format_number_color_fact)
                if sumHY75 != 0:
                    sheet.write_number(row, column + 3, sumHY75, row_format_number)
                    sheet.write_number(row, column + 3 + 42, sumHY75*profitability / 100, row_format_number)
                if sumHY50 != 0:
                    sheet.write_number(row, column + 4, sumHY50, row_format_number)
                    sheet.write_number(row, column + 4 + 42, sumHY50*profitability / 100, row_format_number)
                sumYear100etalon += sumHY100etalon
                sumYear75etalon += sumHY75etalon
                sumYear50etalon += sumHY50etalon
                sumYear100 += sumHY100
                sumYear75 += sumHY75
                sumYear50 += sumHY50
                sumHY100etalon = sumHY75etalon = sumHY50etalon = sumHY100 = sumHY75 = sumHY50 = 0

            if element == 'YEAR':  # 'YEAR итого'
                if sumYear75etalon != 0:
                    sheet.write_number(row, column + 0, sumYear75etalon, row_format_number)
                    sheet.write_number(row, column + 0 + 42, sumYear75etalon*profitability / 100, row_format_number)
                if sumYear50etalon != 0:
                    sheet.write_number(row, column + 1, sumYear50etalon, row_format_number)
                    sheet.write_number(row, column + 1 + 42, sumYear50etalon*profitability / 100, row_format_number)
                if sumYear100 != 0:
                    sheet.write_number(row, column + 2, sumYear100, row_format_number_color_fact)
                    sheet.write_number(row, column + 2 + 42, sumYear100*profitability / 100, row_format_number_color_fact)
                if sumYear75 != 0:
                    sheet.write_number(row, column + 3, sumYear75, row_format_number)
                    sheet.write_number(row, column + 3 + 42, sumYear75*profitability / 100, row_format_number)
                if sumYear50 != 0:
                    sheet.write_number(row, column + 4, sumYear50, row_format_number)
                    sheet.write_number(row, column + 4 + 42, sumYear50*profitability / 100, row_format_number)
            column += 4
        # end Валовая Выручка, без НДС

    def printworksheet(self,workbook,budget,namesheet):
        report_name = budget.name
        sheet = workbook.add_worksheet(namesheet)
        sheet.set_zoom(85)
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
        })

        row_format_date_month.set_num_format('mmm yyyy')
        row_format = workbook.add_format({
            'border': 1,
            'font_size': 10
        })
        row_format_number = workbook.add_format({
            'border': 1,
            'font_size': 10,
        })
        row_format_number.set_num_format('#,##0.00')

        date_format = workbook.add_format({'num_format': 'd mmmm yyyy'})
        row = 0
        sheet.merge_range(row,0,row,10, budget.name, bold)
        row = 6
        column = 0
        sheet.write_string(row, column, "Прогноз",head_format)
        sheet.write_string(row+1, column, "Проектный офис", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 21.5)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "КАМ", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 19.75)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Заказчик", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 25)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Наименование Проекта", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 12.25)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Номер этапа проекта", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 15)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Стадия продажи", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 16.88)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Сумма проекта, вруб", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 14)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Валовая прибыль экспертно, в руб", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 14)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Прибыльность, экспертно, %", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 9)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "Номер договора", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 11.88)
        column += 1
        sheet.write_string(row, column, "", head_format)
        sheet.write_string(row+1, column, "НДС", head_format_1)
        sheet.write_string(row + 2, column, "", head_format_1)
        sheet.set_column(column, column, 7)
        column += 1
        column = self.print_month_head_contract_pds(workbook, sheet, row, column,  '2023')
        column = self.print_month_head_revenue_margin(workbook, sheet, row, column,  '2023')
        row += 2
        for spec in budget.projects_ids:
            # if spec.estimated_probability_id.name != '0':
            if spec.vgo == '-':
                row += 1
                if spec.project_have_steps:
                    for step in spec.project_steps_ids:
                        column = 0
                        sheet.write_string(row, column, spec.project_office_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.project_manager_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.customer_organization_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, step.essence_project, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.project_id + " | "+step.step_id, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.estimated_probability_id.name, row_format)
                        column += 1
                        sheet.write_number(row, column, step.total_amount_of_revenue_with_vat, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.margin_income, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.profitability, row_format_number)
                        column += 1
                        sheet.write_string(row, column, "", row_format)
                        column += 1
                        sheet.write_string(row, column, step.vat_attribute_id.name, row_format)
                        self.print_row_Values(workbook, sheet, row, column,  '2023', spec, step)
                        row += 1
                    row -= 1
                else:
                    column = 0
                    sheet.write_string(row, column, spec.project_office_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.project_manager_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.customer_organization_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.essence_project, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.project_id, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.estimated_probability_id.name, row_format)
                    column += 1
                    sheet.write_number(row, column, spec.total_amount_of_revenue_with_vat, row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.margin_income, row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.profitability, row_format)
                    column += 1
                    sheet.write_string(row, column, "", row_format)
                    column += 1
                    sheet.write_string(row, column, spec.vat_attribute_id.name, row_format)
                    self.print_row_Values(workbook, sheet, row, column,  '2023', spec, None)

    def generate_xlsx_report(self, workbook, data, budgets):
        for budget in budgets:
            self.printworksheet(workbook, budget, 'Прогноз')
