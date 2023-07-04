{
'name': 'FM school',
'version': '1.0',
'author': 'Rohit',
'category': 'Education',
'description': 'storing students information',
'website': 'www.fmschool.org',
'depends': ['base', 'mail'],
'summary': 'This is a school management System',
'data': [
        'security/ir.model.access.csv',
        'views/student_details.xml',
        'views/demo_student.xml'
        ],
        'installable': True,
        'application': True,
        'auto_install': False,   
}
