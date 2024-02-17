{
    "name": "DMS",
    "summary": """Document Management System""",
    "version": "2.1.0",
    "category": "Document Management",
    "license": "LGPL-3",
    "website": "",
    "author": "",
    "depends": ['base', 'mail'],
    "assets": {
        "web.assets_backend": [
            "dms/static/src/scss/*",
            "dms/static/src/js/views/**/*.js",
            "dms/static/src/js/views/**/*.xml"
        ],
    },
    "data": [
        'data/dms_data.xml',
        'security/dms_security.xml',
        'security/ir.model.access.csv',
        'views/ir_attachment_views.xml',
        'views/dms_storage_views.xml',
        'views/dms_directory_views.xml',
        'views/dms_document_views.xml',
        'views/dms_version_config_views.xml',
        'views/res_partner_views.xml',
        'views/dms_menu.xml'
    ],
    "demo": [
    ],
    "images": ["static/description/banner.png"],
    "application": True
}
