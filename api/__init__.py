"""
Kingdom-77 Dashboard API
========================
RESTful API endpoints for web dashboard integration.

Modules:
- applications_api: Application forms management
- automessages_api: Auto-messages system management
- social_api: Social media integration management
- auth: Authentication and authorization
"""

from .applications_api import ApplicationsAPI
from .automessages_api import AutoMessagesAPI
from .social_api import SocialAPI

__all__ = [
    'ApplicationsAPI',
    'AutoMessagesAPI',
    'SocialAPI'
]
