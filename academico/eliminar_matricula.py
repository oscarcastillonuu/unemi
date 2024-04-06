
#!/usr/bin/env python
import os
import sys


# SITE_ROOT = os.path.dirname(os.path.realpath(_file_))

# your_djangoproject_home = os.path.split(SITE_ROOT)[0]
# sys.path.append(your_djangoproject_home)
import xlrd
from django.core.wsgi import get_wsgi_application

from Moodle_Funciones import updaterubroepunemi
from settings import EMAIL_INSTITUCIONAL_AUTOMATICO, PROFESORES_GROUP_ID, EMAIL_DOMAIN

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
application = get_wsgi_application()
from sga.models import *
from posgrado.models import *
from sagest.models import *


matriculas = Matricula.objects.filter(id__in=[311622,
311621,
311614,
311613,
311612,
311611,
311610,
311609,
311608,
311607,
311606,
311598,
311597,
311596,
311595,
311594,
311593,
311592,
311591,
311590,
311589,
311588,
311587,
311586,
311585,
311584,
311583,
311582,
311581,
311580,
311579,
311578,
311577,
311576,
311575,
311574,
311573,
311572,
311571,
311570,
311569,
311568,
311567,
311566,
311565,
311564,
311563,
311562,
311561,
311560,
311559,
311558,
311556,
311555,
311554,
311553,
311552,
311551,
311550,
311549,
311548,
311547,
311546,
311545,
311544,
311543,
311542,
311541,
311540,
311539,
311538,
311537,
311536,
311535,
311534,
311533,
311532,
311531,
311530,
311529,
311528,
311527,
311526,
311525,
311524,
311523,
311522,
311521,
311520,
311519,
311518,
311517,
311516,
311515,
311514,
311513,
311512,
311511,
311510,
311509,
311508,
311507,
311506,
311505,
311504,
311503,
311502,
311501,
311500,
311499,
311498,
311497,
311496,
311495,
311494,
311493,
311492,
311491,
311490,
311489,
311488,
311487,
311486,
311485,
311484,
311483,
311482,
311481,
311480,
311479,
311478,
311477,
311476,
311475,
311474,
311473,
311472,
311471,
311470,
311469,
311468,
311467,
311466,
311465,
311464,
311463,
311462,
311461,
311460,
311459,
311458,
311457,
311456,
311455,
311454,
311453,
311452,
311451,
311450,
311449,
311448,
311447,
311446,
311445,
311444,
311443,
311442,
311441,
311440,
311439,
311438,
311276])
conta=0
for matri in matriculas:
    conta = conta + 1
    matri.delete()
    print(conta)
