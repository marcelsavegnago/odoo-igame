# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class Board(models.Model):
    _inherit = "og.board"
    
    @api.multi
    def bid(self, pos, call):
        ret = super(Board, self).bid(pos, call)
        if ret:
            return ret
        
        for channel in self.table_id.channel_ids:
            #TBD
            subject = 'bid'
            body  = {
                table_id: self.table_id.id,
                board_id: self.id,
            }
            channel.message_post(body=body, subject=subject )
        
        return ret

    @api.multi
    def play(self,pos,card):
        ret = super(Board, self).play(pos, card)
        if ret:
            return ret
        
        for channel in self.table_id.channel_ids:
            #TBD
            subject = 'play'
            body  = {
                table_id: self.table_id.id,
                board_id: self.id,
            }
            channel.message_post(body=body, subject=subject )

        return ret

    @api.multi
    def claim(self,pos,num):
        ret = super(Board, self).claim(pos, num)
        if ret:
            return ret
        
        for channel in self.table_id.channel_ids:
            #TBD
            subject = 'claim'
            body  = {
                table_id: self.table_id.id,
                board_id: self.id,
            }
            channel.message_post(body=body, subject=subject )

        return ret

    @api.multi
    def undo(self):
        ret = super(Board, self).undo()
        if not ret:
            return ret
        
        for channel in self.table_id.channel_ids:
            #TBD
            subject = 'undo'
            body  = {
                table_id: self.table_id.id,
                board_id: self.id,
            }
            channel.message_post(body=body, subject=subject )
            
        return ret

class Table(models.Model):
    _inherit = "og.table"
    channel_ids = fields.One2many('og.channel','table_id')
    

class GameChannel(models.Model):
    _name = "og.channel"

    name = fields.Char(related='mail_channel_id.name')
    table_id = fields.Many2one('og.table')
    
    mail_channel_id = fields.Many2one('mail.channel')
    #channel_partner_ids = fields.Many2many('res.partner', 
    #    related='mail_channel_id.channel_partner_ids' )
        
    type = fields.Selection([('all',       'To All'),
                             ('spectator', 'To All Spectators'),
                             ('one',       'To One Spectator'),
                             ('player',    'To All Player'),
                             ('opps',      'To Opps'),
                             ('lho',       'To LHO'),
                             ('rho',       'To RHO'),

                             ], default='all')



    @api.multi
    def message_get(self, message_id ):
        self = self.sudo()

        # TBD,  message format
        msg = self.env['mail.message'].browse(message_id)
        #print(msg)
        subject = msg.subject
        body = msg.body
        table = self.table_id
        return { 'test1': subject, 'test2': body }


    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None ):
        self = self.sudo()
        
        # TBD
        # table_id
        # get new status from table
        # and wrap up message to body
        
        return self.mail_channel_id.message_post(body=body, subject=subject,
                      message_type='comment', subtype='mail.mt_comment')


    @api.multi
    def unlink(self):
        for rec in self:
            rec.mail_channel_id.unlink()
        return super(GameChannel,self).unlink()

    #@api.returns('self')
    @api.model
    def create(self, vals):
    
        name = vals.get('name')
        table_id = vals.get('table_id')

        table = self.env['og.table'].browse(table_id)
        
        partner_ids = table.table_player_ids.mapped(
            'player_id').mapped('partner_id').ids
            
        channel_vals = {
            'name' : name,
            'public':'private',
            'channel_last_seen_partner_ids': [
                [ 0,0,{'partner_id':ptn}] for ptn in partner_ids ]
        }

        mail_channel = self.env['mail.channel'].create(channel_vals)
        
        vals = {
            'name' : name,
            'table_id' : table_id,
            'mail_channel_id': mail_channel.id }

        return super(GameChannel,self).create(vals)

