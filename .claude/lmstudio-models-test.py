#!/usr/bin/env python3
"""
Test LM Studio GGUF models for security analysis
Note: These would need to be loaded in LM Studio first
"""

import json
import requests
import time
from pathlib import Path

# LM Studio models discovered
LMSTUDIO_MODELS = {
    "Llama-3.2-8X3B-MOE-Dark-Champion": {
        "path": "DavidAU/Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B-GGUF",
        "file": "L3.2-8X3B-MOE-Dark-Champion-Inst-18.4B-uncen-ablit_D_AU-IQ4_XS.gguf",
        "estimated_size": "~12GB",
        "type": "MOE (Mixture of Experts)"
    },
    "Devstral-Small-2507": {
        "path": "lmstudio-community/Devstral-Small-2507-GGUF",
        "file": "Devstral-Small-2507-Q4_K_M.gguf", 
        "estimated_size": "~3GB",
        "type": "Code-focused (small)"
    },
    "Phi-4-reasoning-plus": {
        "path": "lmstudio-community/Phi-4-reasoning-plus-GGUF",
        "file": "Phi-4-reasoning-plus-Q4_K_M.gguf",
        "estimated_size": "~8GB", 
        "type": "Reasoning-focused"
    },
    "Qwen3-14B": {
        "path": "lmstudio-community/Qwen3-14B-GGUF",
        "file": "Qwen3-14B-Q4_K_M.gguf",
        "estimated_size": "~8GB",
        "type": "General purpose"
    },
    "Qwen3-30B-A3B": {
        "path": "lmstudio-community/Qwen3-30B-A3B-GGUF", 
        "file": "Qwen3-30B-A3B-Q4_K_M.gguf",
        "estimated_size": "~18GB",
        "type": "Large general purpose"
    },
    "Gemma-3-12B": {
        "path": "lmstudio-community/gemma-3-12b-it-GGUF",
        "file": "gemma-3-12b-it-Q4_K_M.gguf",
        "estimated_size": "~7GB",
        "type": "Google's model"
    },
    "Absolute_Zero_Reasoner-Coder-14B": {
        "path": "mradermacher/Absolute_Zero_Reasoner-Coder-14b-GGUF",
        "file": "Absolute_Zero_Reasoner-Coder-14b.Q5_K_S.gguf",
        "estimated_size": "~10GB",
        "type": "Reasoning + Coding specialist"
    },
    "WhiteRabbitNeo-V3-7B": {
        "path": "mradermacher/WhiteRabbitNeo-V3-7B-i1-GGUF",
        "file": "WhiteRabbitNeo-V3-7B.i1-Q6_K.gguf",
        "estimated_size": "~6GB",
        "type": "WhiteRabbitNeo variant"
    }
}

def test_lmstudio_model_if_loaded(model_name: str, port: int = 1234):
    """Test a model if it's loaded in LM Studio (default port 1234)"""
    
    test_code = """
    contract ReentrancyTest {
        mapping(address => uint256) balances;
        
        function withdraw() external {
            uint256 amount = balances[msg.sender];
            (bool success,) = msg.sender.call{value: amount}("");
            require(success);
            balances[msg.sender] = 0;
        }
    }
    """
    
    prompt = f"""Analyze this Solidity smart contract for security vulnerabilities:

{test_code}

Identify:
1. Specific vulnerabilities
2. Attack scenarios  
3. Severity level
4. How to fix them

Be technical and specific."""

    try:
        start_time = time.time()
        
        # LM Studio uses OpenAI-compatible API
        response = requests.post(
            f'http://localhost:{port}/v1/chat/completions',
            headers={'Content-Type': 'application/json'},
            json={
                'model': 'current-model',  # LM Studio uses this placeholder
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.1,
                'max_tokens': 800
            },
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            content_lower = content.lower()
            
            # Score the response
            score = 0
            findings = []
            
            # Reentrancy detection (40 points)
            if 'reentrancy' in content_lower or 're-entrancy' in content_lower:
                score += 40
                findings.append('reentrancy')
            
            # Understanding of call/state issue (25 points)
            if 'call' in content_lower and ('state' in content_lower or 'balance' in content_lower):
                score += 25
                findings.append('call_state_understanding')
            
            # CEI pattern or fix suggestion (25 points)
            if any(term in content_lower for term in ['check', 'effect', 'interaction', 'nonreentrant', 'mutex']):
                score += 25
                findings.append('fix_suggested')
            
            # Severity assessment (10 points)
            if any(sev in content_lower for sev in ['high', 'critical', 'severe']):
                score += 10
                findings.append('severity_assessed')
            
            return {
                'model': model_name,
                'score': score,
                'time': elapsed,
                'findings': findings,
                'response_preview': content[:300] + '...' if len(content) > 300 else content,
                'available': True
            }
        else:
            return {'model': model_name, 'error': f"HTTP {response.status_code}", 'available': False}
            
    except requests.exceptions.ConnectionError:
        return {'model': model_name, 'error': 'LM Studio not running or model not loaded', 'available': False}
    except Exception as e:
        return {'model': model_name, 'error': str(e), 'available': False}

def create_model_comparison_report():
    """Create a comprehensive report comparing Ollama vs LM Studio models"""
    
    print("LM Studio Models Analysis")
    print("=" * 50)
    print("Note: Models need to be loaded in LM Studio to test")
    print("Default LM Studio API port: 1234")
    print("-" * 50)
    
    # Try to test if any model is loaded
    print("\nTesting if LM Studio is running with a model loaded...")
    test_result = test_lmstudio_model_if_loaded("unknown-model")
    
    if test_result.get('available', False):
        print("✅ LM Studio is running with a model loaded!")
        print(f"Score: {test_result['score']}/100")
        print(f"Time: {test_result['time']:.2f}s")
        print(f"Findings: {', '.join(test_result['findings'])}")
    else:
        print(f"❌ LM Studio not accessible: {test_result.get('error', 'Unknown error')}")
    
    # Create comprehensive model analysis
    print("\n" + "=" * 50)
    print("LM STUDIO MODEL INVENTORY")
    print("=" * 50)
    
    recommendations = {
        "security_analysis_potential": [],
        "coding_specialists": [],
        "reasoning_specialists": [],
        "general_purpose": []
    }
    
    for model_name, info in LMSTUDIO_MODELS.items():
        print(f"\n📦 {model_name}")
        print(f"   Size: {info['estimated_size']}")
        print(f"   Type: {info['type']}")
        print(f"   File: {info['file']}")
        
        # Categorize by potential use case
        if 'coder' in model_name.lower() or 'code' in info['type'].lower():
            recommendations['coding_specialists'].append(model_name)
            print("   🔧 Recommended for: Code analysis")
        elif 'reasoning' in model_name.lower() or 'reasoning' in info['type'].lower():
            recommendations['reasoning_specialists'].append(model_name)
            print("   🧠 Recommended for: Complex vulnerability reasoning")
        elif 'whiterabbit' in model_name.lower():
            recommendations['security_analysis_potential'].append(model_name)
            print("   🐰 Recommended for: Security analysis (based on Ollama performance)")
        elif 'dark' in model_name.lower() or 'moe' in info['type'].lower():
            recommendations['security_analysis_potential'].append(model_name)
            print("   🔍 Recommended for: Advanced security analysis")
        else:
            recommendations['general_purpose'].append(model_name)
            print("   📋 General purpose model")
    
    # Create testing recommendations
    print("\n" + "=" * 50)
    print("TESTING RECOMMENDATIONS")
    print("=" * 50)
    
    print("\n🎯 **TOP PRIORITY TO TEST:**")
    priority_models = [
        ("Absolute_Zero_Reasoner-Coder-14B", "Coding + Reasoning specialist"),
        ("WhiteRabbitNeo-V3-7B", "New version of our Ollama champion"),
        ("Llama-3.2-8X3B-MOE-Dark-Champion", "MOE architecture, uncensored"),
        ("Phi-4-reasoning-plus", "Enhanced reasoning capabilities")
    ]
    
    for model, reason in priority_models:
        print(f"  • {model} - {reason}")
    
    print("\n📊 **COMPARISON WITH OLLAMA WINNERS:**")
    ollama_winners = [
        ("whiterabbitneo:latest", "100/100, 12.51s"),
        ("phi4-reasoning:latest", "100/100, 27.20s"), 
        ("qwen3:30b-a3b", "100/100, 34.11s")
    ]
    
    for model, score in ollama_winners:
        print(f"  🏆 {model}: {score}")
    
    print("\n🔬 **POTENTIAL ADVANTAGES OF LM STUDIO MODELS:**")
    advantages = [
        "GGUF format = faster loading and inference",
        "Quantized models = lower memory usage",
        "Uncensored models = better vulnerability analysis", 
        "MOE architecture = specialized expert routing",
        "Local API = no network overhead"
    ]
    
    for advantage in advantages:
        print(f"  ✅ {advantage}")
    
    # Save detailed analysis
    analysis_data = {
        "lmstudio_models": LMSTUDIO_MODELS,
        "recommendations": recommendations,
        "test_results": test_result if test_result.get('available') else None,
        "comparison_notes": "Need to load models in LM Studio to test performance"
    }
    
    with open('.claude/lmstudio-analysis.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\n💾 Analysis saved to .claude/lmstudio-analysis.json")
    
    # Instructions for testing
    print("\n" + "=" * 50)
    print("HOW TO TEST THESE MODELS")
    print("=" * 50)
    print("""
1. Open LM Studio
2. Load one of the recommended models
3. Start the local server (default port 1234)
4. Run this script again to test the loaded model
5. Compare results with Ollama models

Example LM Studio startup:
  - Model: Absolute_Zero_Reasoner-Coder-14B
  - Context Length: 4096
  - Temperature: 0.1
  - Server Port: 1234
""")

def main():
    create_model_comparison_report()

if __name__ == "__main__":
    main()