# -*- coding: utf-8 -*-
# Part of Eagle ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Italy - E-invoicing',
    'version': '0.3',
    'depends': ['l10n_it'],
    'author': 'Eagle ERP',
    'description': """
E-invoice implementation
    """,
    'category': 'Localization',
    'website': 'http://www.eagle.com/',
    'data': [
        'security/ir.model.access.csv',
        'data/invoice_it_template.xml',
        'views/l10n_it_view.xml',
        ],
    'demo': [
        'data/account_invoice_demo.xml',
    ],
}