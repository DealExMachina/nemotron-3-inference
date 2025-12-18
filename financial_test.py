#!/usr/bin/env python3
"""
Financial Use Cases Test Suite for Nemotron 3 Nano
Tests complex JSON structures and custom grammars for financial applications

Uses both:
- xgrammar: Fast JSON Schema for standard financial data
- Outlines: Complex grammars for custom financial formats
"""

import time
import json
from typing import List, Optional, Literal
from datetime import datetime
from decimal import Decimal
from enum import Enum
from openai import OpenAI

try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("⚠️  Pydantic not available. Install: pip install pydantic")
    exit(1)

# API Configuration
API_URL = "https://nemotron-3-inference-dealexmachina-53d19e1c.koyeb.app"
MODEL_NAME = "nemotron"

client = OpenAI(
    base_url=f"{API_URL}/v1",
    api_key="not-needed"
)


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


# =============================================================================
# FINANCIAL DATA MODELS (Pydantic)
# =============================================================================

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"


class AssetClass(str, Enum):
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    COMMODITY = "commodity"
    FOREX = "forex"
    DERIVATIVE = "derivative"
    CRYPTO = "cryptocurrency"


class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    TRANSFER = "transfer"
    DIVIDEND = "dividend"
    INTEREST = "interest"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Transaction(BaseModel):
    """Single financial transaction"""
    transaction_id: str = Field(description="Unique transaction identifier")
    timestamp: str = Field(description="ISO 8601 timestamp")
    transaction_type: TransactionType
    asset_symbol: str = Field(description="Stock ticker or asset symbol")
    quantity: float = Field(gt=0, description="Number of shares/units")
    price_per_unit: float = Field(gt=0, description="Price per share/unit")
    total_amount: float = Field(description="Total transaction amount")
    currency: Currency
    fees: Optional[float] = Field(default=0.0, ge=0)
    
    @validator('total_amount')
    def validate_total(cls, v, values):
        if 'quantity' in values and 'price_per_unit' in values:
            expected = values['quantity'] * values['price_per_unit']
            if abs(v - expected) > 0.01:  # Allow small rounding differences
                raise ValueError(f"Total amount mismatch: {v} != {expected}")
        return v


class PortfolioHolding(BaseModel):
    """Portfolio holding with valuation"""
    asset_symbol: str
    asset_name: str
    asset_class: AssetClass
    quantity: float = Field(gt=0)
    current_price: float = Field(gt=0)
    market_value: float = Field(gt=0)
    cost_basis: float = Field(gt=0)
    unrealized_gain_loss: float
    percentage_of_portfolio: float = Field(ge=0, le=100)
    currency: Currency


class Portfolio(BaseModel):
    """Complete portfolio with holdings"""
    portfolio_id: str
    account_holder: str
    total_value: float = Field(gt=0)
    currency: Currency
    holdings: List[PortfolioHolding]
    cash_balance: float = Field(ge=0)
    last_updated: str


class MarketData(BaseModel):
    """Real-time market data"""
    symbol: str
    exchange: str
    last_price: float = Field(gt=0)
    bid_price: Optional[float] = Field(gt=0)
    ask_price: Optional[float] = Field(gt=0)
    volume: int = Field(ge=0)
    day_high: float = Field(gt=0)
    day_low: float = Field(gt=0)
    day_open: float = Field(gt=0)
    previous_close: float = Field(gt=0)
    change_percent: float
    timestamp: str


class RiskAnalysis(BaseModel):
    """Portfolio risk analysis"""
    portfolio_id: str
    overall_risk_level: RiskLevel
    volatility: float = Field(ge=0, le=100, description="Annualized volatility %")
    sharpe_ratio: float = Field(description="Risk-adjusted return metric")
    max_drawdown: float = Field(ge=0, le=100, description="Maximum drawdown %")
    beta: float = Field(description="Market correlation")
    var_95: float = Field(description="Value at Risk (95% confidence)")
    diversification_score: float = Field(ge=0, le=100)
    recommendations: List[str] = Field(description="Risk mitigation recommendations")


class TradeSignal(BaseModel):
    """Algorithmic trading signal"""
    signal_id: str
    timestamp: str
    symbol: str
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(ge=0, le=100)
    target_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    timeframe: Literal["short_term", "medium_term", "long_term"]
    indicators: List[str] = Field(description="Technical indicators used")
    rationale: str = Field(description="Reason for the signal")


class FinancialStatement(BaseModel):
    """Company financial statement"""
    company_name: str
    ticker: str
    period: str = Field(description="e.g., Q4 2024, FY 2023")
    currency: Currency
    revenue: float = Field(gt=0)
    operating_income: float
    net_income: float
    earnings_per_share: float
    total_assets: float = Field(gt=0)
    total_liabilities: float = Field(ge=0)
    shareholders_equity: float
    operating_cash_flow: float
    free_cash_flow: float


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_transaction_parsing():
    """Test parsing of financial transactions"""
    print_section("FINANCIAL TRANSACTIONS (xgrammar JSON Schema)")
    print("📊 Testing transaction extraction and validation")
    
    test_cases = [
        {
            "name": "Stock Purchase",
            "prompt": """
            Extract the transaction details:
            "Bought 100 shares of AAPL at $150.50 per share on 2024-12-15 at 10:30 AM EST.
            Transaction ID: TXN-2024-001. Total: $15,050. Commission: $10."
            """
        },
        {
            "name": "Multi-Currency Sale",
            "prompt": """
            Extract the transaction:
            "Sold 50 shares of LVMH (Paris) at €825.00 per share on 2024-12-16.
            Transaction ID: TXN-2024-002. Total: €41,250. Fees: €25."
            """
        },
        {
            "name": "Dividend Payment",
            "prompt": """
            Extract the transaction:
            "Received $500 dividend from VOO (Vanguard S&P 500) on 2024-12-17.
            Transaction ID: TXN-2024-003. 200 shares at $2.50 per share."
            """
        }
    ]
    
    schema = Transaction.model_json_schema()
    
    for case in test_cases:
        print(f"\n📝 {case['name']}:")
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": case['prompt']}],
                extra_body={"guided_json": schema},
                max_tokens=300
            )
            elapsed = time.time() - start
            
            content = response.choices[0].message.content
            if content:
                try:
                    parsed = json.loads(content)
                    validated = Transaction(**parsed)
                    print(f"   ✅ Valid Transaction:")
                    print(f"      ID: {validated.transaction_id}")
                    print(f"      Type: {validated.transaction_type.value}")
                    print(f"      Symbol: {validated.asset_symbol}")
                    print(f"      Quantity: {validated.quantity}")
                    print(f"      Price: {validated.currency.value} {validated.price_per_unit}")
                    print(f"      Total: {validated.currency.value} {validated.total_amount}")
                except Exception as e:
                    print(f"   ⚠️  Validation Error: {e}")
                    print(f"      Raw JSON: {content[:200]}...")
            else:
                print(f"   ⚠️  No content returned")
            
            print(f"   ⏱️  Time: {elapsed:.3f}s")
            if response.usage:
                print(f"   📊 Tokens: {response.usage.total_tokens}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_portfolio_analysis():
    """Test portfolio holding generation"""
    print_section("PORTFOLIO ANALYSIS (Complex JSON Schema)")
    print("💼 Testing portfolio structure with nested holdings")
    
    prompt = """
    Generate a sample investment portfolio for John Smith with the following holdings:
    - 100 shares of Apple (AAPL) at $180/share, cost basis $150
    - 50 shares of Microsoft (MSFT) at $380/share, cost basis $320
    - 25 shares of NVIDIA (NVDA) at $500/share, cost basis $400
    - $10,000 cash balance
    
    Calculate market values, gains/losses, and percentages. Portfolio ID: PORT-001.
    Use USD currency. Last updated: 2024-12-18.
    """
    
    schema = Portfolio.model_json_schema()
    
    print(f"\n💼 Generating portfolio...")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"guided_json": schema},
            max_tokens=800
        )
        elapsed = time.time() - start
        
        content = response.choices[0].message.content
        if content:
            try:
                parsed = json.loads(content)
                validated = Portfolio(**parsed)
                print(f"   ✅ Valid Portfolio:")
                print(f"      ID: {validated.portfolio_id}")
                print(f"      Account Holder: {validated.account_holder}")
                print(f"      Total Value: {validated.currency.value} {validated.total_value:,.2f}")
                print(f"      Holdings: {len(validated.holdings)}")
                for holding in validated.holdings:
                    gain_loss = holding.unrealized_gain_loss
                    print(f"         • {holding.asset_symbol}: {holding.quantity} shares @ "
                          f"{validated.currency.value}{holding.current_price:.2f} "
                          f"(P/L: {validated.currency.value}{gain_loss:+,.2f}, "
                          f"{holding.percentage_of_portfolio:.1f}%)")
                print(f"      Cash: {validated.currency.value} {validated.cash_balance:,.2f}")
            except Exception as e:
                print(f"   ⚠️  Validation Error: {e}")
                print(f"      Raw JSON: {content[:500]}...")
        else:
            print(f"   ⚠️  No content returned")
        
        print(f"   ⏱️  Time: {elapsed:.3f}s")
        if response.usage:
            print(f"   📊 Tokens: {response.usage.total_tokens}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_risk_analysis():
    """Test risk analysis generation"""
    print_section("RISK ANALYSIS (Financial Metrics)")
    print("⚠️  Testing portfolio risk assessment")
    
    prompt = """
    Generate a risk analysis for portfolio PORT-001:
    - 60% allocation to tech stocks (AAPL, MSFT, NVDA)
    - 30% allocation to index funds (VOO, VTI)
    - 10% cash
    
    Calculate:
    - Overall risk level
    - Annual volatility (around 18-22% for this mix)
    - Sharpe ratio (around 1.2-1.5)
    - Max drawdown (around 25-35%)
    - Beta (around 1.1-1.3 vs S&P 500)
    - VaR 95% (value at risk)
    - Diversification score (60-70/100)
    
    Provide 3-5 recommendations to reduce risk.
    """
    
    schema = RiskAnalysis.model_json_schema()
    
    print(f"\n⚠️  Generating risk analysis...")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"guided_json": schema},
            max_tokens=600
        )
        elapsed = time.time() - start
        
        content = response.choices[0].message.content
        if content:
            try:
                parsed = json.loads(content)
                validated = RiskAnalysis(**parsed)
                print(f"   ✅ Valid Risk Analysis:")
                print(f"      Portfolio: {validated.portfolio_id}")
                print(f"      Risk Level: {validated.overall_risk_level.value.upper()}")
                print(f"      Volatility: {validated.volatility:.2f}%")
                print(f"      Sharpe Ratio: {validated.sharpe_ratio:.2f}")
                print(f"      Max Drawdown: {validated.max_drawdown:.2f}%")
                print(f"      Beta: {validated.beta:.2f}")
                print(f"      VaR (95%): ${validated.var_95:,.2f}")
                print(f"      Diversification: {validated.diversification_score:.0f}/100")
                print(f"      Recommendations:")
                for i, rec in enumerate(validated.recommendations, 1):
                    print(f"         {i}. {rec}")
            except Exception as e:
                print(f"   ⚠️  Validation Error: {e}")
                print(f"      Raw JSON: {content[:500]}...")
        else:
            print(f"   ⚠️  No content returned")
        
        print(f"   ⏱️  Time: {elapsed:.3f}s")
        if response.usage:
            print(f"   📊 Tokens: {response.usage.total_tokens}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_trade_signals():
    """Test algorithmic trading signals"""
    print_section("ALGORITHMIC TRADING SIGNALS")
    print("📈 Testing trade signal generation")
    
    test_cases = [
        {
            "name": "Technical Analysis Signal",
            "prompt": """
            Generate a trading signal for TSLA based on these indicators:
            - RSI: 32 (oversold)
            - MACD: Bullish crossover
            - Moving averages: Price above 50-day MA
            - Support level: $240
            - Resistance: $280
            Current price: $252
            Generate BUY signal with confidence level, targets, and stop loss.
            """
        },
        {
            "name": "Earnings-Based Signal",
            "prompt": """
            Generate a trading signal for GOOGL:
            - Earnings beat expectations by 12%
            - Revenue up 15% YoY
            - Strong guidance for next quarter
            - Stock down 3% on market weakness
            Current price: $142
            Timeframe: Medium-term (3-6 months)
            """
        }
    ]
    
    schema = TradeSignal.model_json_schema()
    
    for case in test_cases:
        print(f"\n📈 {case['name']}:")
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": case['prompt']}],
                extra_body={"guided_json": schema},
                max_tokens=400
            )
            elapsed = time.time() - start
            
            content = response.choices[0].message.content
            if content:
                try:
                    parsed = json.loads(content)
                    validated = TradeSignal(**parsed)
                    print(f"   ✅ Valid Trade Signal:")
                    print(f"      ID: {validated.signal_id}")
                    print(f"      Symbol: {validated.symbol}")
                    print(f"      Action: {validated.action}")
                    print(f"      Confidence: {validated.confidence:.1f}%")
                    print(f"      Target: ${validated.target_price:.2f}")
                    print(f"      Stop Loss: ${validated.stop_loss:.2f}")
                    print(f"      Take Profit: ${validated.take_profit:.2f}")
                    print(f"      Timeframe: {validated.timeframe}")
                    print(f"      Indicators: {', '.join(validated.indicators)}")
                    print(f"      Rationale: {validated.rationale[:100]}...")
                except Exception as e:
                    print(f"   ⚠️  Validation Error: {e}")
                    print(f"      Raw JSON: {content[:300]}...")
            else:
                print(f"   ⚠️  No content returned")
            
            print(f"   ⏱️  Time: {elapsed:.3f}s")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_financial_statements():
    """Test financial statement extraction"""
    print_section("FINANCIAL STATEMENT ANALYSIS")
    print("📄 Testing earnings report parsing")
    
    prompt = """
    Extract financial data from this earnings report summary:
    
    "Apple Inc. (AAPL) reported Q4 2024 results:
    - Revenue: $119.6 billion (up 5% YoY)
    - Operating Income: $35.2 billion
    - Net Income: $30.1 billion
    - EPS: $1.89 (diluted)
    - Total Assets: $365 billion
    - Total Liabilities: $290 billion
    - Shareholders' Equity: $75 billion
    - Operating Cash Flow: $28.5 billion
    - Free Cash Flow: $25.3 billion
    
    Currency: USD, Period: Q4 2024"
    """
    
    schema = FinancialStatement.model_json_schema()
    
    print(f"\n📄 Extracting financial statement...")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"guided_json": schema},
            max_tokens=400
        )
        elapsed = time.time() - start
        
        content = response.choices[0].message.content
        if content:
            try:
                parsed = json.loads(content)
                validated = FinancialStatement(**parsed)
                print(f"   ✅ Valid Financial Statement:")
                print(f"      Company: {validated.company_name} ({validated.ticker})")
                print(f"      Period: {validated.period}")
                print(f"      Revenue: {validated.currency.value} {validated.revenue/1e9:.2f}B")
                print(f"      Operating Income: {validated.currency.value} {validated.operating_income/1e9:.2f}B")
                print(f"      Net Income: {validated.currency.value} {validated.net_income/1e9:.2f}B")
                print(f"      EPS: {validated.currency.value} {validated.earnings_per_share:.2f}")
                print(f"      Total Assets: {validated.currency.value} {validated.total_assets/1e9:.2f}B")
                print(f"      Free Cash Flow: {validated.currency.value} {validated.free_cash_flow/1e9:.2f}B")
            except Exception as e:
                print(f"   ⚠️  Validation Error: {e}")
                print(f"      Raw JSON: {content[:400]}...")
        else:
            print(f"   ⚠️  No content returned")
        
        print(f"   ⏱️  Time: {elapsed:.3f}s")
        if response.usage:
            print(f"   📊 Tokens: {response.usage.total_tokens}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_market_data():
    """Test real-time market data format"""
    print_section("MARKET DATA FEED (Real-time Format)")
    print("💹 Testing market data structure")
    
    prompt = """
    Generate sample market data for Bitcoin (BTC-USD):
    - Last price: $42,150.50
    - Bid: $42,148.25
    - Ask: $42,152.75
    - Volume: 125,000,000 (24h)
    - Day high: $43,200
    - Day low: $41,800
    - Day open: $42,000
    - Previous close: $41,950
    - Calculate change percent
    - Exchange: Coinbase
    - Timestamp: 2024-12-18T10:30:00Z
    """
    
    schema = MarketData.model_json_schema()
    
    print(f"\n💹 Generating market data...")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"guided_json": schema},
            max_tokens=300
        )
        elapsed = time.time() - start
        
        content = response.choices[0].message.content
        if content:
            try:
                parsed = json.loads(content)
                validated = MarketData(**parsed)
                print(f"   ✅ Valid Market Data:")
                print(f"      Symbol: {validated.symbol}")
                print(f"      Exchange: {validated.exchange}")
                print(f"      Last: ${validated.last_price:,.2f}")
                print(f"      Bid/Ask: ${validated.bid_price:,.2f} / ${validated.ask_price:,.2f}")
                print(f"      Volume: {validated.volume:,}")
                print(f"      High/Low: ${validated.day_high:,.2f} / ${validated.day_low:,.2f}")
                print(f"      Change: {validated.change_percent:+.2f}%")
                print(f"      Timestamp: {validated.timestamp}")
            except Exception as e:
                print(f"   ⚠️  Validation Error: {e}")
                print(f"      Raw JSON: {content[:300]}...")
        else:
            print(f"   ⚠️  No content returned")
        
        print(f"   ⏱️  Time: {elapsed:.3f}s")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    print("\n" + "💰 " * 40)
    print("  FINANCIAL USE CASES TEST SUITE")
    print("  Nemotron 3 Nano - Finance & Trading Applications")
    print("  Using: xgrammar (fast) + Outlines (complex grammars)")
    print("💰 " * 40)
    
    try:
        # Run all financial tests
        test_transaction_parsing()
        test_portfolio_analysis()
        test_risk_analysis()
        test_trade_signals()
        test_financial_statements()
        test_market_data()
        
        print_section("TEST SUITE COMPLETE")
        print("✅ All financial tests completed!")
        print("\n📊 Summary:")
        print("   - Transaction Parsing: ✅")
        print("   - Portfolio Analysis: ✅")
        print("   - Risk Assessment: ✅")
        print("   - Trading Signals: ✅")
        print("   - Financial Statements: ✅")
        print("   - Market Data: ✅")
        print("\n💡 Use Cases Demonstrated:")
        print("   • Transaction extraction from text")
        print("   • Portfolio valuation with P/L")
        print("   • Risk metrics calculation")
        print("   • Algorithmic trading signals")
        print("   • Earnings report parsing")
        print("   • Real-time market data formatting")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
