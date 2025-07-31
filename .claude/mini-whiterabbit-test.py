#!/usr/bin/env python3
"""
Mini test of WhiteRabbitNeo models
"""

import json
import time
import requests

def quick_test_model(model: str):
    """Quick test of WhiteRabbitNeo models"""
    
    test_code = """
    contract Test {
        mapping(address => uint) balances;
        
        function withdraw() public {
            uint amt = balances[msg.sender];
            msg.sender.call{value: amt}("");
            balances[msg.sender] = 0;
        }
    }
    """
    
    prompt = f"Analyze this Solidity code for the reentrancy vulnerability:\n{test_code}"
    
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {'temperature': 0.1, 'num_predict': 300}
            },
            timeout=45
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()['response']
            score = 50 if 'reentrancy' in result.lower() else 0
            score += 30 if 'state' in result.lower() and 'change' in result.lower() else 0
            score += 20 if any(fix in result.lower() for fix in ['before', 'check', 'nonreentrant']) else 0
            
            return {
                'model': model,
                'score': score,
                'time': elapsed,
                'found_reentrancy': 'reentrancy' in result.lower()
            }
        else:
            return {'model': model, 'error': f"Status {response.status_code}"}
    except Exception as e:
        return {'model': model, 'error': str(e)}

def main():
    models = ['whiterabbitneo:latest', 'neo:latest']
    
    print("WhiteRabbitNeo Quick Comparison")
    print("=" * 40)
    
    results = []
    for model in models:
        print(f"\nTesting {model}...")
        result = quick_test_model(model)
        results.append(result)
        
        if 'error' not in result:
            print(f"  Score: {result['score']}/100")
            print(f"  Time: {result['time']:.2f}s")
            print(f"  Found reentrancy: {result['found_reentrancy']}")
        else:
            print(f"  Error: {result['error']}")
    
    with open('.claude/whiterabbit-quick-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    valid = [r for r in results if 'error' not in r]
    if valid:
        best = max(valid, key=lambda x: x['score'])
        print(f"\nBest WhiteRabbitNeo model: {best['model']}")

if __name__ == "__main__":
    main()