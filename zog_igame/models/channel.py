# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import json

import logging
_logger = logging.getLogger(__name__)

class Board(models.Model):
    _inherit = "og.board"

    def message_post(self, subject, message):
        for channel in self.table_id.channel_ids:
            body = json.dumps(message)
            channel.message_post(body=body, subject=subject )

    @api.multi
    def bid(self, pos, call):
        self = self.sudo()
        ret = super(Board, self).bid(pos, call)
        if ret:
            return ret

        for rec in self:
            subject = 'bid'
            message  = {
                'table_id': rec.table_id.id,
                'board_id': rec.id,
                'bidder': rec.bidder,
                'auction': rec.call_ids.read(['pos','name'])
            }
            rec.message_post(subject,message)

        return ret

    @api.multi
    def play(self,pos,card):
        ret = super(Board, self).play(pos, card)
        if ret:
            return ret
        
        return ret

    @api.multi
    def claim(self,pos,num):
        ret = super(Board, self).claim(pos, num)
        if ret:
            return ret
        
        return ret

    @api.multi
    def undo(self):
        ret = super(Board, self).undo()
        if not ret:
            return ret
        
        return ret

class Table(models.Model):
    _inherit = "og.table"
    channel_ids = fields.One2many('og.channel','table_id')
    

class GameChannel(models.Model):
    _name = "og.channel"

    name = fields.Char(related='mail_channel_id.name')
    table_id = fields.Many2one('og.table')
    
    mail_channel_id = fields.Many2one('mail.channel')

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
        uid = self.env.uid
        print('uid',uid)
        self = self.sudo()
        print('uid2',self.env.uid)
        msg = self.env['mail.message'].browse(message_id)
        #subject = msg.subject
        body = msg.body
        if body[:3] == '<p>' and body[-4:] == '</p>':
            body = body[3:-4]

        body = json.loads(body)
        body = {'uid':uid, 'board': body}

        return json.dumps(body)

    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None ):
        self = self.sudo()
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

