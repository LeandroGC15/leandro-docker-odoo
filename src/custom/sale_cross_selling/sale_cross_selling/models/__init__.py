# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

_logger.info("Cargando modelos de sale_cross_selling...")

from . import product_cross_sell
from . import product_template
from . import sale_order

_logger.info("Modelos de sale_cross_selling cargados correctamente")

