# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

_logger.info("Cargando modelos de pos_loyalty_program...")

from . import pos_loyalty_history
from . import res_partner
from . import pos_config
from . import pos_order
from . import pos_session

_logger.info("Modelos de pos_loyalty_program cargados correctamente")

