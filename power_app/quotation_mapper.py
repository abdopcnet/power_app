# Copyright (c) 2025, Power App and contributors
# For license information, please see license.txt

"""
Override make_sales_order to copy expenses table from Quotation to Sales Order
"""

import frappe
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_sales_order(source_name: str, target_doc=None, args=None):
    """
    Override make_sales_order to copy expenses table
    """
    return _make_sales_order(source_name, target_doc, args=args)


def _make_sales_order(source_name, target_doc=None, ignore_permissions=False, args=None):
    """
    Extended version of _make_sales_order that copies expenses table
    """
    # Import required functions
    if args is None:
        args = {}
    if isinstance(args, str):
        import json
        args = json.loads(args)

    from erpnext.selling.doctype.quotation.quotation import _make_customer, get_ordered_items
    from frappe.utils import flt

    customer = _make_customer(source_name, ignore_permissions)
    ordered_items = get_ordered_items(source_name)

    selected_rows = [x.get("name") for x in frappe.flags.get(
        "args", {}).get("selected_items", [])]

    # 0 qty is accepted, as the qty uncertain for some items
    has_unit_price_items = frappe.db.get_value(
        "Quotation", source_name, "has_unit_price_items")

    def is_unit_price_row(source) -> bool:
        return has_unit_price_items and source.qty == 0

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

        if source.referral_sales_partner:
            target.sales_partner = source.referral_sales_partner
            target.commission_rate = frappe.get_value(
                "Sales Partner", source.referral_sales_partner, "commission_rate"
            )

        target.flags.ignore_permissions = ignore_permissions
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

        # Copy expenses table from Quotation to Sales Order
        if hasattr(source, 'custom_quotation_expenses_table') and source.custom_quotation_expenses_table:
            if not hasattr(target, 'custom_sales_order_service_expenses_table'):
                target.set('custom_sales_order_service_expenses_table', [])

            for expense in source.custom_quotation_expenses_table:
                target.append('custom_sales_order_service_expenses_table', {
                    'service_expense_type': expense.service_expense_type,
                    'company': expense.company,
                    'default_account': expense.default_account,
                    'amount': expense.amount,
                })
            frappe.log_error(
                f"[quotation_mapper.py] _make_sales_order: Copied {len(source.custom_quotation_expenses_table)} expense(s) from Quotation {source_name}")

    def update_item(obj, target, source_parent):
        balance_qty = obj.qty if is_unit_price_row(
            obj) else obj.qty - ordered_items.get(obj.name, 0.0)
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
        3. If no selections: Simple row: Map if adequate qty
        """
        if not ((item.qty > ordered_items.get(item.name, 0.0)) or is_unit_price_row(item)):
            return False

        if not selected_rows:
            return not item.is_alternative

        if selected_rows and (item.is_alternative or item.has_alternative_item):
            return item.name in selected_rows

        # Simple row
        return True

    def select_item(d):
        filtered_items = args.get("filtered_children", [])
        child_filter = d.name in filtered_items if filtered_items else True
        return child_filter

    doclist = get_mapped_doc(
        "Quotation",
        source_name,
        {
            "Quotation": {"doctype": "Sales Order", "validation": {"docstatus": ["=", 1]}},
            "Quotation Item": {
                "doctype": "Sales Order Item",
                "field_map": {"parent": "prevdoc_docname", "name": "quotation_item"},
                "postprocess": update_item,
                "condition": lambda d: can_map_row(d) and select_item(d),
            },
            "Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "reset_value": True},
            "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
            "Payment Schedule": {"doctype": "Payment Schedule", "add_if_empty": True},
        },
        target_doc,
        set_missing_values,
        ignore_permissions=ignore_permissions,
    )

    return doclist
