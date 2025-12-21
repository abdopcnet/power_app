import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_material_request_from_quotation(source, target=None):
    """
    Creates a Material Request from a Quotation.
    Maps item details and sets the Material Request Type to 'Purchase'.

    Args:
        source: Quotation document name
        target: Existing Material Request name (optional)

    Returns:
        Material Request document
    """
    # Define the core mapping settings
    def set_missing_values(source, target):
        # Set the Material Request Type
        target.material_request_type = "Purchase"
        target.company = source.company
        target.custom_created_from_doctype = "Material Request"
        target.custom_quotation_refrence = source.name
        target.run_method("set_missing_values")

    # Execute the mapping process
    # Allow mapping from Draft Quotations (docstatus = 0) for intermediary workflow
    frappe.log_error(
        f"[material_request.py] make_material_request_from_quotation: Creating MR from {source}")
    doc = get_mapped_doc(
        "Quotation",
        source,
        {
            "Quotation": {
                "doctype": "Material Request",
                "validation": {
                    # Allow both Draft (0) and Submitted (1) Quotations
                    "docstatus": ["in", [0, 1]]
                },
                "field_map": {},
            },
            "Quotation Item": {
                "doctype": "Material Request Item",
                "field_map": {
                    "item_code": "item_code",
                    "qty": "qty",
                },
            }
        },
        target,
        set_missing_values
    )

    frappe.log_error(
        f"[material_request.py] make_material_request_from_quotation: Material Request {doc.name} created successfully")
    return doc
