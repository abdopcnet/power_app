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

    # ============================================
    # Function 1: Copy items and prices
    # Fields: item_code, qty, rate, custom_supplier_quotation_item_rate,
    #        custom_supplier_quotation, margin_type
    # ============================================
    # Loop through source items and create new rows for the target
    for source_item in source_doc.items:
        new_item = frappe.new_doc(
            "Quotation Item", parent=target_doc, parentfield="items", parenttype="Quotation"
        )

        # Copy required fields: item_code, qty, rate
        if hasattr(source_item, "item_code"):
            new_item.item_code = source_item.item_code
        if hasattr(source_item, "qty"):
            new_item.qty = source_item.qty
        if hasattr(source_item, "rate"):
            new_item.rate = source_item.rate
        elif hasattr(source_item, "base_rate"):
            new_item.rate = source_item.base_rate

        # Copy custom fields: custom_supplier_quotation_item_rate, custom_supplier_quotation
        if hasattr(source_item, "custom_supplier_quotation_item_rate"):
            new_item.custom_supplier_quotation_item_rate = source_item.custom_supplier_quotation_item_rate
        if hasattr(source_item, "custom_supplier_quotation"):
            new_item.custom_supplier_quotation = source_item.custom_supplier_quotation
        else:
            # If custom_supplier_quotation doesn't exist in source item, set it to the Supplier Quotation name
            new_item.custom_supplier_quotation = source_supplier_quotation_name

        # Copy margin_type if it exists in source
        if hasattr(source_item, "margin_type"):
            new_item.margin_type = source_item.margin_type

        # Set the parent link fields before appending
        new_item.parent = target_doc.name
        new_item.parenttype = "Quotation"
        new_item.parentfield = "items"

        target_doc.append("items", new_item)

    # ============================================
    # Function 2: Copy expenses table
    # Copy custom_service_expense_table from Supplier Quotation to Quotation
    # ============================================
    if hasattr(source_doc, 'custom_service_expense_table') and source_doc.custom_service_expense_table:
        # Clear existing expenses in target Quotation
        if hasattr(target_doc, 'custom_service_expense_table'):
            target_doc.set('custom_service_expense_table', [])

        # Copy expenses from Supplier Quotation to Quotation
        for expense in source_doc.custom_service_expense_table:
            target_doc.append('custom_service_expense_table', {
                'service_expense_type': expense.service_expense_type,
                'company': expense.company,
                'default_account': expense.default_account,
                'amount': expense.amount,
                'description': expense.description
            })

    # Copy custom_expense_template from Supplier Quotation to Quotation
    if hasattr(source_doc, 'custom_expense_template') and source_doc.custom_expense_template:
        target_doc.custom_expense_template = source_doc.custom_expense_template

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
