# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


from .bridge_tools import PASS, DBL, RDB, CALLS
from .bridge_tools import POSITIONS
from .bridge_tools import TRUMPS,RISKS,CONTRACTS
from .bridge_tools import SUITS,RANKS,CARDS
from .bridge_tools import partner, lho
from .bridge_tools import get_point



class Board(models.Model):
    _name = "og.board"
    _description = "Board"
    _rec_name = 'number'
    _order = 'number'

    table_id = fields.Many2one('og.table')
    deal_id = fields.Many2one('og.deal')
    card_str = fields.Char(related='deal_id.card_str')

    name   = fields.Char('Name', related='deal_id.name' )
    number = fields.Integer(related='deal_id.number' )
    dealer = fields.Selection(related='deal_id.dealer' )
    vulnerable = fields.Selection(related='deal_id.vulnerable' )

    call_ids = fields.One2many('og.board.call','board_id')

    declarer   = fields.Selection(POSITIONS,compute='_compute_contract')
    contract =  fields.Selection(CONTRACTS,compute='_compute_contract')
    
    declarer_manual   = fields.Selection(POSITIONS )
    contract_manual =  fields.Selection(CONTRACTS )
    
    contract_rank = fields.Integer(compute='_compute_contract2')
    contract_trump = fields.Selection(TRUMPS,compute='_compute_contract2')
    contract_risk =  fields.Selection(RISKS,compute='_compute_contract2')

    openleader = fields.Selection(POSITIONS,compute='_compute_contract2')
    dummy      = fields.Selection(POSITIONS,compute='_compute_contract2')
    
    bidder     = fields.Selection(POSITIONS,compute='_compute_bidder')

    @api.multi
    def _compute_contract(self):
        for rec in self:
            if not (rec.declarer_manual and rec.contract_manual):
                dclr,contract,rank,trump,risk = rec.call_ids._compute_contract()
                rec.contract_manual = contract
                rec.declarer_manual = dclr
            
            rec.contract = rec.contract_manual
            rec.declarer = rec.declarer_manual
            
    @api.multi
    def _compute_contract2(self):
        for rec in self:
            ctrct = rec.contract
            rec.contract_rank  = ctrct and int(ctrct[0]) or 0
            trump = ctrct and ctrct[1] or None
            rec.contract_trump =  trump == 'N' and 'NT' or trump 
            rec.contract_risk = ctrct and ctrct[-2:]=='xx' and RDB or (
                                ctrct and ctrct[-1:]== 'x' and DBL or '')
                                
            dclr = rec.declarer
            rec.dummy = dclr and partner(dclr) or None
            rec.openleader = dclr and lho(dclr) or None
            
    @api.multi
    def _compute_bidder(self):
        for rec in self:
            if rec.contract:
                rec.bidder = None
                continue
            cs = rec.call_ids
            rec.bidder = cs and lho(cs[-1].pos) or rec.dealer or None

    openlead = fields.Selection(CARDS, compute='_compute_openlead')
    openlead_manual = fields.Selection(CARDS)

    player = fields.Selection(POSITIONS,compute='_compute_player')
    last_trick =  fields.One2many('og.board.card',compute='_compute_trick')
    current_trick=fields.One2many('og.board.card',compute='_compute_trick')

    def _get_tricks(self):
        """All Played Cards """
        cs = self.card_ids.filtered(lambda c: c.number)
        ts = list( set([ c.trickno for c in cs] ) )
        ts.sort()
        return [ cs.filtered(lambda c: c.trickno==t) for t in ts]

    @api.multi
    def get_tricks(self):
        return self._get_tricks()

    @api.multi
    def _compute_trick(self):
        for rec in self:
            ts = rec._get_tricks()
            rec.last_trick = ( ts and len(ts)>=2 and ts[-2]
                             ) or rec.env['og.board.card']

            rec.current_trick = ( ts and ts[-1]
                                ) or rec.env['og.board.card']

    @api.multi
    def _compute_player(self):
        def fn(rec):
            ts = rec._get_tricks()
            ct = ts and ts[-1] or None

            if not ct:
                return rec.openleader
            elif len(ct)<4:
                ct = [c for c in ct]
                ct.sort(key=lambda c: c.number)
                return lho(ct[-1].pos)
            else:
                return ct.get_winner(rec.contract_trump)

        for rec in self:
            rec.player = fn(rec)

    @api.multi
    def _compute_openlead(self):
        def fn(rec):
            ts = rec._get_tricks()
            t1 = ts and ts[0] or []
            t1 = [c for c in t1]
            t1.sort(key=lambda c: c.number)
            return t1 and t1[0].name or None

        for rec in self:
            if not rec.openlead_manual:
                rec.openlead_manual = fn(rec)

            rec.openlead = rec.openlead_manual


    declarer_win = fields.Integer(compute='_compute_win')
    opp_win = fields.Integer(compute='_compute_win')
    ns_win  = fields.Integer(compute='_compute_win')
    ew_win  = fields.Integer(compute='_compute_win')

    @api.multi
    def _compute_win(self):
        for rec in self:
            dclr, opp, ns, ew = rec._get_win()
            rec.declarer_win = dclr
            rec.opp_win = opp
            rec.ns_win  = ns
            rec.ew_win  = ew

    def _get_win(self):
        ts = self._get_tricks()

        def fn(trick):
            w = trick.get_winner(self.contract_trump)
            if not w:
                return 0, 0
            return w in 'NS' and (1,0) or (0,1)

        nsew = [ fn(t) for t in ts ]
        ns = sum( [ win[0] for win in nsew ] )
        ew = sum( [ win[1] for win in nsew ] )

        if not self.declarer:
            dclr, opp = 0, 0
        else:
            dclr, opp = self.declarer in 'NS' and (ns, ew
                                             ) or (ew, ns)
        return dclr, opp, ns, ew

    claimer = fields.Selection(POSITIONS)
    claim_result = fields.Integer()
    declarer_claim = fields.Integer(compute='_compute_claim')
    opp_claim = fields.Integer(compute='_compute_claim')
    ns_claim  = fields.Integer(compute='_compute_claim')
    ew_claim  = fields.Integer(compute='_compute_claim')

    @api.multi
    def _compute_claim(self):
        for rec in self:
            dclr, opp, ns, ew = rec._get_claim()
            rec.declarer_claim = dclr
            rec.opp_claim = opp
            rec.ns_claim  = ns
            rec.ew_claim  = ew

    def _get_claim(self):
        dclr, opp, ns, ew = 0, 0, 0, 0

        if not self.claimer:
            return dclr, opp, ns, ew

        rest = 13 - self.declarer_win - self.opp_win
        fst, scd = self.claim_result, rest - self.claim_result

        dclr, opp = self.claimer==self.declarer and (fst, scd
                                               ) or (scd, fst)
        ns, ew = self.declarer in 'NS' and (dclr, opp
                                      ) or (opp, dclr)
        return dclr, opp, ns, ew


    trick_count = fields.Integer(compute='_compute_trick_cnt')

    @api.multi
    def _compute_trick_cnt(self):
        for rec in self:
            cnt = rec.declarer_win + rec.opp_win
            cnt += rec.declarer_claim + rec.opp_claim
            rec.trick_count = cnt

    result = fields.Integer(compute='_compute_result')
    result2 = fields.Char(compute='_compute_result2')

    @api.multi
    def _compute_result(self):
        def fn(rec):
            if not rec.contract or rec.contract == PASS or rec.trick_count<13:
                return 0

            rslt = rec.declarer_win + rec.declarer_claim
            rslt -= (rec.contract_rank + 6)
            return rslt
            
        for rec in self:
            rec.result = fn(rec)

    @api.multi
    def _compute_result2(self):
        def fn(rec):
            if not rec.contract:
                return None

            if rec.contract == PASS:
                return 'All Pass'

            if rec.trick_count<13:
                return None
                
            if rec.result is None:
                return None

            rslt = rec.result

            rslt2 = rslt == 0 and '=' or ((rslt>0 and '+' or '') + str(rslt) )

            rslt2 = rec.declarer and rec.contract and (
                    rec.declarer + ' ' + rec.contract + ' ' + rslt2
                    ) or None
                    
            return rslt2

        for rec in self:
            rec.result2 = fn(rec)

    point = fields.Integer(compute='_compute_point')
    ns_point = fields.Integer(compute='_compute_point')
    ew_point = fields.Integer(compute='_compute_point')

    @api.multi
    def _compute_point(self):
        for rec in self:
            rec.point, rec.ns_point, rec.ew_point = rec._get_point()

    def _get_point(self):
        #if self.trick_count<13 or self.contract == PASS:
        if self.trick_count<13:
            return 0, 0, 0

        if self.contract == PASS:
            return 0, 0, 0


        vs = {  'BO': lambda d: 1,
                'NO': lambda d: 0,
                'NS': lambda d: d in 'NS',
                'EW': lambda d: d in 'EW' }

        vul = vs[self.vulnerable](self.declarer)
        rank = self.contract_rank
        trump = self.contract_trump
        risk = self.contract_risk
        num = self.result

        point = get_point(vul,rank,trump,risk,num)


        dclr = point > 0 and point or 0
        opp  = point < 0 and -point or 0
        
        ns, ew = self.declarer in 'NS' and (dclr, opp) or (opp,dclr)
        return point, ns, ew

    card_ids  = fields.One2many('og.board.card','board_id')

    @api.model
    def create(self, vals):
        deal = vals.get('deal_id')
        if not deal:
            return 0
        nvs = vals.copy()
        if nvs.get('card_ids'):
            del nvs['card_ids']

        board = super(Board,self).create(nvs)

        for dc in board.deal_id.card_ids:
            cards = {'board_id': board.id,'deal_card_id':dc.id }
            board.card_ids.create(cards)

        return board
