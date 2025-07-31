#!/usr/bin/env python3
"""
Quick focused test on specific models for security analysis
"""

import json
import time
import requests
from typing import Dict, Tuple

# Focus on the models you specifically asked about
TEST_MODELS = [
    "deepseek-coder:33b-instruct",
    "deepseek-r1:7b-qwen-distill-q8_0", 
    "devstral:latest"
]

# Quick but comprehensive security test
QUICK_TEST = """
contract VulnerableBank {
    mapping(address => uint) public balances;
    
    function withdraw() public {
        uint amount = balances[msg.sender];
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Failed");
        balances[msg.sender] = 0;
    }
}
"""

def test_model(model: str) -> Tuple[Dict, float]:
    """Quick test of model's security analysis capabilities"""
    
    prompt = """Analyze this smart contract for security vulnerabilities. Be specific about:
1. What vulnerability exists
2. How severe it is
3. How to fix it

Code:
""" + QUICK_TEST
    
    start_time = time.time()
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_predict': 500
                }
            },
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()['response']
            
            # Quick scoring
            score = 0
            result_lower = result.lower()
            
            # Check for key vulnerability identification
            if 'reentrancy' in result_lower or 're-entrancy' in result_lower:
                score += 40
            if 'call' in result_lower and 'state' in result_lower:
                score += 20
            if 'check' in result_lower and 'effect' in result_lower:
                score += 20
            if any(fix in result_lower for fix in ['nonreentrant', 'mutex', 'lock', 'before']):
                score += 20
                
            return {
                'model': model,
                'score': score,
                'time': elapsed,
                'response_preview': result[:200] + '...' if len(result) > 200 else result
            }, elapsed
        else:
            return {'model': model, 'error': f"Status {response.status_code}"}, elapsed
            
    except Exception as e:
        return {'model': model, 'error': str(e)}, 60

def main():
    print("Quick Security Analysis Model Test")
    print("=" * 50)
    print(f"Testing models: {', '.join(TEST_MODELS)}")
    print("\nTest case: Classic reentrancy vulnerability")
    print("-" * 50)
    
    results = []
    
    for model in TEST_MODELS:
        print(f"\nTesting {model}...")
        result, elapsed = test_model(model)
        results.append(result)
        
        if 'error' not in result:
            print(f"  Score: {result['score']}/100")
            print(f"  Time: {result['time']:.2f}s")
            print(f"  Response preview: {result['response_preview']}")
        else:
            print(f"  Error: {result['error']}")
    
    # Rank results
    valid_results = [r for r in results if 'error' not in r]
    valid_results.sort(key=lambda x: (x['score'], -x['time']), reverse=True)
    
    print("\n" + "=" * 50)
    print("RANKINGS:")
    print("=" * 50)
    
    for i, result in enumerate(valid_results, 1):
        efficiency = result['score'] / result['time'] if result['time'] > 0 else 0
        print(f"{i}. {result['model']}")
        print(f"   Score: {result['score']}/100")
        print(f"   Time: {result['time']:.2f}s")
        print(f"   Efficiency: {efficiency:.2f} points/second")
    
    with open('.claude/quick-test-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    if valid_results:
        print(f"\nBEST MODEL: {valid_results[0]['model']}")

if __name__ == "__main__":
    main()