import frappe
from frappe import _


@frappe.whitelist()
def check_quotation_linked(doc):
    """
    Check if Supplier Quotation is linked to Customer Quotation via Material Request

    Returns quotation name if linked, None otherwise
    """
    sq = frappe.get_doc("Supplier Quotation", doc)
    mr = ""
    quotation_name = ""

    for item in sq.items:
        mr = item.material_request
        if mr and frappe.db.get_value("Material Request", mr, "custom_dc_refrance"):
            quotation_name = frappe.db.get_value(
                "Material Request", mr, "custom_dc_refrance"
            )
            break

    if quotation_name:
        frappe.log_error(f"[supplier_quotation.py] check_quotation_linked: Found linked quotation {quotation_name} for {doc}")
    else:
        frappe.log_error(f"[supplier_quotation.py] check_quotation_linked: No linked quotation found for {doc}")
    return quotation_name if quotation_name else None


@frappe.whitelist()
def update_quotation_linked(doc, q):
    """
    Update Customer Quotation with items and rates from Supplier Quotation

    Args:
        doc: Supplier Quotation document name
        q: Customer Quotation document name
    """
    source_supplier_quotation_name = doc
    target_quotation_name = q

    if not source_supplier_quotation_name:
        frappe.log_error(f"[supplier_quotation.py] update_quotation_linked: No Supplier Quotation specified")
        frappe.throw(_("No Supplier Quotation specified."))
        return

    # Set Quotation to Draft status
    frappe.db.set_value("Quotation", target_quotation_name, "docstatus", 0)
    frappe.log_error(f"[supplier_quotation.py] update_quotation_linked: Updating {target_quotation_name} from {source_supplier_quotation_name}")

    try:
        # Load the target Quotation (the document to be updated)
        target_doc = frappe.get_doc("Quotation", target_quotation_name)

        # Load the source Supplier Quotation
        source_doc = frappe.get_doc("Supplier Quotation", source_supplier_quotation_name)

    except frappe.DoesNotExistError as e:
        frappe.throw(_("Document not found: {0}").format(e))
        return

    # Clear existing items in the target Quotation
    target_doc.set("items", [])

    # List of fields to copy from Supplier Quotation Item to Quotation Item
    item_fields_to_copy = [
        "item_code", "item_name", "qty", "uom", "rate", "amount",
        "stock_uom", "description", "brand",
    ]

    # Loop through source items and create new rows for the target
    for source_item in source_doc.items:
        new_item = frappe.new_doc(
            "Quotation Item", parent=target_doc, parentfield="items", parenttype="Quotation"
        )

        for field in item_fields_to_copy:
            if hasattr(source_item, field):
                new_item.set(field, getattr(source_item, field))

        # Map the Supplier Quotation Item's Base Rate to the Quotation Item's Rate
        if hasattr(source_item, "base_rate"):
            new_item.rate = source_item.base_rate
        else:
            new_item.rate = source_item.rate

        # Set the parent link fields before appending
        new_item.parent = target_doc.name
        new_item.parenttype = "Quotation"
        new_item.parentfield = "items"

        target_doc.append("items", new_item)

    # Add a comment to the Quotation timeline noting the update source
    comment_text = f"Successfully copied {len(source_doc.items)} items from {source_supplier_quotation_name}."
    target_doc.add_comment('Comment', comment_text)

    # Calculate taxes and totals based on new items and save the document
    target_doc.run_method("calculate_taxes_and_totals")
    target_doc.save(ignore_permissions=True)
    frappe.log_error(f"[supplier_quotation.py] update_quotation_linked: Updated {target_quotation_name} with {len(source_doc.items)} items")

    return target_doc

