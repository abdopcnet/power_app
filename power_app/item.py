import frappe
from frappe import _


@frappe.whitelist()
def get_item_details(item_code):
    """
    Get item details including stock quantity, last selling rate, last purchase rate, and supplier

    Returns:
        dict: {
            item_code: item_code,
            stock_qty: stock_qty,
            last_selling_rate: last_selling_rate,
            last_purchase_rate: last_purchase_rate,
            supplier: supplier_name
        }
    """
    frappe.log_error(f"[item.py] get_item_details: Fetching details for {item_code}")
    stock_qty = 0.00
    last_purchase_rate = 0.00
    supplier = ""
    last_selling_rate = 0.00

    try:
        # Get stock quantity from Bin
        last_bin_list = frappe.db.get_all(
            "Bin",
            filters={
                "item_code": item_code,
            },
            fields=[
                "name",
                "warehouse",
                "actual_qty",
                "projected_qty",
                "modified"
            ],
            order_by="modified desc",
            limit=1
        )

        if last_bin_list:
            stock_qty = last_bin_list[0].actual_qty
            frappe.log_error(f"[item.py] get_item_details: Stock qty found: {stock_qty}")
    except Exception as e:
        frappe.log_error(f"[item.py] get_item_details: Error fetching Bin data - {str(e)}")
        frappe.throw(
            frappe._("Failed to fetch Bin data from the server."),
            title=frappe._("Database Error")
        )

    try:
        # Get last purchase rate from Purchase Invoice
        last_invoice_data = frappe.db.get_all(
            "Purchase Invoice Item",
            filters={
                "item_code": item_code,
                "parenttype": "Purchase Invoice",
                "docstatus": 1
            },
            fields=["rate", "parent"],
            order_by="creation desc",
            limit=1
        )
        if not last_invoice_data:
            last_purchase_rate = 0.00
            supplier = ""
        else:
            last_purchase_rate = last_invoice_data[0].get("rate") if last_invoice_data else 0.0
            supplier = frappe.db.get_value(
                "Purchase Invoice", last_invoice_data[0].get("parent"), "supplier_name"
            )
            frappe.log_error(f"[item.py] get_item_details: Purchase rate: {last_purchase_rate}, Supplier: {supplier}")

    except Exception as e:
        frappe.log_error(f"[item.py] get_item_details: Error fetching purchase details - {str(e)}")
        frappe.throw(
            frappe._("Failed to retrieve last purchase details from the server."),
            title=frappe._("Database Error")
        )

    try:
        # Get last selling rate from Sales Invoice
        last_sales_invoice_data = frappe.db.get_all(
            "Sales Invoice Item",
            filters={
                "item_code": item_code,
                "parenttype": "Sales Invoice",
                "docstatus": 1
            },
            fields=["rate", "parent"],
            order_by="creation desc",
            limit=1
        )
        if last_sales_invoice_data:
            last_selling_rate = last_sales_invoice_data[0].get("rate") if last_sales_invoice_data else 0.0
            frappe.log_error(f"[item.py] get_item_details: Selling rate: {last_selling_rate}")
    except Exception as e:
        frappe.log_error(f"[item.py] get_item_details: Error fetching selling rate - {str(e)}")
        # Don't throw error for selling rate, just log it
        last_selling_rate = 0.00

    frappe.log_error(f"[item.py] get_item_details: Returning details for {item_code}")
    return {
        "item_code": item_code,
        "stock_qty": stock_qty,
        "last_selling_rate": last_selling_rate,
        "last_purchase_rate": last_purchase_rate,
        "supplier": supplier or ""
    }

