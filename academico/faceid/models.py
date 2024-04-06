# -*- coding: UTF-8 -*-
import operator
import os
import random
import time
import sys
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.db import models, connection, connections
from sga.models import Persona
from sga.funciones import ModeloBase


class PersonTrainFace(ModeloBase):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, verbose_name='Persona')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fechahora = models.DateTimeField(blank=True, null=True, verbose_name='Fecha y hora')

    def __str__(self):
        return u'%s' % self.persona

    class Meta:
        verbose_name = u"Rostro facial"
        verbose_name_plural = u"Rostros faciales"
        unique_together = ('persona',)
