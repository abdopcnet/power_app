# Copyright (c) 2025, Power App and contributors
# For license information, please see license.txt

"""
Override Landed Cost Voucher to support Service Items
This extends ERPNext's Landed Cost Voucher to allow Service Items
in addition to Stock Items and Fixed Assets.
"""

import frappe
from frappe import _
from frappe.query_builder.custom import ConstantColumn
import erpnext
from erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher import (
    LandedCostVoucher as OriginalLandedCostVoucher,
)


class LandedCostVoucher(OriginalLandedCostVoucher):
    """
    Extended Landed Cost Voucher that supports Service Items
    Note: Service Items will be included in the items table, but:
    - update_stock_ledger() automatically skips non-stock items (safe)
    - update_valuation_rate() automatically skips non-stock items (safe)
    - make_gl_entries() will handle service items correctly (safe)
    """

    @frappe.whitelist()
    def get_items_from_purchase_receipts(self):
        """
        Override to include Service Items in addition to Stock Items and Fixed Assets
        """
        self.set("items", [])
        for pr in self.get("purchase_receipts"):
            if pr.receipt_document_type and pr.receipt_document:
                pr_items = get_pr_items_extended(pr)

                for d in pr_items:
                    item = self.append("items")
                    item.item_code = d.item_code
                    item.description = d.description
                    item.qty = d.qty
                    item.rate = d.base_rate
                    item.cost_center = (
                        d.cost_center or erpnext.get_default_cost_center(
                            self.company)
                    )
                    item.amount = d.base_amount
                    item.receipt_document_type = pr.receipt_document_type
                    item.receipt_document = pr.receipt_document
                    item.purchase_receipt_item = d.name
                    item.is_fixed_asset = d.is_fixed_asset


def get_pr_items_extended(purchase_receipt):
    """
    Extended version of get_pr_items that includes Service Items
    Original: Only Stock Items (is_stock_item == 1) or Fixed Assets (is_fixed_asset == 1)
    Extended: Includes Service Items (is_stock_item == 0) as well
    """
    item = frappe.qb.DocType("Item")
    pr_item = frappe.qb.DocType(
        purchase_receipt.receipt_document_type + " Item"
    )
    return (
        frappe.qb.from_(pr_item)
        .inner_join(item)
        .on(item.name == pr_item.item_code)
        .select(
            pr_item.item_code,
            pr_item.description,
            pr_item.qty,
            pr_item.base_rate,
            pr_item.base_amount,
            pr_item.name,
            pr_item.cost_center,
            pr_item.is_fixed_asset,
            ConstantColumn(purchase_receipt.receipt_document_type).as_(
                "receipt_document_type"
            ),
            ConstantColumn(purchase_receipt.receipt_document).as_(
                "receipt_document"
            ),
        )
        .where(
            (pr_item.parent == purchase_receipt.receipt_document)
            & (
                (item.is_stock_item == 1)
                | (item.is_fixed_asset == 1)
                | (item.is_stock_item == 0)  # Include Service Items
            )
        )
        .orderby(pr_item.idx)
        .run(as_dict=True)
    )
