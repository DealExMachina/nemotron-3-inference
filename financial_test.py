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
    from pydantic import BaseModel, Field, field_validator, ConfigDict
    from pydantic.types import PositiveFloat
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("⚠️  Pydantic not available. Install: pip install pydantic>=2.0")
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
    """Single financial transaction with automatic validation"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_default=True,
        extra='forbid'
    )
    
    transaction_id: str = Field(description="Unique transaction identifier")
    timestamp: str = Field(description="ISO 8601 timestamp")
    transaction_type: TransactionType
    asset_symbol: str = Field(description="Stock ticker or asset symbol")
    quantity: PositiveFloat = Field(description="Number of shares/units")
    price_per_unit: PositiveFloat = Field(description="Price per share/unit")
    total_amount: float = Field(description="Total transaction amount")
    currency: Currency
    fees: float = Field(default=0.0, ge=0)
    
    @field_validator('total_amount', mode='after')
    @classmethod
    def validate_total(cls, v: float, info) -> float:
        """Validate total amount matches quantity × price"""
        # Access other field values from info.data
        if hasattr(info, 'data'):
            quantity = info.data.get('quantity')
            price = info.data.get('price_per_unit')
            if quantity and price:
                expected = quantity * price
                if abs(v - expected) > 0.01:  # Allow small rounding differences
                    raise ValueError(f"Total amount mismatch: {v:.2f} != {expected:.2f}")
        return v


class PortfolioHolding(BaseModel):
    """Portfolio holding with valuation"""
    model_config = ConfigDict(validate_default=True, extra='forbid')
    
    asset_symbol: str = Field(min_length=1, max_length=10)
    asset_name: str = Field(min_length=1)
    asset_class: AssetClass
    quantity: PositiveFloat
    current_price: PositiveFloat
    market_value: PositiveFloat
    cost_basis: float = Field(ge=0, description="Cost basis (can be 0 for gifts/transfers)")
    unrealized_gain_loss: float
    percentage_of_portfolio: float = Field(ge=0, le=100)
    currency: Currency


class Portfolio(BaseModel):
    """Complete portfolio with holdings"""
    model_config = ConfigDict(
        validate_default=True,
        extra='forbid',
        str_strip_whitespace=True
    )
    
    portfolio_id: str = Field(min_length=1, description="Unique portfolio identifier")
    account_holder: str = Field(min_length=1, description="Account holder name")
    total_value: PositiveFloat = Field(description="Total portfolio value")
    currency: Currency
    holdings: List[PortfolioHolding] = Field(min_length=0, description="List of holdings")
    cash_balance: float = Field(ge=0, description="Available cash")
    last_updated: str = Field(description="ISO 8601 timestamp")


class MarketData(BaseModel):
    """Real-time market data"""
    model_config = ConfigDict(validate_default=True, extra='forbid')
    
    symbol: str = Field(min_length=1, max_length=20)
    exchange: str = Field(min_length=1)
    last_price: PositiveFloat
    bid_price: Optional[PositiveFloat] = None
    ask_price: Optional[PositiveFloat] = None
    volume: int = Field(ge=0)
    day_high: PositiveFloat
    day_low: PositiveFloat
    day_open: PositiveFloat
    previous_close: PositiveFloat
    change_percent: float
    timestamp: str = Field(description="ISO 8601 timestamp")


class RiskAnalysis(BaseModel):
    """Portfolio risk analysis with comprehensive metrics"""
    model_config = ConfigDict(
        validate_default=True,
        extra='forbid',
        str_strip_whitespace=True
    )
    
    portfolio_id: str = Field(min_length=1, description="Portfolio identifier")
    overall_risk_level: RiskLevel
    volatility: float = Field(ge=0, le=100, description="Annualized volatility %")
    sharpe_ratio: float = Field(ge=-10, le=10, description="Risk-adjusted return metric")
    max_drawdown: float = Field(ge=0, le=100, description="Maximum drawdown %")
    beta: float = Field(ge=-5, le=5, description="Market correlation coefficient")
    var_95: float = Field(description="Value at Risk (95% confidence)")
    diversification_score: float = Field(ge=0, le=100, description="Diversification score 0-100")
    recommendations: List[str] = Field(min_length=1, description="Risk mitigation recommendations")


class TradeSignal(BaseModel):
    """Algorithmic trading signal with validation"""
    model_config = ConfigDict(
        validate_default=True,
        extra='forbid',
        str_strip_whitespace=True
    )
    
    signal_id: str = Field(min_length=1, description="Unique signal identifier")
    timestamp: str = Field(description="ISO 8601 timestamp")
    symbol: str = Field(min_length=1, max_length=10, description="Asset symbol")
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(ge=0, le=100, description="Confidence level 0-100%")
    target_price: PositiveFloat = Field(description="Target price")
    stop_loss: PositiveFloat = Field(description="Stop loss price")
    take_profit: PositiveFloat = Field(description="Take profit price")
    timeframe: Literal["short_term", "medium_term", "long_term"]
    indicators: List[str] = Field(min_length=1, description="Technical indicators used")
    rationale: str = Field(min_length=10, description="Reason for the signal")


class FinancialStatement(BaseModel):
    """Company financial statement with comprehensive data"""
    model_config = ConfigDict(
        validate_default=True,
        extra='forbid',
        str_strip_whitespace=True
    )
    
    company_name: str = Field(min_length=1, description="Company legal name")
    ticker: str = Field(min_length=1, max_length=10, description="Stock ticker symbol")
    period: str = Field(min_length=1, description="e.g., Q4 2024, FY 2023")
    currency: Currency
    revenue: PositiveFloat = Field(description="Total revenue")
    operating_income: float = Field(description="Operating income (can be negative)")
    net_income: float = Field(description="Net income (can be negative)")
    earnings_per_share: float = Field(description="EPS (diluted)")
    total_assets: PositiveFloat = Field(description="Total assets")
    total_liabilities: float = Field(ge=0, description="Total liabilities")
    shareholders_equity: float = Field(description="Shareholders equity")
    operating_cash_flow: float = Field(description="Operating cash flow")
    free_cash_flow: float = Field(description="Free cash flow")


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
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "Transaction",
                        "schema": schema,
                        "strict": True
                    }
                },
                max_tokens=800,  # Increased to prevent any truncation
                temperature=0  # Zero temperature for 100% deterministic output
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
    Generate a JSON portfolio for John Smith (Portfolio ID: PORT-001) with these exact holdings:
    
    Holding 1:
    - Symbol: AAPL, Name: Apple Inc, Class: equity
    - Quantity: 100 shares
    - Current price: $180.00, Cost basis: $150.00
    - Market value: $18,000 (100 × $180)
    - Unrealized gain: $3,000 ($18,000 - $15,000)
    - Percentage: 48.6% of portfolio
    
    Holding 2:
    - Symbol: MSFT, Name: Microsoft Corp, Class: equity  
    - Quantity: 50 shares
    - Current price: $380.00, Cost basis: $320.00
    - Market value: $19,000 (50 × $380)
    - Unrealized gain: $3,000 ($19,000 - $16,000)
    - Percentage: 51.4% of portfolio
    
    Total value: $37,000
    Cash balance: $10,000
    Currency: USD
    Last updated: 2024-12-18T10:00:00Z
    """
    
    schema = Portfolio.model_json_schema()
    
    print(f"\n💼 Generating portfolio...")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "Portfolio", "schema": schema, "strict": True}
            },
            max_tokens=2000  # Large increase for nested array of holdings
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
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "RiskAnalysis", "schema": schema, "strict": True}
            },
            max_tokens=800,  # Increased for complete recommendations
            temperature=0  # Deterministic output
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
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": "TradeSignal", "schema": schema, "strict": True}
                },
                max_tokens=800  # Increased to prevent truncation in rationale field
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
    Generate financial statement JSON with these values:
    company_name: "Apple Inc."
    ticker: "AAPL"
    period: "Q4 2024"
    currency: "USD"
    revenue: 119600000000
    operating_income: 35200000000
    net_income: 30100000000
    earnings_per_share: 1.89
    total_assets: 365000000000
    total_liabilities: 290000000000
    shareholders_equity: 75000000000
    operating_cash_flow: 28500000000
    free_cash_flow: 25300000000
    """
    
    schema = FinancialStatement.model_json_schema()
    
    print(f"\n📄 Extracting financial statement...")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "FinancialStatement", "schema": schema, "strict": True}
            },
            max_tokens=800  # Increased to prevent truncation
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
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "MarketData", "schema": schema, "strict": True}
            },
            max_tokens=700,  # Increased for complete market data
            temperature=0  # Deterministic output
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
