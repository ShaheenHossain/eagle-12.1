# -*- coding: utf-8 -*-
from eagle import fields, models


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('activity', 'Activity')])
