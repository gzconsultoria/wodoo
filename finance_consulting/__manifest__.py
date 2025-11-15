{
    'name': 'Finance Consulting Module',
    'version': '19.0.1.0.0',
    'category': 'Finance',
    'author': 'GZ Consultoria',
    'depends': [
        'base',
        'mail',
        'calendar',
        'crm',
        'account',
    ],
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/cron_jobs.xml',
        'data/automated_actions.xml',
        
        # Views
        'views/menus.xml',
        'views/finance_profile_views.xml',
        'views/investment_plan_views.xml',
        'views/portfolio_views.xml',
        'views/consulting_case_views.xml',
        'views/suitability_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
