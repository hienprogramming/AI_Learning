import ollama
import json

MODEL = "llama3"

# Các tiêu chuẩn test (Checklist)
TESTING_CHECKLIST = {
    "autosar_compliance": {
        "title": "AUTOSAR Compliance",
        "items": [
            "Naming conventions follow AUTOSAR (e.g., Com_SendSignal, PduR_SendPdu)",
            "Function/variable names use correct prefix (Com_, PduR_, CanIf_, CanTp_)",
            "Return types follow AUTOSAR (Std_ReturnType, uint8, uint16, etc.)",
        ]
    },
    "embedded_c": {
        "title": "Embedded C Best Practices",
        "items": [
            "NO malloc/dynamic memory allocation found",
            "All variables are properly initialized",
            "No undefined behavior or potential undefined behavior",
            "No buffer overflow risks",
            "Proper scope and visibility of functions/variables",
        ]
    },
    "code_correctness": {
        "title": "Code Correctness",
        "items": [
            "Code matches the given requirement exactly",
            "Logic is correct and handles edge cases",
            "Constants and limits are respected (MAX_SIGNALS=8, MAX_PDUS=4, etc.)",
            "No dead code or unreachable statements",
        ]
    },
    "type_safety": {
        "title": "Type Safety",
        "items": [
            "Proper use of custom types (Com_SignalType, PduR_PduIdType, etc.)",
            "No inappropriate type casting",
            "Enums and defines used correctly",
            "Correct data type sizes for values",
        ]
    },
    "code_structure": {
        "title": "Code Structure",
        "items": [
            "Header guards present in .h files",
            "Proper separation: declarations in .h, implementation in .c",
            "Include dependencies are correct and minimal",
            "No circular includes",
        ]
    },
    "unit_testability": {
        "title": "Unit Test Compatibility",
        "items": [
            "Functions are testable (not too complex, clear inputs/outputs)",
            "Functions have single responsibility (easy to test in isolation)",
            "No hardcoded dependencies that prevent mocking",
            "Error handling and edge cases are testable",
            "Return values indicate success/failure clearly",
            "Function signatures are simple and clear",
        ]
    }
}

def build_test_prompt(code: str) -> str:
    """Build detailed testing prompt with checklist"""
    checklist_text = "TESTING CHECKLIST:\n\n"
    for category, data in TESTING_CHECKLIST.items():
        checklist_text += f"\n{data['title']}:\n"
        for item in data['items']:
            checklist_text += f"  ☐ {item}\n"
    
    return f"""{checklist_text}

CODE TO TEST:
```
{code}
```

Hãy kiểm tra code theo từng tiêu chuẩn trên. Trả về kết quả JSON với format:
{{
  "category_name": {{
    "passed": [list của items PASS],
    "failed": [list của items FAIL với lý do],
    "score": "X/Y"
  }},
  "summary": {{
    "total_checks": N,
    "passed": X,
    "failed": Y,
    "pass_rate": "X%"
  }}
}}

Chỉ trả về JSON, không có văn bản khác."""

def run(code: str) -> dict:
    """Test code với checklist định dạng JSON"""
    prompt = build_test_prompt(code)
    
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system", 
                "content": "You are a strict embedded C code tester. Evaluate code against a detailed checklist. Return ONLY valid JSON, no other text."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
    )["message"]["content"]
    
    # Try to parse JSON response
    try:
        # Find JSON in response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            result = json.loads(json_str)
            return result
    except json.JSONDecodeError:
        # If parsing fails, return the raw response
        return {"error": "Failed to parse JSON response", "raw": response}
    
    return {"error": "No JSON found in response", "raw": response}