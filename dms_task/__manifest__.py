{
    'name': 'DMS: Task',
    'version': '1.0.0',
    'category': 'Document Management',
    'depends': ['dms', 'task'],
    'description': """
    """,
    'author': '',
    'support': '',
    'installable': True,
    'auto_install': True,
    'assets': {
        'web.assets_backend': [
            'dms/static/src/scss/*',
            'dms/static/src/views/**/*.js',
            'dms/static/src/views/**/*.xml'
        ],
    },
    'data': [
        'views/task_task_views.xml'
    ],
    'license': 'LGPL-3'
}
