def calculate_financial_health(conn):
    cursor = conn.cursor()
    
    # 1. إجمالي المبيعات (الفواتير)
    cursor.execute("SELECT SUM(total_with_vat) FROM orders WHERE status != 'ملغي'")
    total_sales = cursor.fetchone()[0] or 0
    
    # 2. إجمالي المحصل (الكاش الداخل)
    cursor.execute("SELECT SUM(paid) FROM orders")
    total_collected = cursor.fetchone()[0] or 0
    
    # 3. الديون الخارجية (مبالغ عند العملاء)
    accounts_receivable = total_sales - total_collected
    
    # 4. المصاريف والرواتب
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(base_salary + bonus - deductions) FROM payroll WHERE is_paid = TRUE")
    total_salaries = cursor.fetchone()[0] or 0
    
    # صافي الربح الحقيقي = (المحصل - المصاريف - الرواتب)
    net_profit = total_collected - total_expenses - total_salaries
    
    return {
        "sales": total_sales,
        "collected": total_collected,
        "debts": accounts_receivable,
        "net_profit": net_profit
    }
