from odoo import models

class report_budget_excel(models.AbstractModel):
    _name = 'report.project_budget.report_budget_excel'
    _description = 'project_budget.report_budget_excel'
    _inherit = 'report.report_xlsx.abstract'
    def printworksheet(self,workbook,budget,namesheet,stateproject):
        report_name = budget.name
            # One sheet by partner
        sheet = workbook.add_worksheet(namesheet)
        bold = workbook.add_format({'bold': True})
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        head_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'font_size': 11,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#3265a5'
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
            'num_format': '#,##0.00'
        })

        date_format = workbook.add_format({'num_format': 'd mmmm yyyy'})
        row = 0
        sheet.merge_range(row,0,row,10, budget.name, bold)
        row += 1
        sheet.merge_range(row, 0, row, 1,"Состояние бюджета")
        sheet.merge_range(row, 2, row, 4,budget.budget_state, bold)
        row += 1
        sheet.merge_range(row, 0, row, 1, "Дата актуализации бюджета")
        if budget.date_actual:
            sheet.merge_range(row, 2, row, 4, budget.date_actual.strftime("%d/%m/%Y"), bold)
        row += 1
        sheet.merge_range(row, 0, row, 1, "Описание")
        sheet.merge_range(row, 2, row, 6, budget.descr  or "", bold)

        row += 2

        column = 0
        sheet.write_string(row, column, "Project ID",head_format)
        sheet.set_column(column, column, 14)
        column += 1
        sheet.write_string(row, column, "Проектный офис",head_format)
        sheet.set_column(column, column, 14)
        column += 1
        sheet.write_string(row, column, "Куратор проекта",head_format)
        sheet.set_column(column, column, 20)
        column += 1
        sheet.write_string(row, column, "Руководитель проекта",head_format)
        sheet.set_column(column, column, 15)
        column += 1
        sheet.write_string(row, column, "Заказчик/Организация",head_format)
        sheet.set_column(column, column, 25)
        column += 1
        sheet.write_string(row, column, "Статус Заказчика",head_format)
        sheet.set_column(column, column, 14)
        column += 1
        sheet.write_string(row, column, "Отрасль",head_format)
        sheet.set_column(column, column, 18)
        column += 1
        sheet.write_string(row, column, "Суть проекта",head_format)
        sheet.set_column(column, column, 45)
        column += 1
        sheet.write_string(row, column, "Дата окончания Presale-проекта (квартал)",head_format)
        sheet.set_column(column, column, 15)
        column += 1
        sheet.write_string(row, column, "Дата перехода в Производственный бюджет (МЕСЯЦ)",head_format)
        sheet.set_column(column, column, 15)
        column += 1
        sheet.write_string(row, column, " Дата окончания Sale-проекта (квартал)",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Период отгрузки либо оказания услуг Клиенту (МЕСЯЦ)",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Признак НДС",head_format)
        sheet.set_column(column, column, 13)
        column += 1
        sheet.write_string(row, column, "Общая сумма выручки, руб.",head_format)
        sheet.set_column(column, column, 13)
        column += 1
        sheet.write_string(row, column, " Выручка от реализации работ(услуг),  руб",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, " Выручка от реализации товара, руб",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Себестоимость , руб, в т.ч.:",head_format)
        sheet.set_column(column, column, 13)
        column += 1
        sheet.write_string(row, column, "Себестоимость товаров, руб",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Работы собственные (ФОТ), руб",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Работы сторонние (субподряд), руб",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Премии по итогам проекта, руб",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Транспортные расходы, руб.",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Командировочные расходы, руб",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, " Представительские расходы, руб.",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, " Налоги на ФОТ и премии, руб.",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, " Расходы на гарант. обслуж., руб.",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "РКО прочие руб.",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Прочие расходы, руб.",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Маржинальный доход, руб",head_format)
        sheet.set_column(column, column, 13)
        column += 1
        sheet.write_string(row, column, "Рентабельность (доля Sale маржи в выручке)",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Оценочная вероятность реализации проекта, %",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "юрлицо, подписывающее договор от НКК",head_format)
        sheet.set_column(column, column, 15)
        column += 1
        sheet.write_string(row, column, "Тип проекта",head_format)
        sheet.set_column(column, column, 10)
        column += 1
        sheet.write_string(row, column, "Комментарии",head_format)
        sheet.set_column(column, column, 15)
        column += 1
        sheet.write_string(row, column, "Технологическое направление",head_format)
        sheet.set_column(column, column, 15)
        sheet.autofilter(row, 0, row, column)

        for spec in budget.projects_ids:
            if spec.specification_state == stateproject:
                if spec.project_have_steps == False:
                    row += 1
                    column = 0
                    sheet.write_string(row, column, spec.project_id, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.project_office_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.project_supervisor_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.project_manager_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.customer_organization_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.customer_status_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.industry_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.essence_project  or "", row_format)
                    column += 1
                    sheet.write_string(row, column, spec.end_presale_project_quarter, row_format)
                    column += 1
                    sheet.write_datetime(row, column, spec.end_presale_project_month, row_format_date_month)
                    column += 1
                    sheet.write_string(row, column, spec.end_sale_project_quarter, row_format)
                    column += 1
                    sheet.write_datetime(row, column, spec.end_sale_project_month, row_format_date_month)
                    column += 1
                    sheet.write_string(row, column, spec.vat_attribute_id.name or "", row_format)
                    column += 1
                    sheet.write_number(row, column, spec.total_amount_of_revenue, row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.revenue_from_the_sale_of_works,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.revenue_from_the_sale_of_goods,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.cost_price,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.cost_of_goods,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.own_works_fot,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.third_party_works,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.awards_on_results_project,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.transportation_expenses,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.travel_expenses,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.representation_expenses,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.taxes_fot_premiums,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.warranty_service_costs,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.rko_other,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.other_expenses,row_format_number)
                    column += 1
                    sheet.write_number(row, column, spec.margin_income,row_format_number)
                    column += 1
                    sheet.write(row, column, spec.profitability, row_format_number)
                    column += 1
                    sheet.write(row, column, spec.estimated_probability_id.name, row_format_number)
                    column += 1
                    sheet.write(row, column, spec.legal_entity_signing_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.project_type_id.name, row_format)
                    column += 1
                    sheet.write_string(row, column, spec.comments or "", row_format)
                    column += 1
                    sheet.write_string(row, column, spec.technological_direction_id.name, row_format)
                else:
                    for step in spec.project_steps_ids:
                        row += 1
                        column = 0
                        sheet.write_string(row, column, spec.project_id + ' | ' + step.step_id, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.project_office_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.project_supervisor_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.project_manager_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.customer_organization_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.customer_status_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.industry_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, step.essence_project or "", row_format)
                        column += 1
                        sheet.write_string(row, column, step.end_presale_project_quarter, row_format)
                        column += 1
                        sheet.write_datetime(row, column, step.end_presale_project_month, row_format_date_month)
                        column += 1
                        sheet.write_string(row, column, step.end_sale_project_quarter, row_format)
                        column += 1
                        sheet.write_datetime(row, column, step.end_sale_project_month, row_format_date_month)
                        column += 1
                        sheet.write_string(row, column, step.vat_attribute_id.name or "", row_format)
                        column += 1
                        sheet.write_number(row, column, step.total_amount_of_revenue, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.revenue_from_the_sale_of_works, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.revenue_from_the_sale_of_goods, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.cost_price, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.cost_of_goods, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.own_works_fot, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.third_party_works, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.awards_on_results_project, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.transportation_expenses, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.travel_expenses, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.representation_expenses, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.taxes_fot_premiums, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.warranty_service_costs, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.rko_other, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.other_expenses, row_format_number)
                        column += 1
                        sheet.write_number(row, column, step.margin_income, row_format_number)
                        column += 1
                        sheet.write(row, column, step.profitability, row_format_number)
                        column += 1
                        sheet.write(row, column, spec.estimated_probability_id.name, row_format_number)
                        column += 1
                        sheet.write(row, column, spec.legal_entity_signing_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.project_type_id.name, row_format)
                        column += 1
                        sheet.write_string(row, column, spec.comments or "", row_format)
                        column += 1
                        sheet.write_string(row, column, spec.technological_direction_id.name, row_format)
                #sheet.write(row, 0, 'Total', bold, row_format)
                #sheet.write(row, 2, '=SUM(C2:C5, row_format)', money_format, row_format)


    def generate_xlsx_report(self, workbook, data, budgets):
        for budget in budgets:
            self.printworksheet(workbook, budget, 'КБ', 'prepare')
        for budget in budgets:
            self.printworksheet(workbook, budget, 'ПБ', 'production')
        for budget in budgets:
            self.printworksheet(workbook, budget, 'Отменен', 'cancel')
