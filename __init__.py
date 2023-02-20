from odoo import api, SUPERUSER_ID, http
from odoo.exceptions import Warning

from . import controllers


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    return True


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    return True

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    return True


def apply_patch():
    pass
