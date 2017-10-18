# -*- coding: utf-8 -*-
"""
Datary Api python sdk Operations module.
"""
from .add import DataryAddOperation
from .modify import DataryModifyOperation
from .remove import DataryRemoveOperation
from .rename import DataryRenameOperation
from .clean import DataryCleanOperation

_DEFAULT_LIMITED_DATARY_SIZE = 12000000


class DataryOperations(DataryAddOperation, DataryModifyOperation,
                       DataryRenameOperation, DataryCleanOperation):
    """
    Datary operations class
    """
    pass
