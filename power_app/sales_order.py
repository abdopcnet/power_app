import frappe
from frappe import _
from frappe.utils import flt
from collections import defaultdict


def create_je_from_service_expence(doc, method):
    """
    Document event handler for Sales Order on_submit
    Creates Journal Entry automatically when Sales Order with custom service expenses is submitted
    """
    expenses_field_candidates = [
        "custom_service_expense_table",
        "custom_sales_order_service_expenses_table",
    ]
    expenses_field = next(
        (fieldname for fieldname in expenses_field_candidates if doc.meta.has_field(fieldname)),
        None,
    )
    expenses_rows = doc.get(expenses_field) if expenses_field else None
    if not expenses_rows:
        frappe.log_error(
            "[sales_order.py] create_je_from_service_expence: No expenses table found")
        return

    company = doc.company
    frappe.log_error(
        f"[sales_order.py] create_je_from_service_expence: Processing expenses for {doc.name}")

    # Get the default service expense account from the Company master
    default_credit_account = frappe.db.get_value(
        "Company", company, "custom_default_service_expense_account"
    )

    if not default_credit_account:
        frappe.throw(
            _("Please set the default service expense account in Company: {0}").format(
                company)
        )

    # Group expenses from the child table by their respective expense account
    grouped_expenses = defaultdict(float)
    for row in expenses_rows:
        expense_account = row.default_account
        amount = flt(row.amount)
        if expense_account and amount > 0:
            grouped_expenses[expense_account] += amount

    if not grouped_expenses:
        frappe.log_error(
            f"[sales_order.py] create_je_from_service_expence: No grouped expenses to process")
        return  # No entries to process

    # Create the Journal Entry document
    frappe.log_error(
        f"[sales_order.py] create_je_from_service_expence: Creating JE with {len(grouped_expenses)} expense account(s)")
    je = frappe.new_doc("Journal Entry")
    je.entry_type = "Journal Entry"
    je.company = company
    je.posting_date = doc.transaction_date
    je.user_remark = f"Journal Entry for {doc.doctype}: {doc.name}"

    total_amount = 0
    for account, amount in grouped_expenses.items():
        total_amount += amount
        # Add a Debit entry for the expense account
        je.append("accounts", {
            "account": account,
            "debit_in_account_currency": amount,
            "credit_in_account_currency": 0,
            "is_advance": "No",
            "cost_center": doc.cost_center if hasattr(doc, 'cost_center') else None
        })

    # Add a Credit entry for the default service expense account (from Company settings)
    je.append("accounts", {
        "account": default_credit_account,
        "debit_in_account_currency": 0,
        "credit_in_account_currency": total_amount,
        "is_advance": "No"
    })

    # Save and Submit the Journal Entry
    je.flags.ignore_mandatory = True
    je.insert(ignore_permissions=True)
    je.submit()
    frappe.log_error(
        f"[sales_order.py] create_je_from_service_expence: Journal Entry {je.name} created and submitted")


def copy_quotation_expenses_to_sales_order(doc, method):
    """
    Document event handler for Sales Order before_save
    Copies custom_service_expense_table from Quotation to Sales Order custom_sales_order_service_expenses_table
    Uses mapper hook approach - extends without overriding
    """
    # Check if expenses already copied (avoid duplicate on save)
    if hasattr(doc, '_quotation_expenses_copied'):
        frappe.log_error(
            f"[sales_order.py] copy_quotation_expenses_to_sales_order: Expenses already copied, skipping")
        return

    # Get quotation reference - try multiple methods
    quotation_name = None

    # Method 1: Check if created from Quotation via quotation_to field
    if hasattr(doc, 'quotation_to') and doc.quotation_to == "Quotation":
        # Get quotation from items
        for item in doc.items:
            if item.quotation_item:
                quotation_name = frappe.db.get_value(
                    "Quotation Item", item.quotation_item, "parent"
                )
                break

    # Method 2: Get quotation from prevdoc_docname (set by mapper)
    if not quotation_name and hasattr(doc, 'prevdoc_docname'):
        quotation_name = doc.prevdoc_docname

    # Method 3: Get quotation from items (quotation_item field)
    if not quotation_name:
        for item in doc.items:
            if item.quotation_item:
                quotation_name = frappe.db.get_value(
                    "Quotation Item", item.quotation_item, "parent"
                )
                if quotation_name:
                    break

    if not quotation_name:
        frappe.log_error(
            f"[sales_order.py] copy_quotation_expenses_to_sales_order: No quotation reference found for {doc.name}")
        return

    frappe.log_error(
        f"[sales_order.py] copy_quotation_expenses_to_sales_order: Processing expenses copy for {doc.name} from Quotation {quotation_name}")

    # Get quotation expenses
    try:
        quotation = frappe.get_doc("Quotation", quotation_name)
        if not hasattr(quotation, 'custom_service_expense_table') or not quotation.custom_service_expense_table:
            frappe.log_error(
                f"[sales_order.py] copy_quotation_expenses_to_sales_order: No expenses in quotation {quotation_name}")
            return

        # Copy expenses to Sales Order
        if not hasattr(doc, 'custom_sales_order_service_expenses_table'):
            doc.set('custom_sales_order_service_expenses_table', [])

        for expense in quotation.custom_service_expense_table:
            doc.append('custom_sales_order_service_expenses_table', {
                'service_expense_type': expense.service_expense_type,
                'company': expense.company,
                'default_account': expense.default_account,
                'amount': expense.amount,
            })

        # Mark as copied to avoid duplicates
        doc._quotation_expenses_copied = True
        frappe.log_error(
            f"[sales_order.py] copy_quotation_expenses_to_sales_order: Copied {len(quotation.custom_service_expense_table)} expense(s) from {quotation_name}")
    except Exception as e:
        frappe.log_error(
            f"[sales_order.py] copy_quotation_expenses_to_sales_order: Error copying expenses: {str(e)}")
