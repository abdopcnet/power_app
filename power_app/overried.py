# Copyright (c) 2025, Hadeel Milad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate

from erpnext.controllers.selling_controller import SellingController
# from erpnext.crm.doctype.lead.lead import _make_customer

form_grid_templates = {"items": "templates/form_grid/item_grid.html"}

@frappe.whitelist()
def make_sales_order(source_name: str, target_doc=None):
	if not frappe.db.get_singles_value(
		"Selling Settings", "allow_sales_order_creation_for_expired_quotation"
	):
		quotation = frappe.db.get_value(
			"Quotation", source_name, ["transaction_date", "valid_till"], as_dict=1
		)
		if quotation.valid_till and (
			quotation.valid_till < quotation.transaction_date or quotation.valid_till < getdate(nowdate())
		):
			frappe.throw(_("Validity period of this quotation has ended."))

	return _make_sales_order(source_name, target_doc)


def _make_sales_order(source_name, target_doc=None, ignore_permissions=False):
	customer = _make_customer(source_name, ignore_permissions)
	ordered_items = frappe._dict(
		frappe.db.get_all(
			"Sales Order Item",
			{"prevdoc_docname": source_name, "docstatus": 1},
			["item_code", "sum(qty)"],
			group_by="item_code",
			as_list=1,
		)
	)

	selected_rows = [x.get("name") for x in frappe.flags.get("args", {}).get("selected_items", [])]

	def set_missing_values(source, target):
		if customer:
			target.customer = customer.name
			target.customer_name = customer.customer_name

			# sales team
			if not target.get("sales_team"):
				for d in customer.get("sales_team") or []:
					target.append(
						"sales_team",
						{
							"sales_person": d.sales_person,
							"allocated_percentage": d.allocated_percentage or None,
							"commission_rate": d.commission_rate,
						},
					)

			# sales team
			if not target.get("custom_quotation_expenses"):
				for d in customer.get("custom_quotation_expenses") or []:
					target.append(
						"custom_quotation_expenses",
						{
							"sales_person": d.sales_person,
							"allocated_percentage": d.allocated_percentage or None,
							"commission_rate": d.commission_rate,
						},
					)

		if source.referral_sales_partner:
			target.sales_partner = source.referral_sales_partner
			target.commission_rate = frappe.get_value(
				"Sales Partner", source.referral_sales_partner, "commission_rate"
			)

		target.flags.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		balance_qty = obj.qty - ordered_items.get(obj.item_code, 0.0)
		target.qty = balance_qty if balance_qty > 0 else 0
		target.stock_qty = flt(target.qty) * flt(obj.conversion_factor)

		if obj.against_blanket_order:
			target.against_blanket_order = obj.against_blanket_order
			target.blanket_order = obj.blanket_order
			target.blanket_order_rate = obj.blanket_order_rate

	def can_map_row(item) -> bool:
		"""
		Row mapping from Quotation to Sales order:
		1. If no selections, map all non-alternative rows (that sum up to the grand total)
		2. If selections: Is Alternative Item/Has Alternative Item: Map if selected and adequate qty
		3. If selections: Simple row: Map if adequate qty
		"""
		balance_qty = item.qty - ordered_items.get(item.item_code, 0.0)
		if balance_qty <= 0:
			return False

		has_qty = balance_qty

		if not selected_rows:
			return not item.is_alternative

		if selected_rows and (item.is_alternative or item.has_alternative_item):
			return (item.name in selected_rows) and has_qty

		# Simple row
		return has_qty

	doclist = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {"doctype": "Sales Order", "validation": {"docstatus": ["=", 1]}},
			"Quotation Item": {
				"doctype": "Sales Order Item",
				"field_map": {"parent": "prevdoc_docname", "name": "quotation_item"},
				"postprocess": update_item,
				"condition": can_map_row,
			},
            "Quotation Item": {
				"doctype": "Sales Order Item",
				"field_map": {"parent": "prevdoc_docname", "name": "quotation_item"},
				"postprocess": update_item,
				"condition": can_map_row,
			},
			"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "reset_value": True},
			"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
			"Payment Schedule": {"doctype": "Payment Schedule", "add_if_empty": True},
			"Service Expense": {"doctype": "Service Expense", "add_if_empty": True},
		},
		target_doc,
		set_missing_values,
		ignore_permissions=ignore_permissions,
	)

	return doclist


def _make_customer(source_name, ignore_permissions=False):
	quotation = frappe.db.get_value(
		"Quotation",
		source_name,
		["order_type", "quotation_to", "party_name", "customer_name"],
		as_dict=1,
	)

	if quotation.quotation_to == "Customer":
		return frappe.get_doc("Customer", quotation.party_name)

	# Check if a Customer already exists for the Lead or Prospect.
	existing_customer = None
	if quotation.quotation_to == "Lead":
		existing_customer = frappe.db.get_value("Customer", {"lead_name": quotation.party_name})
	elif quotation.quotation_to == "Prospect":
		existing_customer = frappe.db.get_value("Customer", {"prospect_name": quotation.party_name})

	if existing_customer:
		return frappe.get_doc("Customer", existing_customer)

	# If no Customer exists, create a new Customer or Prospect.
	if quotation.quotation_to == "Lead":
		return create_customer_from_lead(quotation.party_name, ignore_permissions=ignore_permissions)
	elif quotation.quotation_to == "Prospect":
		return create_customer_from_prospect(quotation.party_name, ignore_permissions=ignore_permissions)

	return None

