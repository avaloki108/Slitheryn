# Ollama Model Integration Guide for Slitheryn

## Model Recommendations Based on Your Available Models

### For Security Analysis Tasks:

1. **deepseek-coder:33b-instruct** (18 GB)
   - Best for: Code analysis, vulnerability detection
   - Strengths: Trained specifically on code, understands Solidity patterns
   - Use case: Primary model for vulnerability analysis

2. **devstral:latest** (14 GB)
   - Best for: Code completion and pattern matching
   - Strengths: Fast inference, good for real-time analysis
   - Use case: Secondary model for quick checks

3. **SmartLLM-OG:latest** / **smartllm:latest**
   - Best for: Custom security patterns (if fine-tuned on security data)
   - Use case: Specialized detection based on your training

### Integration Architecture

```python
# Example integration with Slitheryn
import requests
from typing import Dict, List, Optional

class OllamaSecurityAnalyzer:
    def __init__(self, model_name: str = "deepseek-coder:33b-instruct"):
        self.model = model_name
        self.base_url = "http://localhost:11434"
        
    def analyze_vulnerability(self, code: str, context: Dict) -> Dict:
        """Analyze code for vulnerabilities using Ollama"""
        
        prompt = self._build_security_prompt(code, context)
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low for consistent analysis
                    "top_p": 0.9,
                    "num_predict": 1000
                }
            }
        )
        
        return self._parse_security_response(response.json())
    
    def _build_security_prompt(self, code: str, context: Dict) -> str:
        """Build specialized prompt for security analysis"""
        
        return f"""You are a smart contract security expert. Analyze this code for vulnerabilities.

Contract Code:
{code}

Context:
- Solidity Version: {context.get('solc_version', 'unknown')}
- Contract Type: {context.get('contract_type', 'unknown')}
- Previous Vulnerabilities Found: {context.get('previous_vulns', [])}

Identify:
1. Security vulnerabilities (reentrancy, overflow, access control, etc.)
2. Severity level (Critical/High/Medium/Low)
3. False positive likelihood (High/Medium/Low)
4. Specific line numbers affected
5. Recommended fixes

Format your response as JSON.
"""
```

### Model Selection Strategy

```python
class ModelSelector:
    """Select best model based on analysis type"""
    
    MODEL_CONFIGS = {
        "deep_analysis": {
            "model": "deepseek-coder:33b-instruct",
            "temperature": 0.1,
            "timeout": 60
        },
        "quick_scan": {
            "model": "devstral:latest",
            "temperature": 0.2,
            "timeout": 10
        },
        "pattern_matching": {
            "model": "smartllm:latest",
            "temperature": 0.1,
            "timeout": 30
        },
        "reasoning": {
            "model": "phi4-reasoning:latest",
            "temperature": 0.3,
            "timeout": 45
        }
    }
    
    @classmethod
    def get_model_for_task(cls, task_type: str) -> Dict:
        return cls.MODEL_CONFIGS.get(task_type, cls.MODEL_CONFIGS["deep_analysis"])
```

### False Positive Reduction Using Multiple Models

```python
class EnsembleAnalyzer:
    """Use multiple models to reduce false positives"""
    
    def __init__(self):
        self.models = [
            "deepseek-coder:33b-instruct",
            "devstral:latest",
            "smartllm:latest"
        ]
    
    def analyze_with_consensus(self, code: str) -> Dict:
        """Get consensus from multiple models"""
        
        results = []
        for model in self.models:
            analyzer = OllamaSecurityAnalyzer(model)
            result = analyzer.analyze_vulnerability(code, {})
            results.append(result)
        
        # Only report vulnerabilities found by majority
        return self._calculate_consensus(results)
```

### Performance Optimization Tips

1. **Model Loading**:
   - Keep frequently used models loaded: `ollama run deepseek-coder:33b-instruct`
   - Use model aliases for quick switching

2. **Context Management**:
   - Limit context window to relevant code sections
   - Use sliding window for large contracts

3. **Caching**:
   - Cache analysis results for identical code patterns
   - Store embeddings for similarity matching

4. **Batch Processing**:
   - Analyze multiple functions in parallel
   - Use different models for different vulnerability types

### Recommended Workflow

1. **Initial Scan**: Use `devstral` for quick overview
2. **Deep Analysis**: Use `deepseek-coder:33b-instruct` for detailed review
3. **Verification**: Use `smartllm` or `whiterabbitneo` for second opinion
4. **Reasoning**: Use `phi4-reasoning` for complex logic vulnerabilities

### Model-Specific Prompting Tips

#### DeepSeek Coder:
- Include specific Solidity version
- Provide function signatures for context
- Ask for line-by-line analysis

#### Devstral:
- Keep prompts concise
- Focus on specific vulnerability types
- Good for pattern matching

#### SmartLLM Models:
- Can handle more conversational prompts
- Good for explaining complex vulnerabilities
- Useful for generating fix suggestions

### Integration with Slitheryn Detectors

```python
# Example: Enhancing existing detector with LLM
class LLMEnhancedDetector(AbstractDetector):
    def __init__(self):
        super().__init__()
        self.llm_analyzer = OllamaSecurityAnalyzer()
    
    def _detect(self):
        results = []
        
        # Run traditional static analysis
        traditional_results = self._run_static_analysis()
        
        # Enhance with LLM analysis
        for result in traditional_results:
            llm_verification = self.llm_analyzer.analyze_vulnerability(
                result.code_snippet,
                {"detector": self.NAME, "confidence": result.confidence}
            )
            
            # Adjust confidence based on LLM feedback
            if llm_verification.get("false_positive_likelihood") == "High":
                result.confidence *= 0.5
            
            results.append(result)
        
        return results
```

## Quick Start Commands

```bash
# Test model connectivity
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-coder:33b-instruct",
  "prompt": "Explain reentrancy vulnerability",
  "stream": false
}'

# Run the evaluation script
python3 .claude/ollama-model-evaluation.py

# Keep your primary model loaded
ollama run deepseek-coder:33b-instruct --keepalive 24h
```