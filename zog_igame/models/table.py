# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


POSITIONS = [
        ('-',  'Neednot'),
        ('NS', 'NS'),
        ('EW', 'EW'),
        ('N', 'North'),
        ('E', 'East'),
        ('S', 'South'),
        ('W', 'West'),
    ]


class Table(models.Model):
    _name = "og.table"
    _description = "Table"
    _order = 'number'

    name = fields.Char('Name' )
    number = fields.Integer(default=1 )
    room_type = fields.Selection([
        ('open', 'Open' ),
        ('close','Close')], string='Room Type', default='open')

    match_id = fields.Many2one('og.match', string='Match', ondelete='restrict')
    pair_round_id = fields.Many2one('og.game.round', string='Pair Round')
    round_id = fields.Many2one('og.game.round', string='Round',
                                compute='_get_round')
    game_id = fields.Many2one('og.game', related='round_id.game_id')

    @api.multi
    def _get_round(self):
        for rec in self:
            rec.round_id = rec.match_id and rec.match_id.round_id or (
                           rec.pair_round_id and rec.pair_round_id or None)

    deal_ids  = fields.Many2many('og.deal', string='Deals', related='round_id.deal_ids' )
    board_ids = fields.One2many('og.board', 'table_id', string='Boards')
    board_id = fields.Many2one('og.board', help="The board played now")

    ns_team_id = fields.Many2one('og.game.team', compute='_compute_team')
    ew_team_id = fields.Many2one('og.game.team', compute='_compute_team')

    @api.multi
    def _compute_team(self):
        for rec in self:
            teams = {'open.NS' : rec.match_id.host_id,
                     'open.EW' : rec.match_id.guest_id,
                     'close.NS': rec.match_id.guest_id,
                     'close.EW': rec.match_id.host_id,
                     }
            
            rec.ns_team_id = teams[rec.room_type + '.NS' ]
            rec.ew_team_id = teams[rec.room_type + '.EW' ]

    # pair game
    ns_pair_id = fields.Many2one('og.game.team')
    ew_pair_id = fields.Many2one('og.game.team')

    #table_partner_ids = fields.Many2many('res.partner','table_id')
    #player_user_ids = fields.Many2many('res.users','table_id')

    # 4 player in table
    east_id = fields.Many2one('og.game.team.player', 
                compute='_compute_player', inverse='_inverse_player_east')
    west_id = fields.Many2one('og.game.team.player',
                compute='_compute_player', inverse='_inverse_player_west')
    north_id = fields.Many2one('og.game.team.player',
                compute='_compute_player', inverse='_inverse_player_north')
    south_id = fields.Many2one('og.game.team.player',
                compute='_compute_player', inverse='_inverse_player_south')
    table_player_ids = fields.One2many('og.table.player','table_id')
    player_ids = fields.Many2one('og.game.team.player', compute='_compute_player')

    @api.multi
    def _compute_player(self):
        def _get(pos):
            return rec.table_player_ids.filtered(lambda p: p.position in pos ).player_id

        for rec in self:
            rec.east_id  = _get('E')
            rec.west_id  = _get('W')
            rec.north_id = _get('N')
            rec.south_id = _get('S')
            rec.player_ids = rec.table_player_ids.mapped('player_id')

    @api.onchange('east_id', 'west_id', 'north_id', 'south_id')
    def _inverse_player_east(self):
        self._inverse_player('E')

    @api.onchange('east_id', 'west_id', 'north_id', 'south_id')
    def _inverse_player_west(self):
        self._inverse_player('W')

    @api.onchange('east_id', 'west_id', 'north_id', 'south_id')
    def _inverse_player_north(self):
        self._inverse_player('N')

    @api.onchange('east_id', 'west_id', 'north_id', 'south_id')
    def _inverse_player_south(self):
        self._inverse_player('S')

    def _inverse_player(self,pos):
        for rec in self:
            table_player = rec.table_player_ids.filtered(lambda s: s.position==pos)

            ptns = {'N': rec.north_id,
                    'E': rec.east_id,
                    'S': rec.south_id,
                    'W': rec.west_id}

            if table_player:
                table_player.player_id = ptns[pos]
            else:
                vals = {'table_id':rec.id,
                        'position':pos,
                        'player_id': ptns[pos].id }

                table_player.create(vals)


class TablePlayer(models.Model):
    _name = "og.table.player"
    _description = "Table Player"

    name = fields.Char('Name', related = 'player_id.name' )

    table_id = fields.Many2one('og.table')
    player_id = fields.Many2one('og.game.team.player')
    team_id = fields.Many2one('og.game.team', related = 'player_id.team_id')
    position = fields.Selection(POSITIONS, string='Position', default='-')

