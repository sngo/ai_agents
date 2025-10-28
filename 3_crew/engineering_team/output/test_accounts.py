import unittest
from unittest.mock import patch, MagicMock
import datetime

from accounts import Account


class TestAccount(unittest.TestCase):
    def test_initialization(self):
        # Test normal initialization
        account = Account("123", 1000.0)
        self.assertEqual(account.account_id, "123")
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(account.initial_deposit, 1000.0)
        self.assertEqual(account.holdings, {})
        self.assertEqual(len(account.transactions), 1)
        
        # Test initialization with negative amount
        with self.assertRaises(ValueError):
            Account("456", -100.0)
    
    def test_deposit_funds(self):
        account = Account("123", 1000.0)
        
        # Test valid deposit
        account.deposit_funds(500.0)
        self.assertEqual(account.balance, 1500.0)
        self.assertEqual(len(account.transactions), 2)
        
        # Test deposit with zero amount
        with self.assertRaises(ValueError):
            account.deposit_funds(0.0)
        
        # Test deposit with negative amount
        with self.assertRaises(ValueError):
            account.deposit_funds(-100.0)
    
    def test_withdraw_funds(self):
        account = Account("123", 1000.0)
        
        # Test valid withdrawal
        result = account.withdraw_funds(500.0)
        self.assertTrue(result)
        self.assertEqual(account.balance, 500.0)
        self.assertEqual(len(account.transactions), 2)
        
        # Test withdrawal with insufficient funds
        result = account.withdraw_funds(1000.0)
        self.assertFalse(result)
        self.assertEqual(account.balance, 500.0)
        self.assertEqual(len(account.transactions), 2)
        
        # Test withdrawal with zero amount
        with self.assertRaises(ValueError):
            account.withdraw_funds(0.0)
        
        # Test withdrawal with negative amount
        with self.assertRaises(ValueError):
            account.withdraw_funds(-100.0)
    
    def test_buy_shares(self):
        account = Account("123", 10000.0)
        
        # Test valid purchase
        result = account.buy_shares("AAPL", 10)
        self.assertTrue(result)
        self.assertEqual(account.balance, 8500.0)  # 10000 - (10 * 150)
        self.assertEqual(account.holdings, {"AAPL": 10})
        self.assertEqual(len(account.transactions), 2)
        
        # Test purchase with insufficient funds
        result = account.buy_shares("TSLA", 20)  # Would cost 16000 (20 * 800)
        self.assertFalse(result)
        self.assertEqual(account.balance, 8500.0)
        self.assertEqual(account.holdings, {"AAPL": 10})
        self.assertEqual(len(account.transactions), 2)
        
        # Test purchase with zero quantity
        with self.assertRaises(ValueError):
            account.buy_shares("AAPL", 0)
        
        # Test purchase with negative quantity
        with self.assertRaises(ValueError):
            account.buy_shares("AAPL", -5)
        
        # Test purchase with unknown symbol
        with self.assertRaises(ValueError):
            account.buy_shares("UNKNOWN", 5)
    
    def test_sell_shares(self):
        account = Account("123", 10000.0)
        account.buy_shares("AAPL", 10)
        
        # Test valid sale
        result = account.sell_shares("AAPL", 5)
        self.assertTrue(result)
        self.assertEqual(account.balance, 9250.0)  # 8500 + (5 * 150)
        self.assertEqual(account.holdings, {"AAPL": 5})
        
        # Test selling all remaining shares
        result = account.sell_shares("AAPL", 5)
        self.assertTrue(result)
        self.assertEqual(account.balance, 10000.0)  # 9250 + (5 * 150)
        self.assertEqual(account.holdings, {})
        
        # Test selling shares we don't have
        result = account.sell_shares("TSLA", 1)
        self.assertFalse(result)
        
        # Test selling more shares than we have
        account.buy_shares("GOOGL", 1)
        result = account.sell_shares("GOOGL", 2)
        self.assertFalse(result)
        
        # Test selling with zero quantity
        with self.assertRaises(ValueError):
            account.sell_shares("GOOGL", 0)
        
        # Test selling with negative quantity
        with self.assertRaises(ValueError):
            account.sell_shares("GOOGL", -1)
    
    def test_get_portfolio_value(self):
        account = Account("123", 10000.0)
        account.buy_shares("AAPL", 10)  # 1500 worth
        account.buy_shares("TSLA", 5)   # 4000 worth
        
        # 10000 - 1500 - 4000 + 1500 + 4000 = 10000
        self.assertEqual(account.get_portfolio_value(), 10000.0)
        
        # Test after price change (simulate with patch)
        with patch('accounts.Account.get_share_price', return_value=200.0):
            # (4500 balance) + (10 * 200) + (5 * 200) = 7500
            self.assertEqual(account.get_portfolio_value(), 7500.0)
    
    def test_get_profit_or_loss(self):
        account = Account("123", 10000.0)
        account.buy_shares("AAPL", 10)  # 1500 worth
        
        # No profit/loss yet as portfolio value equals initial deposit
        self.assertEqual(account.get_profit_or_loss(), 0.0)
        
        # Test with profit (simulate price increase)
        with patch('accounts.Account.get_share_price', return_value=200.0):
            # (8500 balance) + (10 * 200) - 10000 = 500 profit
            self.assertEqual(account.get_profit_or_loss(), 500.0)
        
        # Test with loss (simulate price decrease)
        with patch('accounts.Account.get_share_price', return_value=100.0):
            # (8500 balance) + (10 * 100) - 10000 = -500 loss
            self.assertEqual(account.get_profit_or_loss(), -500.0)
    
    def test_get_holdings(self):
        account = Account("123", 10000.0)
        
        # Test empty holdings
        self.assertEqual(account.get_holdings(), {})
        
        # Test with holdings
        account.buy_shares("AAPL", 10)
        account.buy_shares("TSLA", 5)
        expected_holdings = {"AAPL": 10, "TSLA": 5}
        self.assertEqual(account.get_holdings(), expected_holdings)
        
        # Test that get_holdings returns a copy
        holdings = account.get_holdings()
        holdings["AAPL"] = 20
        self.assertEqual(account.holdings["AAPL"], 10)  # Original unchanged
    
    def test_get_transactions(self):
        account = Account("123", 1000.0)
        
        # Initial deposit transaction
        transactions = account.get_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["type"], "DEPOSIT")
        self.assertEqual(transactions[0]["amount"], 1000.0)
        
        # Add more transactions
        account.deposit_funds(500.0)
        account.withdraw_funds(200.0)
        
        transactions = account.get_transactions()
        self.assertEqual(len(transactions), 3)
        self.assertEqual(transactions[1]["type"], "DEPOSIT")
        self.assertEqual(transactions[1]["amount"], 500.0)
        self.assertEqual(transactions[2]["type"], "WITHDRAWAL")
        self.assertEqual(transactions[2]["amount"], 200.0)
        
        # Test that get_transactions returns a copy
        transactions = account.get_transactions()
        transactions.append({"fake": "transaction"})
        self.assertEqual(len(account.transactions), 3)  # Original unchanged
    
    def test_record_transaction(self):
        account = Account("123", 1000.0)
        
        # Mock datetime.now() to get consistent timestamps
        mock_now = datetime.datetime(2023, 1, 1, 12, 0, 0)
        with patch('datetime.datetime.now', return_value=mock_now):
            
            # Test recording a deposit transaction
            account._record_transaction("TEST", amount=500.0, note="Test transaction")
            
            transactions = account.get_transactions()
            self.assertEqual(len(transactions), 2)
            self.assertEqual(transactions[1]["type"], "TEST")
            self.assertEqual(transactions[1]["amount"], 500.0)
            self.assertEqual(transactions[1]["note"], "Test transaction")
            self.assertEqual(transactions[1]["timestamp"], mock_now)
    
    def test_get_share_price(self):
        # Test valid symbols
        self.assertEqual(Account.get_share_price("AAPL"), 150.0)
        self.assertEqual(Account.get_share_price("TSLA"), 800.0)
        self.assertEqual(Account.get_share_price("GOOGL"), 2500.0)
        
        # Test case insensitivity
        self.assertEqual(Account.get_share_price("aapl"), 150.0)
        
        # Test unknown symbol
        with self.assertRaises(ValueError):
            Account.get_share_price("UNKNOWN")


if __name__ == '__main__':
    unittest.main()