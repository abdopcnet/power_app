import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_supplier_quotation_items(quotation_name):
    """
    Get all items from supplier quotations linked to this customer quotation

    Linking method: Via Material Request
    1. Customer Quotation → Material Request (via custom_dc_refrance)
    2. Material Request → Supplier Quotation Items (via material_request field)

    Returns list of supplier quotation items with supplier details
    """
    # Get Material Request linked to Customer Quotation
    mr_list = frappe.get_all(
        "Material Request",
        filters={"custom_dc_refrance": quotation_name},
        fields=["name"]
    )

    if not mr_list:
        return []

    mr_names = [mr.name for mr in mr_list]

    # Get all Supplier Quotation Items linked to these Material Requests
    sq_items = frappe.get_all(
        "Supplier Quotation Item",
        filters={
            "material_request": ["in", mr_names],
            "docstatus": 1
        },
        fields=[
            "name",
            "parent as supplier_quotation",
            "item_code",
            "item_name",
            "qty",
            "uom",
            "rate",
            "amount",
            "material_request"
        ],
        order_by="item_code, rate"
    )

    if not sq_items:
        return []

    # Get supplier names and other details from Supplier Quotation
    for item in sq_items:
        sq_doc = frappe.get_doc("Supplier Quotation",
                                item["supplier_quotation"])
        item["supplier"] = sq_doc.supplier
        item["supplier_name"] = sq_doc.supplier_name
        item["valid_till"] = sq_doc.valid_till
        item["transaction_date"] = sq_doc.transaction_date

    return sq_items


@frappe.whitelist()
def get_material_requests_from_quotation(quotation_name):
    """
    Get all Material Requests linked to Customer Quotation

    Returns list of Material Requests with their details
    """
    # Get Material Requests linked to Customer Quotation
    mr_list = frappe.get_all(
        "Material Request",
        filters={"custom_dc_refrance": quotation_name},
        fields=["name", "transaction_date", "status", "material_request_type"]
    )

    if not mr_list:
        return []

    # Get RFQ for each Material Request
    result = []
    for mr in mr_list:
        # Get Request for Quotation from Material Request Items
        rfq_items = frappe.get_all(
            "Request for Quotation Item",
            filters={"material_request": mr.name},
            fields=["parent"],
            limit=1
        )

        mr_data = {
            "material_request": mr.name,
            "transaction_date": mr.transaction_date,
            "status": mr.status,
            "material_request_type": mr.material_request_type,
            "rfq_name": rfq_items[0].parent if rfq_items else None
        }
        result.append(mr_data)

    return result


def quotation_update(doc, method):
    """
    Document event handler for Quotation on_update
    Handles expense allocation and item rate calculations
    """
    from frappe.utils import flt

    total_expenses = 0.00
    if hasattr(doc, 'custom_quotation_expenses') and doc.custom_quotation_expenses:
        for i in doc.custom_quotation_expenses:
            total_expenses += flt(i.amount)

    total_item_rate = 0.00
    total_net_item_rate = 0.00
    total_item_amount = 0.00
    total_net_item_amount = 0.00

    for i in doc.items:
        if not hasattr(i, 'custom_sq_rate') or i.custom_sq_rate == 0:
            i.custom_sq_rate = i.rate
            i.custom_sq_net_rate = i.net_rate
            i.custom_sq_amount = i.amount
            i.custom_sq_net_amount = i.net_amount
            total_item_rate += flt(i.rate)
            total_net_item_rate += flt(i.net_rate)
            total_item_amount += flt(i.amount)
            total_net_item_amount += flt(i.net_amount)
        else:
            total_item_rate += flt(i.custom_sq_rate)
            total_net_item_rate += flt(i.custom_sq_net_rate)
            total_item_amount += flt(i.custom_sq_amount)
            total_net_item_amount += flt(i.custom_sq_net_amount)

    if total_item_amount != 0 and total_net_item_amount != 0:
        for i in doc.items:
            i.rate = i.custom_sq_amount + \
                (i.custom_sq_amount/total_item_amount * total_expenses) / i.qty
            i.net_rate = i.custom_sq_net_amount + \
                (i.custom_sq_net_amount/total_net_item_amount * total_expenses) / i.qty
            i.amount = i.rate * i.qty
            i.net_amount = i.net_rate * i.qty

    if hasattr(doc, 'custom_item_margin') and doc.custom_item_margin:
        for i in doc.items:
            i.rate = i.rate + (i.rate * flt(doc.custom_item_margin)/100)
            i.net_rate = i.net_rate + \
                (i.net_rate * flt(doc.custom_item_margin)/100)
            i.amount = i.rate * i.qty
            i.net_amount = i.net_rate * i.qty

    if (hasattr(doc, 'custom_quotation_expenses') and doc.custom_quotation_expenses) or \
       (hasattr(doc, 'custom_item_margin') and flt(doc.custom_item_margin) != 0):
        frappe.msgprint(_("Item Rate Updated"))
