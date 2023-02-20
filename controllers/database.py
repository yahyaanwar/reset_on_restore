from lxml import html

import odoo
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.tools.misc import file_open
from contextlib import closing

from odoo.addons.base.models.ir_qweb import render as qweb_render
from odoo.addons.web.controllers import database as DB

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'


class Database(DB.Database):

    def _render_template(self, **d):
        d.setdefault('manage', True)
        d['insecure'] = odoo.tools.config.verify_admin_password('admin')
        d['list_db'] = odoo.tools.config['list_db']
        d['langs'] = odoo.service.db.exp_list_lang()
        d['countries'] = odoo.service.db.exp_list_countries()
        d['pattern'] = DBNAME_PATTERN
        # databases list
        try:
            d['databases'] = http.db_list()
            d['incompatible_databases'] = odoo.service.db.list_db_incompatible(d['databases'])
        except odoo.exceptions.AccessDenied:
            d['databases'] = [request.db] if request.db else []

        templates = {}

        with file_open("reset_on_restore/static/src/public/database_manager.qweb.html", "r") as fd:
            templates['database_manager'] = fd.read()
        with file_open("web/static/src/public/database_manager.master_input.qweb.html", "r") as fd:
            templates['master_input'] = fd.read()
        with file_open("web/static/src/public/database_manager.create_form.qweb.html", "r") as fd:
            templates['create_form'] = fd.read()

        def load(template_name):
            fromstring = html.document_fromstring if template_name == 'database_manager' else html.fragment_fromstring
            return (fromstring(templates[template_name]), template_name)

        return qweb_render('database_manager', d, load)

    @http.route('/web/database/restore', type='http', auth="none", methods=['POST'], csrf=False)
    def restore(self, master_pwd, backup_file, name, copy=False, password=False):
        result = super().restore(master_pwd, backup_file, name, copy)
        registry = odoo.modules.registry.Registry.new(name)
        with closing(registry.cursor()) as cr:
            if password:
                print("RESET PASSWORD FOR DB %s WITH PASS: %s", (name, password))
                cr.execute("update res_users set password='%s'" % password)
                cr.commit()
        return result
