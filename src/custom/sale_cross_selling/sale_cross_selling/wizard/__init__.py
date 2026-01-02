# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

_logger.info("Cargando wizards de sale_cross_selling...")

from . import cross_sell_wizard

_logger.info("Wizards de sale_cross_selling cargados correctamente")

