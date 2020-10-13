# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class HelpdeskReport(models.Model):
    _name = "helpdesk.report"
    _description = "Helpdesk Report"
    _auto = False

    stage_id = fields.Many2one('helpdesk.stage', string="Helpdesk Stage", readonly=True)
    total_time_spent = fields.Float('Total Time Spent')
    avg_time_spent = fields.Float('Average Time Spent')
    tickets = fields.Integer('Tickets')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""
        select_ = """
            MIN(htst.stage_id) AS id,
            htst.stage_id AS stage_id,
            SUM(htst.time_spent) AS total_time_spent,
            (SUM(htst.time_spent) / count(htst.ticket_id)) AS avg_time_spent,
            count(htst.ticket_id) AS tickets,
            count(*) as nbr
        """
        from_ = """
            helpdesk_ticket_stage_tracking htst
            %s
        """ % from_clause
        groupby_ = """
            htst.stage_id
        """
        return '%s (SELECT %s FROM %s GROUP BY %s)' % (with_, select_, from_, groupby_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
