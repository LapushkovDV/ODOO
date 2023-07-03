{
    'name': 'Task Management',
    'version': '16.0.1.0.0',
    'category': '',
    'depends': ['base', 'mail', 'uom'],
    'description': """
    """,
    'author': '',
    'support': '',
    'application': True,
    'installable': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
    'assets': {
        'web.assets_backend': [
        ]
    },
    'depends': [
        'base',
        'crnd_web_diagram_plus'
    ],
    'data': [
        'data/task_data.xml',
        'security/task_security.xml',
        'security/ir.model.access.csv',
        'views/task_views.xml',
        'views/task_type_views.xml',
        'views/task_stage_views.xml',
        'views/task_stage_type_views.xml',
        'views/task_stage_route_views.xml'
    ],
    'demo': [
    ],
    'license': 'LGPL-3'
}
