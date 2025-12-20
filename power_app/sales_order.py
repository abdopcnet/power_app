import frappe
from frappe import _
from frappe.utils import flt
from collections import defaultdict


def create_je_from_service_expence(doc, method):
    """
    Document event handler for Sales Order on_submit
    Creates Journal Entry automatically when Sales Order with custom service expenses is submitted
    """
    if not hasattr(doc, 'custom_sales_order_service_expenses_table') or not doc.custom_sales_order_service_expenses_table:
        return

    company = doc.company

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
    for row in doc.get("custom_sales_order_service_expenses_table"):
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
    Copies custom_quotation_expenses_table from Quotation to Sales Order custom_sales_order_service_expenses_table
    Uses mapper hook approach - extends without overriding
    """
    # Only process if Sales Order is created from Quotation
    if not doc.quotation_to or doc.quotation_to != "Quotation":
        return

    # Get quotation reference
    quotation_name = None
    for item in doc.items:
        if item.quotation_item:
            # Get parent quotation from quotation_item
            quotation_name = frappe.db.get_value(
                "Quotation Item", item.quotation_item, "parent"
            )
            break

    if not quotation_name:
        return

    # Check if expenses already copied (avoid duplicate on save)
    if hasattr(doc, '_quotation_expenses_copied'):
        return

    # Get quotation expenses
    quotation = frappe.get_doc("Quotation", quotation_name)
    if not hasattr(quotation, 'custom_quotation_expenses_table') or not quotation.custom_quotation_expenses_table:
        return

    # Copy expenses to Sales Order
    if not hasattr(doc, 'custom_sales_order_service_expenses_table'):
        doc.set('custom_sales_order_service_expenses_table', [])

    for expense in quotation.custom_quotation_expenses_table:
        doc.append('custom_sales_order_service_expenses_table', {
            'service_expense_type': expense.service_expense_type,
            'compnay': expense.compnay,
            'default_account': expense.default_account,
            'amount': expense.amount,
        })

    # Mark as copied to avoid duplicates
    doc._quotation_expenses_copied = True
