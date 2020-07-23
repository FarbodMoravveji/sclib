# -*- coding: utf-8 -*-

class Parameters:
    """
    The Parameters class contains constant constants of the model.
    All attributes have a getter, but no setter. The default values
    are set internally.
    """
    _success: int                   # error code
    _abort: int                     # error code
    _retailer: str                  # Pre-defined agent role
    _manufacturer: str              # Pre-defined agent role
    _supplier: str                  # Pre-defined agent role
    _abs_tol: float                 # The parameter used for abs_tolerance in math.isclose() method.

    def __init__(self):
        """ Constructor """

        self._success = 1
        self._abort = 0
        self._retailer = 'r'
        self._manufacturer = 'm'
        self._supplier = 's'
        self._abs_tol = 1e-4

    @property
    def success(self) -> int:
        return self._success

    @property
    def abort(self) -> int:
        return self._abort

    @property
    def retailer(self) -> str:
        return self._retailer

    @property
    def manufacturer(self) -> str:
        return self._manufacturer

    @property
    def supplier(self) -> str:
        return self._supplier

    @property
    def abs_tol(self) -> float:
        return self._abs_tol