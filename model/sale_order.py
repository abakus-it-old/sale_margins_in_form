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
		cr = self.env.cr
		uid = self.env.user.id

		# Product as sellers
		if len(self.product_id.seller_ids) > 0:
			# get supplier info
			obj = self.pool.get('product.supplierinfo')
			supplier_info_ids = obj.search(cr, uid, [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)], order='sequence ASC')
			if len(supplier_info_ids) > 0:
				right_supplier = obj.browse(cr, uid, supplier_info_ids[0])

				computed_cost_price = right_supplier.price
				_logger.debug("Cost price: %s", computed_cost_price)
				self.margin = (self.price_unit * (1 - (self.discount / 100))) - computed_cost_price
				_logger.debug("MARGIN: %s", self.margin)
			else:
				 #error
				self.margin = -1
		else:
			discount = 0
			if (self.discount):
				self.margin = (self.price_unit * (1 - (self.discount / 100))) - self.product_id.standard_price

class sale_order(models.Model):
    _inherit = ['sale.order']

    total_margin = fields.Float(compute='_compute_margins', string="Total margin", store=True)

    @api.one
    @api.onchange('order_line')#,'order_line.product_uom_qty','order_line.product_id','order_line.discount')
    @api.depends('order_line')
    def _compute_margins(self):
        cr = self.env.cr
        uid = self.env.user.id

        margin = 0

        if self.order_line:
            for sale_order_line in self.order_line:
            	_logger.debug("Margin total: %s", margin)
                margin += sale_order_line.margin * sale_order_line.product_uom_qty

        self.total_margin = margin
