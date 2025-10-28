class Account:
    def __init__(self, account_id: str, initial_deposit: float) -> None:
        """
        Initialize a new account with the given account ID and initial deposit.
        
        Args:
            account_id (str): Unique identifier for the account.
            initial_deposit (float): Initial amount of funds to deposit into the account.
        """
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
            
        self.account_id = account_id
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.holdings = {}
        self.transactions = []
        
        # Record the initial deposit as a transaction
        self._record_transaction("DEPOSIT", amount=initial_deposit)
    
    def deposit_funds(self, amount: float) -> None:
        """
        Add the specified amount to the account balance.
        
        Args:
            amount (float): Amount to deposit.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
            
        self.balance += amount
        self._record_transaction("DEPOSIT", amount=amount)
    
    def withdraw_funds(self, amount: float) -> bool:
        """
        Withdraw the specified amount from the account if it does not result in a negative balance.
        
        Args:
            amount (float): Amount to withdraw.
            
        Returns:
            bool: True if withdrawal is successful, False otherwise.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
            
        if amount > self.balance:
            return False
            
        self.balance -= amount
        self._record_transaction("WITHDRAWAL", amount=amount)
        return True
    
    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """
        Purchase the specified quantity of shares for the given symbol if sufficient balance is available.
        
        Args:
            symbol (str): Stock symbol to buy.
            quantity (int): Number of shares to buy.
            
        Returns:
            bool: True if purchase is successful, False otherwise.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        symbol = symbol.upper()  # Normalize symbol
        price = self.get_share_price(symbol)
        total_cost = price * quantity
        
        if total_cost > self.balance:
            return False
            
        self.balance -= total_cost
        
        # Update holdings
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
            
        self._record_transaction("BUY", symbol=symbol, quantity=quantity, price=price)
        return True
    
    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """
        Sell the specified quantity of shares for the given symbol if the account holds enough shares.
        
        Args:
            symbol (str): Stock symbol to sell.
            quantity (int): Number of shares to sell.
            
        Returns:
            bool: True if sale is successful, False otherwise.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        symbol = symbol.upper()  # Normalize symbol
        
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            return False
            
        price = self.get_share_price(symbol)
        sale_amount = price * quantity
        
        self.balance += sale_amount
        self.holdings[symbol] -= quantity
        
        # Remove symbol from holdings if quantity becomes 0
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
            
        self._record_transaction("SELL", symbol=symbol, quantity=quantity, price=price)
        return True
    
    def get_portfolio_value(self) -> float:
        """
        Calculate and return the total value of the portfolio.
        
        Returns:
            float: Total value of portfolio (cash + shares).
        """
        portfolio_value = self.balance
        
        for symbol, quantity in self.holdings.items():
            price = self.get_share_price(symbol)
            portfolio_value += price * quantity
            
        return portfolio_value
    
    def get_profit_or_loss(self) -> float:
        """
        Calculate and return the profit or loss relative to the initial deposit.
        
        Returns:
            float: Profit (positive) or loss (negative) amount.
        """
        return self.get_portfolio_value() - self.initial_deposit
    
    def get_holdings(self) -> dict:
        """
        Return a dictionary of the current holdings.
        
        Returns:
            dict: Dictionary containing symbols and quantities held.
        """
        return self.holdings.copy()
    
    def get_transactions(self) -> list:
        """
        Return a list of all transactions that have occurred on the account.
        
        Returns:
            list: List of transaction dictionaries.
        """
        return self.transactions.copy()
    
    def _record_transaction(self, transaction_type: str, **kwargs) -> None:
        """
        Record a transaction in the transaction history.
        
        Args:
            transaction_type (str): Type of transaction (DEPOSIT, WITHDRAWAL, BUY, SELL).
            **kwargs: Additional transaction details.
        """
        import datetime
        
        transaction = {
            "type": transaction_type,
            "timestamp": datetime.datetime.now(),
            **kwargs
        }
        
        self.transactions.append(transaction)
    
    @staticmethod
    def get_share_price(symbol: str) -> float:
        """
        Get the current price for a share symbol. This is a mock implementation.
        
        Args:
            symbol (str): Stock symbol to get the price for.
            
        Returns:
            float: Current price of the share.
            
        Raises:
            ValueError: If the symbol is not recognized.
        """
        prices = {
            "AAPL": 150.0,
            "TSLA": 800.0,
            "GOOGL": 2500.0
        }
        
        symbol = symbol.upper()
        if symbol not in prices:
            raise ValueError(f"Unknown symbol: {symbol}")
            
        return prices[symbol]