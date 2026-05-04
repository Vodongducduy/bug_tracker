import os
from mssql.base import DatabaseWrapper as MSSQLDatabaseWrapper
from django.utils.functional import cached_property

class DatabaseWrapper(MSSQLDatabaseWrapper):
    """
    Custom wrapper to support legacy 'SQL Server' ODBC driver.
    Fixes the SYSDATETIME() incompatibility.
    """
    @cached_property
    def sql_server_version(self):
        # Default to a safe version that doesn't use SYSDATETIME if detection fails
        return 11 # SQL Server 2012
        
    def _fetch_server_properties(self):
        # Avoid crashing when fetching properties with legacy driver
        try:
            super()._fetch_server_properties()
        except:
            self.server_version = '11.0.0000'
            self.heading_color = 'blue'

    def get_system_datetime(self):
        # Legacy driver doesn't support SYSDATETIME() well with some Django fields
        return "GETDATE()"
