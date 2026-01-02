# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

_logger.info("Cargando modelos de modulos_contabilidad...")

from . import account_discount_rule
from . import res_partner
from . import account_move
from . import account_move_line

_logger.info("Modelos de modulos_contabilidad cargados correctamente")
