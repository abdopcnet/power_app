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
        if mr and frappe.db.get_value("Material Request", mr, "custom_quotation_refrence"):
            quotation_name = frappe.db.get_value(
                "Material Request", mr, "custom_quotation_refrence"
            )
            break

    return quotation_name if quotation_name else None


@frappe.whitelist()
def get_expense_template_data(template_name):
    """
    Fetch expense template data and return service expenses

    Args:
        template_name: Name of the Expense Template

    Returns:
        List of service expense dictionaries
    """
    if not template_name:
        return []

    try:
        template = frappe.get_doc("Expense Template", template_name)
        expenses = []

        if hasattr(template, 'service_expense') and template.service_expense:
            for expense in template.service_expense:
                expenses.append({
                    'service_expense_type': expense.service_expense_type,
                    'company': expense.company,
                    'default_account': expense.default_account,
                    'amount': expense.amount,
                    'description': expense.description
                })

        return expenses
    except frappe.DoesNotExistError:
        frappe.throw(_("Expense Template {0} not found").format(template_name))
        return []


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
        frappe.throw(_("No Supplier Quotation specified."))
        return

    # Set Quotation to Draft status
    frappe.db.set_value("Quotation", target_quotation_name, "docstatus", 0)

    try:
        # Load the target Quotation (the document to be updated)
        target_doc = frappe.get_doc("Quotation", target_quotation_name)

        # Load the source Supplier Quotation
        source_doc = frappe.get_doc(
            "Supplier Quotation", source_supplier_quotation_name)

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

    # Save the document
    target_doc.save(ignore_permissions=True)

    return target_doc


def supplier_quotation_before_submit(doc, method):
    """
    Document event handler for Supplier Quotation before_submit
    Allows submitting Supplier Quotation only if custom_approve_rfq_technical_specification is checked
    """
    if not hasattr(doc, 'custom_approve_rfq_technical_specification') or not doc.custom_approve_rfq_technical_specification:
        frappe.throw(
            _("Waiting Approve RFQ Technical Specification")
        )
