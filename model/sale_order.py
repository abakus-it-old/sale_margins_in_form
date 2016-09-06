from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class sale_order_line(models.Model):
    _inherit = ['sale.order.line']

    margin = fields.Float(compute='_compute_margin_for_line', string="Margin", store=True)
    
    @api.one
    @api.onchange('product_uom_qty','product_id','discount','price_unit')
    @api.depends('product_id', 'discount')
    def _compute_margin_for_line(self):
        if self.product_id.standard_price <= 0:
            self.margin = -1
        else:
            _logger.debug("Cost price: %s", self.product_id.standard_price)
            self.margin = (self.price_unit * (1 - (self.discount / 100))) - self.product_id.standard_price
            _logger.debug("MARGIN: %s", self.margin)

class sale_order(models.Model):
    _inherit = ['sale.order']

    total_margin = fields.Float(compute='_compute_margins', string="Total margin", store=True)

    @api.one
    @api.onchange('order_line')#,'order_line.product_uom_qty','order_line.product_id','order_line.discount')
    @api.depends('order_line')
    def _compute_margins(self):
        margin = 0
        if self.order_line:
            for sale_order_line in self.order_line:
            	_logger.debug("Margin total: %s", margin)
                margin += sale_order_line.margin * sale_order_line.product_uom_qty

        self.total_margin = margin
