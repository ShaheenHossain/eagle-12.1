# -*- coding: utf-8 -*-
# Part of Eagle. See LICENSE file for full copyright and licensing details.

from eagle import fields, models

class SomeObj(models.Model):
    _name = 'test_access_right.some_obj'
    _description = 'Object For Test Access Right'

    val = fields.Integer()


class Container(models.Model):
    _name = 'test_access_right.container'
    _description = 'Test Access Right Container'

    some_ids = fields.Many2many('test_access_right.some_obj', 'test_access_right_rel', 'container_id', 'some_id')
