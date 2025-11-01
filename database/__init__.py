"""
Database Package for Kingdom-77 Bot v3.0
=========================================
Provides MongoDB integration and data management.
"""

from .mongodb import MongoDB, db, init_database, close_database

__all__ = ['MongoDB', 'db', 'init_database', 'close_database']
__version__ = '4.0.0'
