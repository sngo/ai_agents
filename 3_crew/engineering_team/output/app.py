import gradio as gr
from accounts import Account

# Global variable to hold the account instance
account = None

def create_account(account_id, initial_deposit):
    """Create a new account with the given ID and initial deposit."""
    global account
    try:
        initial_deposit = float(initial_deposit)
        account = Account(account_id, initial_deposit)
        return f"Account {account_id} created with initial deposit of ${initial_deposit:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def deposit_funds(amount):
    """Deposit funds into the account."""
    global account
    if account is None:
        return "Error: No account has been created yet."
    try:
        amount = float(amount)
        account.deposit_funds(amount)
        return f"${amount:.2f} deposited successfully. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def withdraw_funds(amount):
    """Withdraw funds from the account."""
    global account
    if account is None:
        return "Error: No account has been created yet."
    try:
        amount = float(amount)
        if account.withdraw_funds(amount):
            return f"${amount:.2f} withdrawn successfully. New balance: ${account.balance:.2f}"
        else:
            return f"Error: Insufficient funds. Current balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def buy_shares(symbol, quantity):
    """Buy shares of the specified symbol."""
    global account
    if account is None:
        return "Error: No account has been created yet."
    try:
        quantity = int(quantity)
        symbol = symbol.upper()
        price = account.get_share_price(symbol)
        
        if account.buy_shares(symbol, quantity):
            return f"Bought {quantity} shares of {symbol} at ${price:.2f} each. New balance: ${account.balance:.2f}"
        else:
            return f"Error: Insufficient funds to buy {quantity} shares of {symbol} at ${price:.2f} each. Current balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def sell_shares(symbol, quantity):
    """Sell shares of the specified symbol."""
    global account
    if account is None:
        return "Error: No account has been created yet."
    try:
        quantity = int(quantity)
        symbol = symbol.upper()
        price = account.get_share_price(symbol)
        
        if account.sell_shares(symbol, quantity):
            return f"Sold {quantity} shares of {symbol} at ${price:.2f} each. New balance: ${account.balance:.2f}"
        else:
            holdings = account.get_holdings()
            if symbol in holdings:
                return f"Error: You only have {holdings[symbol]} shares of {symbol}, cannot sell {quantity}."
            else:
                return f"Error: You don't own any shares of {symbol}."
    except ValueError as e:
        return f"Error: {str(e)}"

def get_portfolio_summary():
    """Get a summary of the account portfolio."""
    global account
    if account is None:
        return "Error: No account has been created yet."
    
    portfolio_value = account.get_portfolio_value()
    profit_loss = account.get_profit_or_loss()
    profit_loss_str = "profit" if profit_loss >= 0 else "loss"
    
    summary = f"Account ID: {account.account_id}\n"
    summary += f"Cash Balance: ${account.balance:.2f}\n"
    summary += f"Initial Deposit: ${account.initial_deposit:.2f}\n"
    summary += f"Total Portfolio Value: ${portfolio_value:.2f}\n"
    summary += f"Profit/Loss: ${abs(profit_loss):.2f} ({profit_loss_str})\n\n"
    
    holdings = account.get_holdings()
    if holdings:
        summary += "Holdings:\n"
        for symbol, quantity in holdings.items():
            price = account.get_share_price(symbol)
            value = price * quantity
            summary += f"  {symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}\n"
    else:
        summary += "No holdings."
    
    return summary

def get_transaction_history():
    """Get the transaction history for the account."""
    global account
    if account is None:
        return "Error: No account has been created yet."
    
    transactions = account.get_transactions()
    if not transactions:
        return "No transactions found."
    
    history = "Transaction History:\n"
    for idx, transaction in enumerate(transactions, 1):
        history += f"{idx}. {transaction['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {transaction['type']}"
        
        if transaction['type'] == "DEPOSIT" or transaction['type'] == "WITHDRAWAL":
            history += f" ${transaction['amount']:.2f}"
        elif transaction['type'] in ["BUY", "SELL"]:
            history += f" {transaction['quantity']} shares of {transaction['symbol']} @ ${transaction['price']:.2f}"
        
        history += "\n"
    
    return history

def get_share_prices():
    """Get the current prices of available shares."""
    symbols = ["AAPL", "TSLA", "GOOGL"]
    prices = ""
    for symbol in symbols:
        try:
            price = Account.get_share_price(symbol)
            prices += f"{symbol}: ${price:.2f}\n"
        except ValueError:
            pass
    return prices

# Create the Gradio interface
with gr.Blocks(title="Trading Platform Demo") as demo:
    gr.Markdown("# Trading Platform Simulation")
    
    with gr.Tab("Account Management"):
        with gr.Group():
            gr.Markdown("### Create Account")
            with gr.Row():
                account_id_input = gr.Textbox(label="Account ID")
                initial_deposit_input = gr.Textbox(label="Initial Deposit ($)")
            create_account_btn = gr.Button("Create Account")
            create_account_output = gr.Textbox(label="Result", interactive=False)
            
            create_account_btn.click(
                fn=create_account,
                inputs=[account_id_input, initial_deposit_input],
                outputs=create_account_output
            )
        
        with gr.Group():
            gr.Markdown("### Deposit/Withdraw Funds")
            with gr.Row():
                deposit_amount = gr.Textbox(label="Amount ($)")
                deposit_btn = gr.Button("Deposit")
                withdraw_btn = gr.Button("Withdraw")
            deposit_withdraw_output = gr.Textbox(label="Result", interactive=False)
            
            deposit_btn.click(
                fn=deposit_funds,
                inputs=deposit_amount,
                outputs=deposit_withdraw_output
            )
            
            withdraw_btn.click(
                fn=withdraw_funds,
                inputs=deposit_amount,
                outputs=deposit_withdraw_output
            )
    
    with gr.Tab("Trading"):
        with gr.Row():
            share_prices = gr.Textbox(label="Available Shares", interactive=False)
            refresh_prices_btn = gr.Button("Refresh Prices")
        
        with gr.Group():
            gr.Markdown("### Buy/Sell Shares")
            with gr.Row():
                symbol_input = gr.Textbox(label="Symbol (e.g., AAPL)")
                quantity_input = gr.Textbox(label="Quantity")
                buy_btn = gr.Button("Buy")
                sell_btn = gr.Button("Sell")
            trade_output = gr.Textbox(label="Result", interactive=False)
            
            buy_btn.click(
                fn=buy_shares,
                inputs=[symbol_input, quantity_input],
                outputs=trade_output
            )
            
            sell_btn.click(
                fn=sell_shares,
                inputs=[symbol_input, quantity_input],
                outputs=trade_output
            )
            
            refresh_prices_btn.click(
                fn=get_share_prices,
                inputs=[],
                outputs=share_prices
            )
    
    with gr.Tab("Portfolio"):
        portfolio_btn = gr.Button("View Portfolio Summary")
        portfolio_output = gr.Textbox(label="Portfolio Summary", interactive=False, lines=15)
        
        portfolio_btn.click(
            fn=get_portfolio_summary,
            inputs=[],
            outputs=portfolio_output
        )
    
    with gr.Tab("Transactions"):
        transactions_btn = gr.Button("View Transaction History")
        transactions_output = gr.Textbox(label="Transaction History", interactive=False, lines=15)
        
        transactions_btn.click(
            fn=get_transaction_history,
            inputs=[],
            outputs=transactions_output
        )

# Initialize share prices
#demo.load(fn=get_share_prices, outputs=share_prices)

if __name__ == "__main__":
    demo.launch()