{
    'name': 'Document Flow',
    'version': '1.0.0',
    'category': '',
    'depends': ['base', 'mail', 'uom', 'task'],
    "external_dependencies": {"python": ["htmldocx"]},
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
        'security/document_flow_security.xml',
        'views/process_views.xml',
        'views/process_template_views.xml',
        'views/event_task_views.xml',
        'views/event_views.xml',
        'views/event_question_views.xml',
        'views/event_decision_views.xml',
        'views/management_committee_views.xml',
        'report/report.xml'
    ],
    'demo': [
    ],
    'license': 'LGPL-3',
}
