# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

_logger.info("Cargando modelos de hr_performance_review...")

from . import hr_performance_review
from . import hr_employee

_logger.info("Modelos de hr_performance_review cargados correctamente")

