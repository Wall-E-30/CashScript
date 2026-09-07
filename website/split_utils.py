# website/split_utils.py

def simplify_debts(balances):
    """
    Takes a dictionary of net balances and returns the minimum number of transactions to settle them.
    Example Input: {1: -500.0, 2: 200.0, 3: 300.0} (User 1 owes 500, User 2 gets 200, User 3 gets 300)
    """
    debtors = []
    creditors = []
    
    # Separate users into those who owe money (debtors) and those owed money (creditors)
    for user_id, balance in balances.items():
        if balance < -0.01:  # Using 0.01 to avoid floating point precision issues
            debtors.append({'user_id': user_id, 'amount': -balance})
        elif balance > 0.01:
            creditors.append({'user_id': user_id, 'amount': balance})
            
    # Sort both lists by amount descending (largest debts settled first is more efficient)
    debtors.sort(key=lambda x: x['amount'], reverse=True)
    creditors.sort(key=lambda x: x['amount'], reverse=True)
    
    transactions = []
    i, j = 0, 0
    
    # Greedy algorithm: Match the largest debtor with the largest creditor
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        
        # Settle the minimum of what the debtor owes and what the creditor needs
        settle_amount = min(debtor['amount'], creditor['amount'])
        
        transactions.append({
            'from_user': debtor['user_id'],
            'to_user': creditor['user_id'],
            'amount': round(settle_amount, 2)
        })
        
        # Deduct the settled amount
        debtor['amount'] -= settle_amount
        creditor['amount'] -= settle_amount
        
        # Move pointers if fully settled
        if debtor['amount'] < 0.01:
            i += 1
        if creditor['amount'] < 0.01:
            j += 1
            
    return transactions

def calculate_group_balances(group_expenses, expense_splits, settlements):
    """
    Calculates the current net balance for every user in a group based on raw database records.
    """
    balances = {}
    
    # 1. Add money to users who paid for expenses
    for expense in group_expenses:
        balances[expense.paid_by_id] = balances.get(expense.paid_by_id, 0) + expense.amount
        
    # 2. Subtract money from users based on their split shares
    for split in expense_splits:
        balances[split.user_id] = balances.get(split.user_id, 0) - split.owed_amount
        
    # 3. Adjust for settlements (payments already made)
    for settlement in settlements:
        balances[settlement.payer_id] = balances.get(settlement.payer_id, 0) + settlement.amount
        balances[settlement.payee_id] = balances.get(settlement.payee_id, 0) - settlement.amount
        
    return balances