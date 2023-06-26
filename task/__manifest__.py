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
            'project/static/src/js/widgets/*',
            'project/static/src/components/**/*'
        ],
        'project.webclient': [
            'project/static/src/components/task_task_name_with_subtask_count_char_field/*'
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/task_security.xml',
        'views/task_views.xml'
    ],
    'demo': [
    ],
    'license': 'LGPL-3',
}
