{
    'name': 'Document Flow',
    'version': '1.0.0',
    'category': '',
    'depends': ['base', 'mail', 'uom', 'task'],
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
            'document_flow/static/src/css/html_fields.css',
        ]
    },
    'data': [
        'security/ir.model.access.csv',
        'views/event_task_views.xml',
        'views/event_views.xml',
        'views/event_question_views.xml',
        'views/event_decision_views.xml',
    ],
    'demo': [
    ],
    'license': 'LGPL-3',
}
