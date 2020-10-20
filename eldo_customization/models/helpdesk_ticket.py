# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
   
    stage_name = fields.Char(string="Stage", related="stage_id.name")
    stage_tracking_ids = fields.One2many('helpdesk.ticket.stage.tracking', 'ticket_id', string="Stage Tracking")

    @api.model
    def message_new(self, msg, custom_values=None):
        res = super(HelpdeskTicket, self).message_new(msg=msg, custom_values=custom_values)
        res.update({'stage_id': self.env.ref('eldo_customization.stage_new_email').id})
        return res

    @api.multi
    def message_update(self, msg, update_vals=None):
        res = super(HelpdeskTicket, self).message_update(msg=msg, update_vals=update_vals)
        self.write({'stage_id': self.env.ref('eldo_customization.stage_new_email').id})
        return res

    @api.model
    def create(self, vals):
        res = super(HelpdeskTicket, self).create(vals)
        if res.stage_id:
            curr_datetime = fields.datetime.now()
            track_id = self.env['helpdesk.ticket.stage.tracking'].search([('ticket_id', '=', res.id), ('stage_id', '=', vals.get('stage_id'))], limit=1)
            if not track_id:
                self.env['helpdesk.ticket.stage.tracking'].create({
                    'stage_id': res.stage_id.id,
                    'ticket_id': res.id,
                    'start_date': curr_datetime,
                    'ticket_type_id': res.ticket_type_id.id if res.ticket_type_id else False,
                    'team_id': res.team_id.id if res.team_id.id else False
                })
        return res

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('stage_id', False):
                curr_datetime = fields.datetime.now()
                track_id = self.env['helpdesk.ticket.stage.tracking'].search([('ticket_id', '=', rec.id), ('stage_id', '=', vals.get('stage_id'))], limit=1)
                if not track_id:
                    self.env['helpdesk.ticket.stage.tracking'].create({
                        'stage_id': vals.get('stage_id'),
                        'ticket_id': rec.id,
                        'start_date': curr_datetime,
                        'ticket_type_id': rec.ticket_type_id.id if rec.ticket_type_id else False,
                        'team_id': rec.team_id.id if rec.team_id.id else False
                    })
                else:
                    track_id.write({
                        'start_date': curr_datetime,
                        'end_date': False
                    })
                curr_track_id = self.env['helpdesk.ticket.stage.tracking'].search([('ticket_id', '=', rec.id), ('stage_id', '=', rec.stage_id.id)], limit=1)
                if curr_track_id:
                    curr_track_id.write({
                        'end_date': curr_datetime,
                        'time_spent': (curr_track_id.time_spent + ((curr_datetime - curr_track_id.start_date).total_seconds() / 3600))
                    }) 
        return super(HelpdeskTicket, self).write(vals)


class HelpdeskTicketStageTracking(models.Model):
    _name = 'helpdesk.ticket.stage.tracking'
    _description = "Helpdesk Ticket Stage Tracking"

    stage_id = fields.Many2one('helpdesk.stage', string="Name")
    ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket")
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string="Ticket Type")
    team_id = fields.Many2one('helpdesk.team', string="Helpdesk Team")
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    time_spent = fields.Float('Time Spent')
