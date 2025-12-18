# Pydantic V2 Migration - Best Practices Applied

**Date:** December 18, 2025  
**Pydantic Version:** 2.x  
**Updated Files:** financial_test.py

---

## 🎯 What Changed

Migrated from **Pydantic V1** deprecated patterns to **Pydantic V2** best practices following official guidance from:
- Pydantic V2 Migration Guide
- Pydantic V2 Best Practices (2024-2025)
- Hugging Face Inference Providers documentation

---

## 📋 Key Changes

### 1. **Validator Migration** (`@validator` → `@field_validator`)

**Before (V1 - Deprecated):**
```python
from pydantic import BaseModel, validator

class Transaction(BaseModel):
    total_amount: float
    
    @validator('total_amount')
    def validate_total(cls, v, values):
        if 'quantity' in values:
            ...
        return v
```

**After (V2 - Current):**
```python
from pydantic import BaseModel, field_validator

class Transaction(BaseModel):
    total_amount: float
    
    @field_validator('total_amount', mode='after')
    @classmethod
    def validate_total(cls, v: float, info) -> float:
        """Validate total amount matches quantity × price"""
        if hasattr(info, 'data'):
            quantity = info.data.get('quantity')
            ...
        return v
```

**Changes:**
- ✅ `@validator` → `@field_validator`
- ✅ Added `@classmethod` decorator
- ✅ Added explicit type hints (`v: float -> float`)
- ✅ Added `mode='after'` parameter (validates after type coercion)
- ✅ Access other fields via `info.data.get()` instead of `values` dict
- ✅ Added docstring for clarity

---

### 2. **Model Configuration** (`Config` → `model_config`)

**Before (V1 - Deprecated):**
```python
class Transaction(BaseModel):
    class Config:
        validate_all = True
        extra = 'forbid'
```

**After (V2 - Current):**
```python
from pydantic import ConfigDict

class Transaction(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_default=True,
        extra='forbid'
    )
```

**Configuration Options Used:**
- `str_strip_whitespace=True` - Auto-trim strings
- `validate_default=True` - Validate default values
- `extra='forbid'` - Reject extra fields not in schema

---

### 3. **Type Safety with `PositiveFloat`**

**Before (V1):**
```python
quantity: float = Field(gt=0)
price: float = Field(gt=0)
```

**After (V2):**
```python
from pydantic.types import PositiveFloat

quantity: PositiveFloat  # Automatically > 0
price: PositiveFloat
```

**Benefits:**
- ✅ Clearer intent
- ✅ Less verbose
- ✅ Better type hints for IDEs
- ✅ Consistent across codebase

---

### 4. **Field Constraints Enhancement**

**Before:**
```python
symbol: str
name: str
```

**After:**
```python
symbol: str = Field(min_length=1, max_length=10)
name: str = Field(min_length=1)
```

**New Constraints Added:**
- `min_length` - Minimum string length
- `max_length` - Maximum string length
- `ge` / `le` - Greater/less than or equal to
- `gt` / `lt` - Greater/less than
- `description` - Field documentation

---

## 🏗️ Updated Models

### Transaction
```python
class Transaction(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_default=True,
        extra='forbid'
    )
    
    transaction_id: str = Field(description="Unique transaction identifier")
    quantity: PositiveFloat  # Was: float = Field(gt=0)
    price_per_unit: PositiveFloat
    total_amount: float
    
    @field_validator('total_amount', mode='after')
    @classmethod
    def validate_total(cls, v: float, info) -> float:
        # Validation logic
        return v
```

### Portfolio
```python
class Portfolio(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        extra='forbid',
        str_strip_whitespace=True
    )
    
    portfolio_id: str = Field(min_length=1)
    account_holder: str = Field(min_length=1)
    total_value: PositiveFloat
    holdings: List[PortfolioHolding] = Field(min_length=0)
```

### RiskAnalysis
```python
class RiskAnalysis(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        extra='forbid',
        str_strip_whitespace=True
    )
    
    volatility: float = Field(ge=0, le=100)
    sharpe_ratio: float = Field(ge=-10, le=10)  # Realistic bounds
    beta: float = Field(ge=-5, le=5)  # Market correlation bounds
    recommendations: List[str] = Field(min_length=1)  # At least one
```

### TradeSignal
```python
class TradeSignal(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        extra='forbid',
        str_strip_whitespace=True
    )
    
    symbol: str = Field(min_length=1, max_length=10)
    confidence: float = Field(ge=0, le=100)
    target_price: PositiveFloat
    stop_loss: PositiveFloat
    rationale: str = Field(min_length=10)  # Meaningful explanation
```

### MarketData
```python
class MarketData(BaseModel):
    model_config = ConfigDict(validate_default=True, extra='forbid')
    
    symbol: str = Field(min_length=1, max_length=20)
    last_price: PositiveFloat
    bid_price: Optional[PositiveFloat] = None  # May be unavailable
    ask_price: Optional[PositiveFloat] = None
    volume: int = Field(ge=0)
```

### FinancialStatement
```python
class FinancialStatement(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        extra='forbid',
        str_strip_whitespace=True
    )
    
    ticker: str = Field(min_length=1, max_length=10)
    revenue: PositiveFloat
    total_assets: PositiveFloat
    operating_income: float  # Can be negative
    net_income: float  # Can be negative
```

---

## ✅ Benefits of V2 Migration

### 1. **Better Type Safety**
```python
# V1: Runtime error if negative
quantity: float = Field(gt=0)

# V2: Clear at type-check time
quantity: PositiveFloat
```

### 2. **Clearer Validation**
```python
@field_validator('field_name', mode='after')  # Explicit timing
@classmethod  # Clear it's a class method
def validate_field(cls, v: Type) -> Type:  # Full type hints
    """Clear documentation"""
    ...
```

### 3. **Better IDE Support**
- Type hints work correctly in VSCode, PyCharm
- Auto-completion for field attributes
- Better error messages

### 4. **Stricter Validation**
- `extra='forbid'` - Rejects unexpected fields
- `validate_default=True` - Validates default values
- `str_strip_whitespace=True` - Auto-cleanup

### 5. **Future-Proof**
- V1 deprecated, will be removed in V3
- Following current best practices
- Compatible with latest tooling

---

## 📊 Validation Improvements

### Automatic Validation
```python
# Model automatically validates:
transaction = Transaction(
    transaction_id="TXN-001",
    quantity=100.0,  # ✅ PositiveFloat validates > 0
    price_per_unit=150.50,
    total_amount=15050.0,  # ✅ Custom validator checks math
    currency=Currency.USD
)
```

### Error Handling
```python
try:
    transaction = Transaction(**data)
except ValidationError as e:
    print(e.json())  # Detailed error information
    # Shows which field failed and why
```

---

## 🎓 Best Practices Applied

1. **Always use `@classmethod` with `@field_validator`**
   ```python
   @field_validator('field')
   @classmethod
   def validate(cls, v: Type) -> Type:
       ...
   ```

2. **Add explicit type hints**
   ```python
   def validate(cls, v: float, info) -> float:
       # Clear what goes in and comes out
   ```

3. **Use `mode` parameter appropriately**
   - `mode='before'` - Pre-process before type coercion
   - `mode='after'` (default) - Validate after coercion

4. **Add field descriptions**
   ```python
   field: Type = Field(description="What this field represents")
   ```

5. **Use appropriate types**
   - `PositiveFloat` instead of `float = Field(gt=0)`
   - `Optional[Type]` for nullable fields
   - `Literal[...]` for enums

6. **Configure models appropriately**
   ```python
   model_config = ConfigDict(
       validate_default=True,  # Always validate
       extra='forbid',  # Strict schemas
       str_strip_whitespace=True  # Clean input
   )
   ```

---

## 🔗 References

1. **Pydantic V2 Migration Guide**:  
   https://docs.pydantic.dev/latest/migration/

2. **Field Validators Documentation**:  
   https://docs.pydantic.dev/latest/concepts/validators/

3. **ConfigDict Options**:  
   https://docs.pydantic.dev/latest/api/config/

4. **Hugging Face Structured Outputs**:  
   https://huggingface.co/docs/inference-providers/guides/structured-output

---

## 🚀 Impact

### Before:
- ⚠️  Deprecation warnings
- 🟡 V1 style validators
- 🟡 Less type safety
- 🟡 Less IDE support

### After:
- ✅ No deprecation warnings
- ✅ V2 best practices
- ✅ Full type safety
- ✅ Excellent IDE support
- ✅ Future-proof
- ✅ Cleaner, more maintainable code

---

## 📝 Testing

All models have been updated and tested:

```bash
python financial_test.py
```

**Validation now includes:**
- ✅ Type checking (PositiveFloat, etc.)
- ✅ Range validation (ge, le, gt, lt)
- ✅ Length validation (min_length, max_length)
- ✅ Custom logic (field_validator)
- ✅ Cross-field validation (info.data)
- ✅ Automatic string cleanup
- ✅ Extra field rejection

---

## ✨ Summary

Migrated to **Pydantic V2** with:
- ✅ Modern `@field_validator` pattern
- ✅ `ConfigDict` for model configuration
- ✅ `PositiveFloat` for cleaner type hints
- ✅ Comprehensive field constraints
- ✅ Better error messages
- ✅ Future-proof code

**All financial models now follow 2025 best practices!** 🎉
