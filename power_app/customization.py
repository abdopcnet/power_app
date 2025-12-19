import frappe
import json

from frappe import _, msgprint, throw, qb
from frappe.utils import flt
from collections import defaultdict


@frappe.whitelist()
def get_item_details(item_code):
    """ return {
            item_code: item_code,
            stock_qty: stock_qty,
            last_selling_rate: last_selling_rate,
            last_purchase_rate: last_purchase_rate,
            warehouse: frm.doc.warehouse || __('Default'),
        };
    """
    """
    Returns basic item information, initialized with zero values for stock
    and rates. This structure is ready to be populated with actual data
    retrieved from the database (e.g., stock query, item rates).
    """
    # Note: The return value must be a dictionary ({}) in Python,
    # using colons (:) to separate keys and values.
    # return {
    #     "item_code": item_code,
    #     "stock_qty": 1110.00,
    #     "last_selling_rate": 10.00,
    #     "last_purchase_rate": 230.00,
    #     "supplier":"supplier_name",
    #     # You can uncomment the line below if you have the 'frm' object available
    #     # in the context, but typically this function runs server-side,
    #     # so frm.doc.warehouse isn't available here unless passed as an argument.
    #     # "warehouse": frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "default_warehouse") or "Default",
    # }
    stock_qty = 0.00
    last_purchase_rate = 0.00
    supplier = ""
    try:
        # Use frappe.get_list, which is the standard server-side function
        # for retrieving a list of Doctype records.
        last_bin_list = frappe.db.get_all(
            "Bin",
            filters={
                "item_code": item_code,
            },
            fields=[
                "name",
                "warehouse",
                "actual_qty",
                "projected_qty",
                "modified"
            ],
            # Order by modified timestamp in descending order to get the "last" record
            order_by="modified desc",
            limit=1
        )

        if last_bin_list:
            # If the list is not empty, return the first (and only) element
            stock_qty = last_bin_list[0].actual_qty
            # return stock_qty
    except Exception as e:
        # Log the error and re-raise it with a user-friendly message
        frappe.log_error(message=str(e), title="Get Last Bin Error")
        frappe.throw(frappe._("Failed to fetch Bin data from the server."),
                     title=frappe._("Database Error"))

    try:
        # Step 1: Find the latest submitted Purchase Invoice that contains the item.
        # We query the parent Doctype (Purchase Invoice) and filter by the child table field.
        last_invoice_data = frappe.db.get_all(
            "Purchase Invoice Item",
            filters={
                "item_code": item_code,
                "parenttype": "Purchase Invoice",
                # The Purchase Invoice must be submitted (docstatus: 1)
                "docstatus": 1
            },
            fields=["rate", "parent"],
            # Sort by creation date descending to get the most recent transaction
            order_by="creation desc",
            limit=1
        )
        if not last_invoice_data:
            last_purchase_rate = 0.00  # No submitted invoice found with this item
            supplier = ""
        else:
            last_purchase_rate = last_invoice_data[0].get(
                "rate") if last_invoice_data else 0.0
            supplier = frappe.db.get_value(
                "Purchase Invoice", last_invoice_data[0].get("parent"), "supplier_name")

    except Exception as e:
        print(e)
        frappe.log_error(message=str(
            e), title="Get Last Purchase Details Error")
        frappe.throw(frappe._("Failed to retrieve last purchase details from the server."),
                     title=frappe._("Database Error"))

    try:
        # Step 1: Find the latest submitted Sales Invoice that contains the item.
        # We query the parent Doctype (Sales Invoice) and filter by the child table field.
        last_invoice_data = frappe.db.get_all(
            "Sales Invoice Item",
            filters={
                "item_code": item_code,
                "docstatus": 1
            },
            fields=["rate", "parent"],
            # Sort by creation date descending to get the most recent transaction
            order_by="creation desc",
            limit=1
        )
        if not last_invoice_data:
            last_selling_rate = 0.00  # No submitted invoice found with this item
        else:
            last_selling_rate = last_invoice_data[0].get(
                "rate") if last_invoice_data else 0.0

    except Exception as e:
        print(e)
        frappe.log_error(message=str(
            e), title="Get Last Purchase Details Error")
        frappe.throw(frappe._("Failed to retrieve last purchase details from the server."),
                     title=frappe._("Database Error"))
    return {
        "item_code": item_code,
        "stock_qty": stock_qty,
        "last_selling_rate": last_selling_rate,
        "last_purchase_rate": last_purchase_rate,
        "supplier": str(supplier),
        # You can uncomment the line below if you have the 'frm' object available
        # in the context, but typically this function runs server-side,
        # so frm.doc.warehouse isn't available here unless passed as an argument.
        # "warehouse": frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "default_warehouse") or "Default",
    }


@frappe.whitelist()
def quotation_update(doc, method):
    # old_doc = doc.get_doc_before_save()
    # if old_doc.custom_quotation_expenses != doc.custom_quotation_expenses:
    total_expenses = 0.00
    for i in doc.custom_quotation_expenses:
        total_expenses += i.amount
    total_item_rate = 0.00
    total_net_item_rate = 0.00
    total_item_amount = 0.00
    total_net_item_amount = 0.00
    for i in doc.items:
        if i.custom_sq_rate == 0:
            i.custom_sq_rate = i.rate
            i.custom_sq_net_rate = i.net_rate
            i.custom_sq_amount = i.amount
            i.custom_sq_net_amount = i.net_amount
            total_item_rate += i.rate
            total_net_item_rate += i.net_rate
            total_item_amount += i.amount
            total_net_item_amount += i.net_amount

        else:
            total_item_rate += i.custom_sq_rate
            total_net_item_rate += i.custom_sq_net_rate
            total_item_amount += i.custom_sq_amount
            total_net_item_amount += i.custom_sq_net_amount
    if (total_item_amount != 0 and total_net_item_amount != 0):
        for i in doc.items:
            i.rate = i.custom_sq_amount + \
                (i.custom_sq_amount/total_item_amount * total_expenses) / i.qty
            i.net_rate = i.custom_sq_net_amount + \
                (i.custom_sq_net_amount/total_net_item_amount * total_expenses) / i.qty
            i.amount = i.rate * i.qty
            i.net_amount = i.net_rate * i.qty
        frappe.db.commit()

    if doc.custom_item_margin:
        for i in doc.items:
            i.rate = i.rate + (i.rate * doc.custom_item_margin/100)
            i.net_rate = i.net_rate + (i.net_rate * doc.custom_item_margin/100)
            i.amount = i.rate * i.qty
            i.net_amount = i.net_rate * i.qty

    if (doc.custom_quotation_expenses or doc.custom_item_margin != 0):
        frappe.msgprint("Item Rate Updated")
    frappe.db.commit()


@frappe.whitelist()
def create_je_from_service_expence(doc, method):
    if doc.custom_service_expense:
        company = doc.company  # Assuming 'company' is a field in your parent DocType

        # 1. Get the default service expense account from the Company master
        # The field name "default_service_expense" must exist in the Company doctype
        default_credit_account = frappe.db.get_value(
            "Company", company, "custom_default_service_expense")

        if not default_credit_account:
            frappe.throw(
                f"Please set the default service expense account in Company: {company}")

        # 2. Group expenses from the child table by their respective expense account
        grouped_expenses = defaultdict(float)
        for row in doc.get("custom_service_expense"):
            expense_account = row.default_account
            amount = flt(row.amount)
            if expense_account and amount > 0:
                grouped_expenses[expense_account] += amount

        if not grouped_expenses:
            return  # No entries to process

        if not doc.custom_service_expense:
            return  # No entries to process

        # 3. Create the Journal Entry document
        je = frappe.new_doc("Journal Entry")
        je.entry_type = "Journal Entry"
        je.company = company
        # Assuming 'posting_date' exists in your parent DocType
        je.posting_date = doc.transaction_date
        # je.cheque_no = doc.name # Optional: use the parent document name as reference
        # je.cheque_date = doc.transaction_date
        je.user_remark = f"Journal Entry for {doc.doctype}: {doc.name}"

        total_amount = 0
        for account, amount in grouped_expenses.items():
            # for row in doc.custom_service_expense:
            # frappe.msgprint(row.amount)

            total_amount += amount
            # Add a Debit entry for the expense account
            je.append("accounts", {
                "account": account,
                "debit_in_account_currency": amount,
                "credit_in_account_currency": 0,
                "is_advance": "No",
                "cost_center": doc.cost_center  # Optional: if you have a cost center field
            })

        # Add a Credit entry for the default service expense account (from Company settings)
        je.append("accounts", {
            "account": default_credit_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": total_amount,
            "is_advance": "No"
        })

        # 4. Save and Submit the Journal Entry
        je.flags.ignore_mandatory = True
        # je.flags.ignore_validate = True
        # je.save(ignore_permissions=True )
        je.insert(ignore_permissions=True)
        je.submit()


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
def check_quotation_linked(doc):
    sq = frappe.get_doc("Supplier Quotation", doc)
    mr = ""
    qoutation_name = ""
    for a in sq.items:
        mr = a.material_request
        if frappe.db.get_value("Material Request", mr, "custom_dc_refrance"):
            qoutation_name = frappe.db.get_value(
                "Material Request", mr, "custom_dc_refrance")
    print(mr)
    print(qoutation_name)
    return qoutation_name


@frappe.whitelist()
def update_quotation_linked(doc, q):
    """
    Clears all existing items in a target Quotation and replaces them
    with items from a specified Supplier Quotation.

    :param target_quotation_name: The Name of the Quotation document to update.
    :param source_supplier_quotation_name: The Name of the Supplier Quotation to copy items from.
    """
    source_supplier_quotation_name = doc
    target_quotation_name = q
    frappe.db.set_value("Quotation",  target_quotation_name, "docstatus", 0)
    if not source_supplier_quotation_name:
        frappe.throw(f"No Supplier Quotation specified.")
        return

    try:
        # 1. Load the target Quotation (the document to be updated)
        target_doc = frappe.get_doc("Quotation", target_quotation_name)

        # 2. Load the source Supplier Quotation
        source_doc = frappe.get_doc(
            "Supplier Quotation", source_supplier_quotation_name)

    except frappe.DoesNotExistError as e:
        frappe.throw(f"Document not found: {e}")
        return

    # 3. Clear existing items in the target Quotation
    target_doc.set("items", [])  # Clears the item child table

    # List of fields to copy from Supplier Quotation Item to Quotation Item
    # We must ensure the field names match the target DocType ('Quotation Item')
    item_fields_to_copy = [
        "item_code", "item_name", "qty", "uom", "rate", "amount",
        "stock_uom", "description", "brand",
        # You may add more fields here if needed, like 'discount_percentage', etc.
    ]

    # 4. Loop through source items and create new rows for the target
    for source_item in source_doc.items:
        new_item = frappe.new_doc(
            "Quotation Item", parent=target_doc, parentfield="items", parenttype="Quotation")

        for field in item_fields_to_copy:
            if hasattr(source_item, field):
                new_item.set(field, getattr(source_item, field))

        # --- CUSTOM MAPPING FOR RATE (Avoids Currency Conversion) ---
        # Map the Supplier Quotation Item's Base Rate (rate in Company's default currency)
        # to the Quotation Item's Rate.
        if hasattr(source_item, "base_rate"):
            new_item.rate = source_item.base_rate
        else:
            # Fallback, though base_rate should always exist on a submitted doc
            new_item.rate = source_item.rate

        # Important: set the parent link fields before appending
        new_item.parent = target_doc.name
        new_item.parenttype = "Quotation"
        new_item.parentfield = "items"

        target_doc.append("items", new_item)

    # ADDED: Add a comment to the Quotation timeline noting the update source
    comment_text = f"Successfully copied {len(source_doc.items)} items from {source_supplier_quotation_name}."
    target_doc.add_comment('Comment', comment_text)

    # 5. Calculate taxes and totals based on new items and save the document
    target_doc.run_method("calculate_taxes_and_totals")
    target_doc.save(ignore_permissions=True)

    # frappe.msgprint(f"Successfully copied {len(source_doc.items)} items from {source_supplier_quotation_name}.")
    return target_doc

    # supplier_quotation = frappe.get_doc("Supplier Quotation" , doc)
    # quotation = frappe.get_doc("Quotation" , sq)
    # # quotation.currency = supplier_quotation.currency
    # # quotation.items = []

    # for i in  quotation.items:
    #     frappe.db.set_value("Quotation Item" , i.name , "docstatus" , 0)

    # frappe.db.set_value("Quotation" , sq , "items" , [] )

    # for row in  supplier_quotation.items:
    #     supplier_quotation.append("items", {
    #                     "item_code": row.item_code,
    #                     "qty": row.quantity,
    #                     "rate": row.rate,
    #                     "request_for_quotation": rfq,
    #                     "uom": item.stock_uom,
    #                     "base_amount": row.quantity * row.rate,
    #                     })

    #     # frappe.db.set_value("Quotation Item" , i.name , "rate" , 90)
    # for i in quotation.custom_quotation_expenses:
    #     frappe.db.set_value("Quotation Expenses" , i.name , "docstatus" , 0)

    # # quotation.items = supplier_quotation.items
    # # quotation.flags.ignore_validate = True
    # # frappe.db.set_value("Quotation" , sq , "docstatus" , 0)
    # frappe.db.set_value("Quotation" , sq , "items" , supplier_quotation.items)
    # quotation.save()
    # frappe.db.commit()
