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
        return

    company = doc.company

    # Get the default service expense account from the Company master
    default_credit_account = frappe.db.get_value(
        "Company", company, "custom_default_service_expense_account"
    )

    # If not set, use default_expense_account as fallback
    if not default_credit_account:
        default_credit_account = frappe.db.get_value(
            "Company", company, "default_expense_account"
        )

    # If still not set, throw error
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
        return  # No entries to process

    # Create the Journal Entry document
    je = frappe.new_doc("Journal Entry")
    je.entry_type = "Journal Entry"
    je.company = company
    je.posting_date = doc.transaction_date
    je.user_remark = f"Journal Entry for {doc.doctype}: {doc.name}"

    # Link Journal Entry to Sales Order (for Document Links)
    if hasattr(je, 'custom_created_from_doctype'):
        je.custom_created_from_doctype = "Sales Order"
    if hasattr(je, 'custom_sales_order_refrence'):
        je.custom_sales_order_refrence = doc.name

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


def copy_quotation_expenses_to_sales_order(doc, method):
    """
    Document event handler for Sales Order before_save
    Copies custom_service_expense_table from Quotation to Sales Order custom_sales_order_service_expenses_table
    Uses mapper hook approach - extends without overriding
    """
    # Check if expenses already copied (avoid duplicate on save)
    if hasattr(doc, '_quotation_expenses_copied'):
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
        return

    # Get quotation expenses
    try:
        quotation = frappe.get_doc("Quotation", quotation_name)
        if not hasattr(quotation, 'custom_service_expense_table') or not quotation.custom_service_expense_table:
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
    except Exception as e:
        pass


def sales_order_validate(doc, method):
    """
    Document event handler for Sales Order validate
    Cleans up payment_schedule and sets due_date to delivery_date for first row
    """
    from frappe.utils import getdate
    from datetime import timedelta

    if not hasattr(doc, 'payment_schedule') or not doc.payment_schedule:
        return

    # Get posting date (transaction_date for Sales Order)
    posting_date = doc.transaction_date or doc.posting_date
    if not posting_date:
        return

    # Remove empty rows where payment_term is empty
    rows_to_remove = []
    for idx, row in enumerate(doc.payment_schedule):
        if not row.payment_term and not row.payment_amount:
            rows_to_remove.append(idx)

    # Remove rows in reverse order to maintain indices
    for idx in reversed(rows_to_remove):
        doc.payment_schedule.pop(idx)

    # If payment_schedule has rows, set first row due_date (even if payment_term is not set)
    if doc.payment_schedule:
        first_row = doc.payment_schedule[0]

        # Determine due_date: must be after posting_date
        if doc.delivery_date and getdate(doc.delivery_date) >= getdate(posting_date):
            due_date = doc.delivery_date
        else:
            # Use posting_date + 1 day to ensure it's after posting_date
            due_date = getdate(posting_date) + timedelta(days=1)

        # Always ensure due_date is after posting_date
        if getdate(due_date) < getdate(posting_date):
            due_date = getdate(posting_date) + timedelta(days=1)

        # Update due_date for first row (even if payment_term is not set)
        first_row.due_date = due_date
