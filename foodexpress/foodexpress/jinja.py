import frappe

def get_customer_receivables(customer, posting_date=frappe.utils.today()):
    report = frappe.call(
        "frappe.desk.query_report.run",
        report_name = "Accounts Receivable",
        filters  = {
            "company": frappe.defaults.get_defaults().get("company"),
            "report_date": posting_date,
            "party_type": "Customer",
            "party": [customer],
            "ageing_based_on": "Due Date",
            "calculate_ageing_with": "Report Date",
            "range":"30, 60, 90, 120",
            "show_sales_person": 1,

        },
        ignore_prepared_report=True,
        add_total_row=False
    )

    result = report.get("result", [])
    
    html = '<table class="table small table-bordered" style="margin: 0; padding: 0; border-collapse: collapse; width: 100%; border-spacing: 0;">\n'

    html += '''<tr>
        <th class="text-center" style="width: 20%;">Bill Date</th>
        <th class="text-center" style="width: 30%;">Invoice/Credit Note Number</th>
        <th class="text-center" style="width: 25%;">Pending Amount</th>
        <th class="text-center" style="width: 25%;">Salesman</th>

    </tr>
    '''
    # Add data rows
    total_outstanding = 0.0
    for row in result:
        if isinstance(row, dict):

            html += f'''<tr>
                <td>{row.get("posting_date")}</td>
                <td>{row.get("voucher_no")}</td>
                <td class="text-right">{frappe.format(row.get("outstanding"), {'fieldtype': 'Currency'})}</td>
                <td>{frappe.db.get_value("Sales Invoice", row.get("voucher_no"), "custom_salesman") or "" if row.get("voucher_type") == "Sales Invoice" else ""}</td>
            </tr>
            '''
            total_outstanding = total_outstanding + row.get("outstanding", 0.0)

    html += f'''<tr>
        <td></td>
        <td class="text-center"><b>Total</b></td>
        <td class="text-right"><b>{frappe.format(total_outstanding, {'fieldtype': 'Currency'})}</b></td>
        <td></td>
    </tr>'''

    # End HTML table
    html += '</table>'

    return html
