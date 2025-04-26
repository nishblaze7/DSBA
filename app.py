def smarter_nlp_query(question, data):
    subq = question.strip().lower()
    words = subq.split()

    customer_name = None
    division_name = None
    account_owner_name = None

    for word in words:
        match = difflib.get_close_matches(word, [cust.lower() for cust in customer_list], n=1, cutoff=0.7)
        if match:
            for real_name in customer_list:
                if real_name.lower() == match[0]:
                    customer_name = real_name
                    break
            if customer_name:
                break

    for word in words:
        match = difflib.get_close_matches(word, [div.lower() for div in division_list], n=1, cutoff=0.7)
        if match:
            for real_name in division_list:
                if real_name.lower() == match[0]:
                    division_name = real_name
                    break
            if division_name:
                break

    for word in words:
        match = difflib.get_close_matches(word, [acct.lower() for acct in account_owner_list], n=1, cutoff=0.7)
        if match:
            for real_name in account_owner_list:
                if real_name.lower() == match[0]:
                    account_owner_name = real_name
                    break
            if account_owner_name:
                break

    import re
    year_found = None
    current_year = datetime.datetime.now().year

    year_match = re.search(r'20\\d{2}', subq)
    if year_match:
        year_found = int(year_match.group(0))
    elif "last year" in subq:
        year_found = current_year - 1
    elif "this year" in subq:
        year_found = current_year

    month_found = None
    for month_key in month_map.keys():
        if month_key in subq:
            month_found = month_map[month_key]
            break

    if not month_found:
        for word in words:
            month_found = correct_month_typo(word)
            if month_found:
                break

    if customer_name:
        if not month_found or not year_found:
            return "Please specify the month and year when asking about a customer.", None
        result = data[(data['Customer Name'] == customer_name) &
                      (data['Date'].dt.year == year_found) &
                      (data['Date'].dt.month == month_found)]
        if not result.empty:
            revenue = result['Net Revenue'].sum()
            month_name = result.iloc[0]['Month']
            return f"{customer_name} made ${revenue:,.2f} in {month_name} {year_found}.", None
        else:
            return "No matching customer revenue record found.", None

    elif division_name:
        if not year_found:
            return "Please specify the year when asking about a division.", None
        result = data[(data['Division'] == division_name) &
                      (data['Date'].dt.year == year_found)]
        if not result.empty:
            revenue = result['Net Revenue'].sum()
            return f"Division {division_name} generated ${revenue:,.2f} in {year_found}.", None
        else:
            return "No matching division revenue record found.", None

    elif account_owner_name:
        accounts = data[data['Account Owner'] == account_owner_name]

        # Apply month/year filter if mentioned
        if month_found and year_found:
            accounts = accounts[(accounts['Date'].dt.year == year_found) &
                                (accounts['Date'].dt.month == month_found)]

        if accounts.empty:
            return f"No records found for {account_owner_name} in the specified time.", None

        summary = accounts[['Customer Name', 'Month', 'Date', 'Net Revenue']].copy()
        summary['Year'] = summary['Date'].dt.year
        summary = summary[['Customer Name', 'Month', 'Year', 'Net Revenue']]

        unique_accounts = summary['Customer Name'].nunique()
        total_revenue = summary['Net Revenue'].sum()

        if month_found and year_found:
            return (
                f"{account_owner_name} owns {unique_accounts} active accounts in {summary['Month'].iloc[0]} {year_found}. "
                f"Total revenue was ${total_revenue:,.2f}.",
                summary
            )
        else:
            return (
                f"{account_owner_name} owns {unique_accounts} total accounts. Lifetime total revenue: ${total_revenue:,.2f}.",
                summary
            )
    else:
        return "Sorry, I couldn't understand part of the question.", None
