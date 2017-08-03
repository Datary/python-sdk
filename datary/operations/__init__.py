# -*- coding: utf-8 -*-
"""
Datary Api python sdk Operations module.
"""
from .add import DataryAddOperation
from .modify import DataryModifyOperation
from .remove import DataryRemoveOperation
from .clean import DataryCleanOperation


class DataryOperations(DataryAddOperation, DataryModifyOperation,
                       DataryCleanOperation):
    """
    Datary operations class
    """
    pass
