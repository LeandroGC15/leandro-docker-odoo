# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

_logger.info("=== Iniciando módulo sale_cross_selling ===")

from . import models
from . import wizard

_logger.info("=== Módulo sale_cross_selling cargado correctamente ===")

