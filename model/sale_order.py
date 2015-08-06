from openerp import models, fields, api

class sale_order_line(models.Model):
    _inherit = ['sale.order.line']

    margin = fields.Float(compute='_compute_margin_for_line', string="Margin", store=False)
    
    @api.one
    @api.depends('product_id', 'discount')
    def _compute_margin_for_line(self):
        cr = self.env.cr
        uid = self.env.user.id

        if self.product_id.seller_id.id: # Product as sellers
            # get supplier info
            obj = self.pool.get('product.supplierinfo')
            supplier_info = obj.search(cr, uid, [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)])
            if supplier_info and supplier_info[0]:
                right_supplier = obj.browse(cr, uid, supplier_info[0])
                for val in obj.browse(cr, uid, supplier_info):
                    if val.sequence < right_supplier.sequence:
                        right_supplier = val
                pricelist_partnerinfo_obj = self.pool.get('pricelist.partnerinfo')
                pricelist_partnerinfos = pricelist_partnerinfo_obj.search(cr, uid, [('suppinfo_id', '=', right_supplier.id)])
                if pricelist_partnerinfos:
                    computed_cost_price = 0
                    if pricelist_partnerinfo_obj.browse(cr, uid, pricelist_partnerinfos[0]).min_quantity == 0:
                        computed_cost_price = pricelist_partnerinfo_obj.browse(cr, uid, pricelist_partnerinfos[0]).price
                    else:
                        computed_cost_price = pricelist_partnerinfo_obj.browse(cr, uid, pricelist_partnerinfos[0]).price / pricelist_partnerinfo_obj.browse(cr, uid, pricelist_partnerinfos[0]).min_quantity
                    discount = 0
                    if (self.discount):
                        discount = self.discount
                    self.margin = (self.price_unit * (1 - (discount / 100))) - computed_cost_price
                else:
                    self.margin = -1 #error
            else:
                self.margin = -2 #error
        else:
            discount = 0
            if (self.discount):
                discount = self.discount
            self.margin = (self.price_unit * (1 - (discount / 100))) - self.product_id.standard_price

class sale_order(models.Model):
    _inherit = ['sale.order']

    total_margin = fields.Float(compute='_compute_margins', string="Total margin", store=True)

    @api.one
    @api.onchange('order_line','order_line.product_uom_qty','order_line.product_id')
    @api.depends('order_line')
    def _compute_margins(self):
        cr = self.env.cr
        uid = self.env.user.id

        margin = 0

        if self.order_line:
            for sale_order_line in self.order_line:
                margin += sale_order_line.margin * sale_order_line.product_uom_qty

        self.total_margin = margin
