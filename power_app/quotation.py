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
        frappe.log_error(
            f"[quotation.py] get_supplier_quotation_items: No Material Requests found for {quotation_name}")
        return []

    mr_names = [mr.name for mr in mr_list]
    frappe.log_error(
        f"[quotation.py] get_supplier_quotation_items: Found {len(mr_names)} Material Request(s)")

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
        frappe.log_error(
            f"[quotation.py] get_supplier_quotation_items: No Supplier Quotation Items found")
        return []

    # Get supplier names and other details from Supplier Quotation
    for item in sq_items:
        sq_doc = frappe.get_doc("Supplier Quotation",
                                item["supplier_quotation"])
        item["supplier"] = sq_doc.supplier
        item["supplier_name"] = sq_doc.supplier_name
        item["valid_till"] = sq_doc.valid_till
        item["transaction_date"] = sq_doc.transaction_date

    frappe.log_error(
        f"[quotation.py] get_supplier_quotation_items: Returning {len(sq_items)} items")
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
        frappe.log_error(
            f"[quotation.py] get_material_requests_from_quotation: No Material Requests found for {quotation_name}")
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

    frappe.log_error(
        f"[quotation.py] get_material_requests_from_quotation: Returning {len(result)} Material Request(s)")
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
        frappe.log_error(
            f"[quotation.py] add_items_from_supplier_quotations: No items selected")
        frappe.throw(_("No items selected"))

    # Get Quotation document
    quotation = frappe.get_doc("Quotation", quotation_name)
    frappe.log_error(
        f"[quotation.py] add_items_from_supplier_quotations: Processing {len(selected_items)} selected items")

    # Check if quotation is draft
    if quotation.docstatus != 0:
        frappe.throw(_("Can only add items to draft quotations"))

    # Process each selected item
    items_added = 0
    items_updated = 0

    for item_data in selected_items:
        # Get Supplier Quotation Item details
        sq_item = frappe.get_doc(
            "Supplier Quotation Item", item_data.get("item_id"))

        # Get item details from Item master
        item_doc = frappe.get_doc("Item", item_data.get("item_code"))

        # Check if item already exists in quotation
        existing_item = None
        for q_item in quotation.items:
            if q_item.item_code == item_data.get("item_code"):
                existing_item = q_item
                break

        # Prepare item data
        supplier_rate = flt(item_data.get("rate"))
        item_qty = flt(item_data.get("qty"))
        item_uom = item_data.get("uom")
        item_name = item_data.get("item_name")

        if existing_item:
            # Step 1: Copy current rate to custom_original_rate
            current_rate = flt(existing_item.rate) or 0.0
            existing_item.custom_original_rate = current_rate

            # Step 2: Update rate with supplier_rate
            existing_item.rate = supplier_rate
            existing_item.net_rate = supplier_rate
            existing_item.amount = supplier_rate * flt(existing_item.qty)
            existing_item.net_amount = supplier_rate * flt(existing_item.qty)
            existing_item.custom_supplier_quotation = item_data.get(
                "supplier_quotation")

            items_updated += 1
            frappe.log_error(
                f"[quotation.py] add_items_from_supplier_quotations: Updated item {item_data.get('item_code')} - rate: {current_rate} -> {supplier_rate}")
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
                "custom_original_rate": supplier_rate,
            })

            # Calculate amount
            item_row["amount"] = supplier_rate * item_qty
            item_row["net_amount"] = supplier_rate * item_qty

            # Add item to quotation
            quotation.append("items", item_row)
            items_added += 1
            frappe.log_error(
                f"[quotation.py] add_items_from_supplier_quotations: Added item {item_data.get('item_code')} with rate {supplier_rate}")

    # Save quotation
    quotation.save(ignore_permissions=True)
    frappe.log_error(
        f"[quotation.py] add_items_from_supplier_quotations: Saved - Added: {items_added}, Updated: {items_updated}")

    # Prepare message
    message_parts = []
    if items_added > 0:
        message_parts.append(_("Added {0} new item(s)").format(items_added))
    if items_updated > 0:
        message_parts.append(
            _("Updated {0} existing item(s)").format(items_updated))

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


def quotation_validate(doc, method):
    """
    Document event handler for Quotation validate
    Handles expense allocation and item rate calculations

    Runs before save to ensure calculated rates are saved with the document
    """
    from frappe.utils import flt

    total_expenses = 0.00
    if hasattr(doc, 'custom_quotation_expenses_table') and doc.custom_quotation_expenses_table:
        for i in doc.custom_quotation_expenses_table:
            total_expenses += flt(i.amount)
        frappe.log_error(
            f"[quotation.py] quotation_validate: Total expenses: {total_expenses}")

    # Calculate total item amount for expense distribution
    total_item_amount = 0.00
    total_net_item_amount = 0.00
    for i in doc.items:
        total_item_amount += flt(i.amount)
        total_net_item_amount += flt(i.net_amount)

    # Distribute expenses to items
    if total_item_amount != 0 and total_net_item_amount != 0 and total_expenses > 0:
        for i in doc.items:
            expense_per_item = (
                flt(i.amount) / total_item_amount * total_expenses) / flt(i.qty)
            i.rate = flt(i.rate) + expense_per_item
            i.net_rate = flt(i.net_rate) + (flt(i.net_amount) /
                                            total_net_item_amount * total_expenses) / flt(i.qty)
            i.amount = i.rate * flt(i.qty)
            i.net_amount = i.net_rate * flt(i.qty)

    # Apply margin if exists
    if hasattr(doc, 'custom_item_margin') and flt(doc.custom_item_margin) != 0:
        for i in doc.items:
            margin_amount = flt(i.rate) * flt(doc.custom_item_margin) / 100
            i.rate = flt(i.rate) + margin_amount
            i.net_rate = flt(i.net_rate) + (flt(i.net_rate) *
                                            flt(doc.custom_item_margin) / 100)
            i.amount = i.rate * flt(i.qty)
            i.net_amount = i.net_rate * flt(i.qty)

    if (hasattr(doc, 'custom_quotation_expenses_table') and doc.custom_quotation_expenses_table) or \
       (hasattr(doc, 'custom_item_margin') and flt(doc.custom_item_margin) != 0):
        frappe.log_error(
            f"[quotation.py] quotation_validate: Rates updated for {len(doc.items)} items")
        frappe.msgprint(_("Item Rate Updated"))


def quotation_before_submit(doc, method):
    """
    Document event handler for Quotation before_submit
    Allows submitting Quotation only if Approved checkbox is checked
    """
    if not hasattr(doc, 'custom_approved') or not doc.custom_approved:
        frappe.log_error(
            f"[quotation.py] quotation_before_submit: Submission blocked - Approved not checked")
        frappe.throw(
            _("Please check 'Approved' checkbox before submitting the Quotation.")
        )
    frappe.log_error(
        f"[quotation.py] quotation_before_submit: Quotation {doc.name} approved and ready to submit")
