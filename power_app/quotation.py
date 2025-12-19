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


@frappe.whitelist()
def add_items_from_supplier_quotations(quotation_name, selected_items):
    """
    Add selected items from supplier quotations to customer quotation

    Parameters:
    - quotation_name (str): Customer Quotation name
    - selected_items (list): List of selected items with:
        - item_id: Supplier Quotation Item name
        - supplier_quotation: Supplier Quotation name
        - item_code: Item code
        - rate: Item rate
        - qty: Quantity (optional, will be fetched from SQ Item if not provided)
        - uom: Unit of Measure (optional, will be fetched from SQ Item if not provided)
        - item_name: Item name (optional, will be fetched from SQ Item if not provided)

    Returns:
    - Updated Quotation document
    """
    import json

    # Parse selected_items if it's a string
    if isinstance(selected_items, str):
        selected_items = json.loads(selected_items)

    if not selected_items:
        frappe.throw(_("No items selected"))

    # Get Quotation document
    quotation = frappe.get_doc("Quotation", quotation_name)

    # Check if quotation is draft
    if quotation.docstatus != 0:
        frappe.throw(_("Can only add items to draft quotations"))

    # Process each selected item
    items_added = 0
    items_updated = 0

    for item_data in selected_items:
        # Get Supplier Quotation Item details
        sq_item = frappe.get_doc("Supplier Quotation Item", item_data.get("item_id"))

        # Get item details from Item master
        item_doc = frappe.get_doc("Item", item_data.get("item_code"))

        # Check if item already exists in quotation
        existing_item = None
        for q_item in quotation.items:
            if q_item.item_code == item_data.get("item_code"):
                existing_item = q_item
                break

        # Prepare item data
        supplier_rate = flt(item_data.get("rate")) or flt(sq_item.rate) or 0.0
        item_qty = flt(item_data.get("qty")) or flt(sq_item.qty) or 1.0
        item_uom = item_data.get("uom") or sq_item.uom or item_doc.stock_uom
        item_name = item_data.get("item_name") or sq_item.item_name or item_doc.item_name

        if existing_item:
            # Update existing item: Update rates and custom fields only
            existing_item.rate = supplier_rate
            existing_item.net_rate = supplier_rate
            existing_item.amount = supplier_rate * flt(existing_item.qty)
            existing_item.net_amount = supplier_rate * flt(existing_item.qty)

            # Update custom fields
            existing_item.custom_supplier_quotation = item_data.get("supplier_quotation")
            existing_item.custom_supplier_quotation_item = item_data.get("item_id")
            existing_item.custom_supplier_rate = supplier_rate
            existing_item.custom_original_rate = supplier_rate

            items_updated += 1
        else:
            # Add new item
            item_row = {
                "item_code": item_data.get("item_code"),
                "item_name": item_name,
                "qty": item_qty,
                "uom": item_uom,
                "rate": supplier_rate,
                "net_rate": supplier_rate,
                "description": sq_item.description or item_doc.description,
            }

            # Add custom fields for supplier quotation tracking
            item_row.update({
                "custom_supplier_quotation": item_data.get("supplier_quotation"),
                "custom_supplier_quotation_item": item_data.get("item_id"),
                "custom_supplier_rate": supplier_rate,
                "custom_original_rate": supplier_rate,
            })

            # Calculate amount
            item_row["amount"] = supplier_rate * item_qty
            item_row["net_amount"] = supplier_rate * item_qty

            # Add item to quotation
            quotation.append("items", item_row)
            items_added += 1

    # Save quotation
    quotation.save(ignore_permissions=True)

    # Prepare message
    message_parts = []
    if items_added > 0:
        message_parts.append(_("Added {0} new item(s)").format(items_added))
    if items_updated > 0:
        message_parts.append(_("Updated {0} existing item(s)").format(items_updated))

    if message_parts:
        frappe.msgprint(
            " | ".join(message_parts),
            indicator="green"
        )
    else:
        frappe.msgprint(
            _("No items were processed"),
            indicator="orange"
        )

    return quotation


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
