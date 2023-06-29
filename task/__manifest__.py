{
    'name': 'Task Management',
    'version': '1.0.0',
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
    'data': [
        'data/task_data.xml',
        'security/ir.model.access.csv',
        'security/task_security.xml',
        'views/task_views.xml'
    ],
    'demo': [
    ],
    'license': 'LGPL-3',
}
