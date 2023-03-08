{
    'name' : 'Project_budget',
    'version' : '1.0',
    'category': 'Project',
    'depends': ['base','mail','uom'],
    'description':"""
    """,
    'author': 'lapus',
    'support': 'lapushkov@yandex.ru',
    'assets': {
        'web._assets_primary_variables': [
            'web/static/src/scss/primary_variables.scss'
        ]
    },
    'data': [
        'security/project_budget_users_groups.xml',
        'security/project_budget_users_rules.xml',
        'security/ir.model.access.csv',
        'views/project_id_generate.xml',
        'views/project_budget_catalogs.xml',
        'views/project_budget_comercial_budget_access.xml',
        'views/project_budget_comercial_budget_search.xml',
        'views/project_budget_comercial_budget.xml',
        'views/project_budget_menu.xml',
        'report/project_budget_report.xml',
        'report/project_budget_report_template.xml',
    ],
    'demo':[

    ],
    'application':True,
    'images': ['static/description/banner.png'],
    'installable':True,
    'auto_install': False,
    'license': 'LGPL-3',
}