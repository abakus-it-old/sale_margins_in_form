from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class sale_order_line(models.Model):
    _inherit = ['sale.order.line']

    margin = fields.Float(compute='_compute_margin_for_line', string="Margin", store=True)
    
    @api.one
    #@api.onchange('product_uom_qty','product_id','discount','price_unit')
    @api.depends('product_id', 'product_uom_qty', 'price_unit', 'discount')
    def _compute_margin_for_line(self):
        product_cost_price = self.product_id.standard_price
        if product_cost_price <= 0:
            _logger.debug("ERROR of price, standart product price == 0, so margin == -1")
            self.margin = -1
        else:
            #_logger.debug("Cost price: %s", product_cost_price)
            self.margin = (self.price_unit * (1 - (self.discount / 100))) - product_cost_price
            _logger.debug("MARGIN: %s", self.margin)

class sale_order(models.Model):
    _inherit = ['sale.order']

    total_margin = fields.Float(compute='_compute_margins', string="Total margin", store=True)

    @api.one
    @api.onchange('order_line')
    #,'order_line.product_uom_qty','order_line.product_id','order_line.discount')
    @api.depends('order_line')
    def _compute_margins(self):
        margin = 0
        if self.order_line:
            for sale_order_line in self.order_line:
                line_margin = sale_order_line.margin * sale_order_line.product_uom_qty
                #_logger.debug("LINE : margin = %s | qty = %s", sale_order_line.margin, sale_order_line.product_uom_qty)
                #_logger.debug("Margin for line (%s) : %s", sale_order_line.name, line_margin)
            	margin += line_margin
        else:
            _logger.debug("No line in SO (%s)", self.name)

        _logger.debug("Margin total: %s", margin)
        self.total_margin = margin
