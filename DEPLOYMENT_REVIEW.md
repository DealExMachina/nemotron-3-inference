# Koyeb Deployment Review - Issues Found

**Date:** December 18, 2025  
**Service ID:** `0660f41c-9519-406d-8caa-5c4587dfa03b`  
**Current Status:** PAUSED

## 🚨 Critical Issues

### 1. **WRONG REGION CODE**
**Severity:** CRITICAL - Will cause deployment failures

**Current (deploy.yml):**
```json
"regions": ["was"]
```

**Actual API Requirement:**
```json
"regions": ["na"]
```

**Issue:** Koyeb API uses `"na"` (North America) internally, NOT `"was"` (Washington). This mismatch will cause validation errors.

---

### 2. **Missing Scopes on All Fields**
**Severity:** HIGH - May cause configuration issues

The actual deployment definition includes `"scopes":["region:na"]` on:
- `env` variables
- `scalings`
- `instance_types`

**Current deploy.yml:** Missing scopes entirely

**Correct format:**
```json
"env": [
  {"scopes":["region:na"], "key":"HF_TOKEN", "secret":"hf-token"},
  {"scopes":["region:na"], "key":"VLLM_ATTENTION_BACKEND", "value":"FLASHINFER"}
],
"scalings": [{"scopes":["region:na"], "min":0, "max":1}],
"instance_types": [{"scopes":["region:na"], "type":"gpu-nvidia-h100"}]
```

---

### 3. **Missing `image_registry_secret`**
**Severity:** MEDIUM - Required for private Docker Hub images

**Current deploy.yml:**
```json
"docker": {
  "image": "$IMAGE"
}
```

**Should be:**
```json
"docker": {
  "image": "$IMAGE",
  "image_registry_secret": "jeanbapt",
  "command": "",
  "args": [],
  "entrypoint": [],
  "privileged": false
}
```

---

### 4. **Missing Deployment Strategy**
**Severity:** LOW - Uses default if not specified

**Actual deployment:**
```json
"strategy": {"type": "DEPLOYMENT_STRATEGY_TYPE_ROLLING"}
```

**deploy.yml:** Missing this field

---

### 5. **Incomplete `sleep_idle_delay` Configuration**
**Severity:** MEDIUM - Known API validation issue (ref: Koyeb Community #4186)

**Actual deployment:**
```json
"scalings": [{
  "scopes": ["region:na"],
  "min": 0,
  "max": 1,
  "targets": [{
    "sleep_idle_delay": {
      "value": 0,
      "deep_sleep_value": 3900,
      "light_sleep_value": 0
    }
  }]
}]
```

**deploy.yml:** Doesn't include targets/sleep_idle_delay at all

---

### 6. **Missing Required Empty Fields**
**Severity:** LOW - May cause validation warnings

The actual deployment includes these empty fields:
```json
"proxy_ports": [],
"volumes": [],
"config_files": [],
"skip_cache": false
```

---

## 📋 Recommended Fixes

### Fix 1: Update Region Code
Change all instances of `"was"` to `"na"`:

```yaml
# In deploy.yml lines 123, 204
"regions": ["na"]
```

### Fix 2: Add Scopes to All Configuration
Wrap env, scalings, and instance_types with proper scopes:

```json
"env": [
  {"scopes":["region:na"], "key":"HF_TOKEN", "secret":"hf-token"},
  {"scopes":["region:na"], "key":"VLLM_ATTENTION_BACKEND", "value":"FLASHINFER"}
],
"instance_types": [{"scopes":["region:na"], "type":"gpu-nvidia-h100"}],
"scalings": [{
  "scopes":["region:na"],
  "min": 0,
  "max": 1,
  "targets": [{
    "sleep_idle_delay": {
      "value": 0,
      "deep_sleep_value": 3900,
      "light_sleep_value": 0
    }
  }]
}]
```

### Fix 3: Add Docker Registry Secret
```json
"docker": {
  "image": "$IMAGE",
  "image_registry_secret": "jeanbapt",
  "command": "",
  "args": [],
  "entrypoint": [],
  "privileged": false
}
```

### Fix 4: Add Deployment Strategy
```json
"definition": {
  "name": "nemotron",
  "type": "WEB",
  "strategy": {"type": "DEPLOYMENT_STRATEGY_TYPE_ROLLING"},
  ...
}
```

### Fix 5: Add Missing Empty Fields
```json
"proxy_ports": [],
"volumes": [],
"config_files": [],
"skip_cache": false
```

---

## 🔍 Current Service State

- **Status:** PAUSED (manually paused)
- **Latest Deployment:** `1bca56f5-32e5-41cf-b80b-88426507c492` (STOPPED)
- **Successful Run:** Yes, on 2025-12-16 17:31:44 UTC
- **Current Image:** `jeanbapt/nemotron-3-inference:latest`
- **Instance:** `gpu-nvidia-h100` 
- **Actual Region:** `na` (not `was`)

---

## 📚 References

1. **Koyeb API Docs:** https://www.koyeb.com/docs/api
2. **Known Issue - Deep Sleep Value:** https://community.koyeb.com/t/koyeb-cli-400-error-when-updating-deployment/4186
3. **Service Update Best Practices:** 
   - Retrieve current deployment definition first
   - Modify only necessary fields
   - Include all required nested structures

---

## ✅ Next Steps

1. Update deploy.yml with correct region code (`na`)
2. Add scopes to all configuration objects
3. Add image_registry_secret to docker configuration
4. Add deployment strategy
5. Include sleep_idle_delay with all three values
6. Test with a manual workflow dispatch
7. Monitor deployment for validation errors

---

## 🎯 Complete Corrected Definition

```json
{
  "definition": {
    "name": "nemotron",
    "type": "WEB",
    "strategy": {"type": "DEPLOYMENT_STRATEGY_TYPE_ROLLING"},
    "routes": [{"path": "/", "port": 8000}],
    "ports": [{"port": 8000, "protocol": "http"}],
    "proxy_ports": [],
    "env": [
      {"scopes": ["region:na"], "key": "HF_TOKEN", "secret": "hf-token"},
      {"scopes": ["region:na"], "key": "VLLM_ATTENTION_BACKEND", "value": "FLASHINFER"}
    ],
    "regions": ["na"],
    "scalings": [{
      "scopes": ["region:na"],
      "min": 0,
      "max": 1,
      "targets": [{
        "sleep_idle_delay": {
          "value": 0,
          "deep_sleep_value": 3900,
          "light_sleep_value": 0
        }
      }]
    }],
    "instance_types": [{"scopes": ["region:na"], "type": "gpu-nvidia-h100"}],
    "health_checks": [{
      "http": {"path": "/health", "port": 8000, "method": "GET", "headers": []},
      "grace_period": 300,
      "interval": 30,
      "timeout": 10,
      "restart_limit": 3
    }],
    "volumes": [],
    "config_files": [],
    "skip_cache": false,
    "docker": {
      "image": "$IMAGE",
      "image_registry_secret": "jeanbapt",
      "command": "",
      "args": [],
      "entrypoint": [],
      "privileged": false
    }
  }
}
```
