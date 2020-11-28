"""
dict: create required files or put,delete limit files of table
"""

product_template_required = ["type","sale_name","short_name","tmpl_code","import_attribute","xb_product_category_id",
                            "supplier_id","status","brand_id","active","name","min_price","deduction_place",
                            "shelf_time","graphic_description","sale_on_enterprise","sale_line_warn",
                            "purchase_line_warn","tracking","size_description","gsm","main_people_name","sale_ok",
                            "purchase_ok","certificate_description","tag_description","uom_id","categ_id","uom_po_id",
                            "responsible_id","material_name","technology_name","origin_name","create_date","write_date"]

product_product_required = ["default_code","product_tmpl_id","sale_on_enterprise","color","size","weight","price",
                            "unit_price","active","cumulative_quantity","quota","create_date","write_date"]

t_files = {
    "res_partner_required":["is_company","name","mobile","create_date","write_date"],

    "xb_product_category_required":["name","create_date","write_date"],

    "product_product_required":product_product_required,
    "product_attribute_required":["create_variant","name","type","create_date","write_date"],
    "product_attribute_value_required":["attribute_id","name","attribute_category_id","create_date","write_date",'is_custom','active'],
    "xb_product_attribute_category_required":["attribute_id","name","create_date","write_date",'code','active'],
    "product_template_required":product_template_required,
    "product_template_attribute_value_required":["product_attribute_value_id","product_tmpl_id","create_date","write_date"],
    "product_attribute_value_product_product_rel_required":["product_product_id","product_attribute_value_id"],
    "product_template_attribute_line_required":["product_tmpl_id","attribute_id","create_date","write_date"],
    "product_attribute_value_product_template_attribute_line_rel_required":["product_template_attribute_line_id","product_attribute_value_id"],
    "product_supplierinfo_required":["name","sequence","min_qty","price","currency_id","product_tmpl_id","delay","company_id","create_date","write_date"],
    "sale_orders_required":["order_id","book_name","order_date","arrive_date","website_address","purchase_price","price","customer_phone"]
}
