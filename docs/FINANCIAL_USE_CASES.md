# Financial Use Cases - Structured Generation

**Model:** NVIDIA Nemotron-3-Nano-30B-A3B-FP8  
**Backends:** xgrammar (fast) + Outlines (complex)  
**Date:** December 18, 2025

---

## 🎯 Why Both Backends for Finance?

| Use Case | Backend | Reason |
|----------|---------|--------|
| **Transaction parsing** | **xgrammar** | Fast, high-volume processing |
| **Risk calculations** | **xgrammar** | Standard JSON Schema |
| **Custom formats** | **Outlines** | SWIFT messages, FIX protocol |
| **Compliance docs** | **Outlines** | Complex validation rules |
| **Market data** | **xgrammar** | Real-time speed critical |
| **Algorithmic trading** | **xgrammar** | Low-latency signals |

---

## 📊 Financial Data Structures

### 1. **Transaction Processing**

**Schema:**
```python
class Transaction(BaseModel):
    transaction_id: str
    timestamp: str  # ISO 8601
    transaction_type: Literal["buy", "sell", "transfer", "dividend"]
    asset_symbol: str
    quantity: float
    price_per_unit: float
    total_amount: float
    currency: Literal["USD", "EUR", "GBP", "JPY"]
    fees: float = 0.0
```

**Use Cases:**
- 💳 **Trade confirmation parsing**
- 📄 **Broker statement extraction**
- 🧾 **Expense tracking**
- 📊 **Tax reporting automation**

**Example:**
```python
prompt = """
Extract: "Bought 100 AAPL @ $150.50, ID: TXN-001, Fee: $10"
"""

response = client.chat.completions.create(
    model="nemotron",
    messages=[{"role": "user", "content": prompt}],
    extra_body={"guided_json": Transaction.model_json_schema()}
)
# Returns: {"transaction_id": "TXN-001", "asset_symbol": "AAPL", ...}
```

---

### 2. **Portfolio Management**

**Schema:**
```python
class Portfolio(BaseModel):
    portfolio_id: str
    total_value: float
    holdings: List[PortfolioHolding]
    cash_balance: float
    
class PortfolioHolding(BaseModel):
    asset_symbol: str
    quantity: float
    current_price: float
    market_value: float
    unrealized_gain_loss: float
    percentage_of_portfolio: float
```

**Use Cases:**
- 📊 **Portfolio rebalancing**
- 💼 **Asset allocation tracking**
- 📈 **Performance monitoring**
- 🎯 **Goal-based investing**

**Validation:**
```python
@validator('total_amount')
def validate_total(cls, v, values):
    # Ensures quantity × price = total
    expected = values['quantity'] * values['price_per_unit']
    if abs(v - expected) > 0.01:
        raise ValueError(f"Calculation error")
    return v
```

---

### 3. **Risk Analysis**

**Schema:**
```python
class RiskAnalysis(BaseModel):
    overall_risk_level: Literal["low", "medium", "high", "very_high"]
    volatility: float  # Annual volatility %
    sharpe_ratio: float  # Risk-adjusted return
    max_drawdown: float  # Maximum loss %
    beta: float  # Market correlation
    var_95: float  # Value at Risk (95%)
    diversification_score: float  # 0-100
    recommendations: List[str]
```

**Use Cases:**
- ⚠️ **Portfolio risk assessment**
- 📉 **Stress testing**
- 🎯 **Risk-adjusted returns**
- 💡 **Rebalancing recommendations**

**Calculations:**
```python
# Volatility: Standard deviation of returns
# Sharpe Ratio: (Return - Risk-free rate) / Volatility
# Beta: Correlation with market
# VaR: Maximum loss at confidence level
```

---

### 4. **Trading Signals**

**Schema:**
```python
class TradeSignal(BaseModel):
    signal_id: str
    symbol: str
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float  # 0-100
    target_price: float
    stop_loss: float
    take_profit: float
    timeframe: Literal["short_term", "medium_term", "long_term"]
    indicators: List[str]
    rationale: str
```

**Use Cases:**
- 📈 **Technical analysis**
- 🤖 **Algorithmic trading**
- 💹 **Swing trading signals**
- 📊 **Momentum strategies**

**Indicators:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (MA, EMA)
- Support/Resistance levels

---

### 5. **Financial Statements**

**Schema:**
```python
class FinancialStatement(BaseModel):
    company_name: str
    ticker: str
    period: str  # "Q4 2024", "FY 2023"
    revenue: float
    operating_income: float
    net_income: float
    earnings_per_share: float
    total_assets: float
    total_liabilities: float
    shareholders_equity: float
    operating_cash_flow: float
    free_cash_flow: float
```

**Use Cases:**
- 📄 **Earnings report parsing**
- 📊 **Fundamental analysis**
- 💰 **Valuation models**
- 🔍 **Financial health screening**

**Metrics:**
- **P/E Ratio** = Market Cap / Net Income
- **ROE** = Net Income / Shareholders' Equity
- **Debt-to-Equity** = Total Liabilities / Shareholders' Equity
- **Free Cash Flow** = Operating CF - CapEx

---

### 6. **Market Data Feeds**

**Schema:**
```python
class MarketData(BaseModel):
    symbol: str
    exchange: str
    last_price: float
    bid_price: float
    ask_price: float
    volume: int
    day_high: float
    day_low: float
    change_percent: float
    timestamp: str  # ISO 8601
```

**Use Cases:**
- 💹 **Real-time price feeds**
- 📊 **Order book data**
- ⚡ **High-frequency trading**
- 📈 **Market surveillance**

---

## 🏗️ Complex Financial Formats (Outlines)

### SWIFT Messages

```python
# Use Outlines for SWIFT MT103 (international wire)
from outlines import models, generate

swift_grammar = """
    ?start: mt103
    mt103: header "\\n" basic_header "\\n" text_block
    header: "{1:" sender_bic "}"
    basic_header: "{2:I" message_type sender_bic "}"
    text_block: "{4:" fields+ "}"
    ...
"""

model = outlines.models.from_vllm(vllm_model)
generator = generate.regex(model, swift_grammar)
result = generator("Generate SWIFT MT103 for $10,000 to Deutsche Bank")
```

### FIX Protocol

```python
# Financial Information eXchange protocol
fix_schema = {
    "type": "object",
    "properties": {
        "MsgType": {"enum": ["D", "8", "9"]},  # NewOrder, Execution, Cancel
        "ClOrdID": {"pattern": "^[A-Z0-9]{8}$"},
        "Symbol": {"type": "string"},
        "Side": {"enum": ["1", "2"]},  # Buy=1, Sell=2
        "OrderQty": {"type": "number"},
        "Price": {"type": "number"}
    }
}
```

### Custom Regulatory Formats

```python
# MiFID II transaction reporting
mifid_schema = {
    "type": "object",
    "properties": {
        "venue_identifier": {"pattern": "^[A-Z]{4}$"},
        "instrument_id": {"pattern": "^[A-Z]{12}$"},
        "price_currency": {"enum": ["EUR", "USD", "GBP"]},
        "quantity_currency": {"enum": ["EUR", "USD", "GBP"]},
        "price_notation": {"enum": ["PERC", "MONE", "YIEL"]},
        ...
    }
}
```

---

## 💼 Real-World Scenarios

### Scenario 1: Robo-Advisor

```python
# Client risk questionnaire → Portfolio recommendation
client_profile = {
    "age": 35,
    "risk_tolerance": "moderate",
    "investment_horizon": "long_term",
    "goals": ["retirement", "wealth_growth"]
}

# Generate portfolio using Pydantic model
portfolio = generate_portfolio(client_profile)
# Returns: 60% stocks, 30% bonds, 10% alternatives
```

### Scenario 2: Algorithmic Trading

```python
# Real-time market data → Trading signal
market_data = get_realtime_data("TSLA")
technical_indicators = calculate_indicators(market_data)

# Generate signal using xgrammar (fast!)
signal = generate_trade_signal(technical_indicators)
# Returns: BUY, confidence 75%, target $280, stop $240
```

### Scenario 3: Compliance Reporting

```python
# Transactions → Regulatory report
transactions = get_monthly_transactions()

# Extract and validate using Outlines (complex rules)
report = generate_compliance_report(transactions)
# Validates: MiFID II, Dodd-Frank, Basel III
```

### Scenario 4: Financial Planning

```python
# Income, expenses, goals → Financial plan
user_data = {
    "annual_income": 150000,
    "monthly_expenses": 8000,
    "current_savings": 50000,
    "retirement_goal": 2000000,
    "retirement_age": 65
}

# Generate plan with projections
plan = generate_financial_plan(user_data)
# Returns: Save $X/month, expected retirement age 63
```

---

## 🚀 Performance Optimization

### High-Frequency Trading (xgrammar)

```python
# Latency-critical: Use xgrammar
response = client.chat.completions.create(
    model="nemotron",
    messages=[...],
    extra_body={"guided_json": schema},
    max_tokens=200,  # Keep it small
    temperature=0.1   # Deterministic
)
# Target: <50ms response time
```

### Batch Processing (Both)

```python
# Process 1000 transactions
for batch in chunks(transactions, 100):
    results = process_batch_xgrammar(batch)  # Fast path
    
# Complex validation
for result in results:
    if needs_complex_validation(result):
        validate_with_outlines(result)  # Slow path
```

### Caching Schemas

```python
# Cache compiled schemas
schema_cache = {}

def get_schema(model_class):
    if model_class not in schema_cache:
        schema_cache[model_class] = model_class.model_json_schema()
    return schema_cache[model_class]
```

---

## 🧪 Testing

### Run Financial Tests

```bash
# Activate environment
source venv/bin/activate

# Run financial test suite
python financial_test.py

# Expected output:
# ✅ Transaction Parsing
# ✅ Portfolio Analysis
# ✅ Risk Assessment
# ✅ Trading Signals
# ✅ Financial Statements
# ✅ Market Data
```

### Validation

```python
# All financial data is validated with Pydantic
try:
    transaction = Transaction(**data)
    # Validation passed
except ValidationError as e:
    # Handle invalid data
    print(f"Validation failed: {e}")
```

---

## 📋 Best Practices

1. **Use xgrammar for:**
   - High-frequency operations
   - Standard financial data structures
   - Real-time processing
   - Low-latency requirements

2. **Use Outlines for:**
   - Custom regulatory formats (SWIFT, FIX, MiFID)
   - Complex validation rules
   - Non-standard formats
   - One-off processing

3. **Always validate:**
   ```python
   # Use Pydantic validators
   @validator('price')
   def price_must_be_positive(cls, v):
       if v <= 0:
           raise ValueError('Price must be positive')
       return v
   ```

4. **Cache compiled schemas:**
   - Faster repeated calls
   - Reduce overhead

5. **Set appropriate timeouts:**
   ```python
   # Trading: Fast timeout
   timeout = 100  # 100ms
   
   # Reporting: Generous timeout
   timeout = 30000  # 30s
   ```

---

## 🎓 Financial Concepts

### Risk Metrics

- **Volatility**: Measure of price variability
- **Sharpe Ratio**: Return per unit of risk
- **Beta**: Correlation with market
- **VaR**: Maximum expected loss
- **Max Drawdown**: Largest peak-to-trough decline

### Trading Indicators

- **RSI**: Overbought (>70) / Oversold (<30)
- **MACD**: Trend-following momentum
- **Moving Averages**: Smooth price trends
- **Bollinger Bands**: Volatility channels

### Valuation Metrics

- **P/E Ratio**: Price-to-Earnings
- **P/B Ratio**: Price-to-Book
- **EV/EBITDA**: Enterprise Value to EBITDA
- **FCF Yield**: Free Cash Flow / Market Cap

---

## 🔗 References

1. **Pydantic**: https://docs.pydantic.dev/
2. **Outlines**: https://dottxt-ai.github.io/outlines/
3. **xgrammar**: https://github.com/mlc-ai/xgrammar
4. **SWIFT Standards**: https://www.swift.com/standards
5. **FIX Protocol**: https://www.fixtrading.org/
6. **MiFID II**: https://www.esma.europa.eu/policy-rules/mifid-ii

---

## ✅ Summary

With **xgrammar** + **Outlines**, your Nemotron-3 deployment can handle:

- ✅ **Fast transaction processing** (xgrammar)
- ✅ **Complex financial formats** (Outlines)
- ✅ **Portfolio analytics** (both)
- ✅ **Risk calculations** (xgrammar for speed)
- ✅ **Algorithmic trading** (xgrammar for low latency)
- ✅ **Regulatory compliance** (Outlines for validation)
- ✅ **Earnings analysis** (xgrammar for extraction)
- ✅ **Custom protocols** (Outlines for SWIFT/FIX)

**Production-ready for financial applications!** 💰🚀
