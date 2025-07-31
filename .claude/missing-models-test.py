#!/usr/bin/env python3
"""
Test the models I missed: phi4-reasoning, magistral, qwen3
"""

import json
import time
import requests

def test_missing_models():
    """Test the models I didn't include in the original comparison"""
    
    models = [
        'phi4-reasoning:latest',  # 11 GB
        'magistral:latest',       # 14 GB  
        'qwen3:30b-a3b'          # 18 GB
    ]
    
    # Same reentrancy test for consistency
    test_code = """
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
    
    prompt = f"""Analyze this smart contract for security vulnerabilities. Be specific about:
1. What vulnerability exists
2. How severe it is  
3. How to fix it

Code:
{test_code}

Focus on reentrancy and state management issues."""
    
    results = []
    
    for model in models:
        print(f"\nTesting {model}...")
        
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
                        'num_predict': 600
                    }
                },
                timeout=90  # Longer timeout for larger models
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()['response']
                result_lower = result.lower()
                
                # Same scoring system as before
                score = 0
                findings = []
                
                # Check for reentrancy detection (40 points)
                if 'reentrancy' in result_lower or 're-entrancy' in result_lower:
                    score += 40
                    findings.append('reentrancy')
                
                # Check for understanding of call-state issue (20 points)
                if 'call' in result_lower and 'state' in result_lower:
                    score += 20
                    findings.append('call_state_issue')
                
                # Check for CEI pattern mention (20 points)
                if any(term in result_lower for term in ['check', 'effect', 'interaction', 'cei']):
                    score += 20
                    findings.append('cei_pattern')
                
                # Check for fix suggestions (20 points)
                if any(fix in result_lower for fix in ['nonreentrant', 'mutex', 'lock', 'before']):
                    score += 20
                    findings.append('fix_suggested')
                
                result_data = {
                    'model': model,
                    'score': score,
                    'time': elapsed,
                    'findings': findings,
                    'response_preview': result[:300] + '...' if len(result) > 300 else result
                }
                
                results.append(result_data)
                
                print(f"  Score: {score}/100")
                print(f"  Time: {elapsed:.2f}s")
                print(f"  Findings: {', '.join(findings)}")
                print(f"  Efficiency: {score/elapsed:.2f} points/second")
                
            else:
                error_result = {'model': model, 'error': f"Status {response.status_code}"}
                results.append(error_result)
                print(f"  Error: Status {response.status_code}")
                
        except Exception as e:
            error_result = {'model': model, 'error': str(e)}
            results.append(error_result)
            print(f"  Error: {str(e)}")
    
    return results

def main():
    print("Testing Missing Models for Security Analysis")
    print("=" * 50)
    print("Models: phi4-reasoning:latest, magistral:latest, qwen3:30b-a3b")
    print("Test: Reentrancy vulnerability detection")
    print("-" * 50)
    
    results = test_missing_models()
    
    # Save results
    with open('.claude/missing-models-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Show final comparison with previously tested models
    print("\n" + "=" * 50)
    print("UPDATED COMPLETE RANKINGS")
    print("=" * 50)
    
    # Previous results (from memory)
    all_results = [
        {'model': 'whiterabbitneo:latest', 'score': 100, 'time': 12.51, 'size': '8.1 GB'},
        {'model': 'SmartLLM-OG:latest', 'score': 100, 'time': 50.83, 'size': '16 GB'},
        {'model': 'smartllm:latest', 'score': 85, 'time': 22.96, 'size': '8.5 GB'},
        {'model': 'devstral:latest', 'score': 80, 'time': 38.08, 'size': '14 GB'},
        {'model': 'neo:latest', 'score': 70, 'time': 18.77, 'size': '15 GB'},
        {'model': 'deepseek-r1:7b-qwen-distill-q8_0', 'score': 20, 'time': 15.45, 'size': '8.1 GB'},
    ]
    
    # Add new results
    for result in results:
        if 'error' not in result:
            all_results.append({
                'model': result['model'], 
                'score': result['score'], 
                'time': result['time'],
                'size': {'phi4-reasoning:latest': '11 GB', 'magistral:latest': '14 GB', 'qwen3:30b-a3b': '18 GB'}[result['model']]
            })
    
    # Sort by score, then by time
    all_results.sort(key=lambda x: (x['score'], -x['time']), reverse=True)
    
    print("\nFinal Complete Rankings:")
    for i, result in enumerate(all_results, 1):
        efficiency = result['score'] / result['time'] if result['time'] > 0 else 0
        print(f"{i}. {result['model']} ({result['size']})")
        print(f"   Score: {result['score']}/100, Time: {result['time']:.2f}s, Efficiency: {efficiency:.2f}")
    
    print(f"\nNEW CHAMPION (if any): {all_results[0]['model']}")

if __name__ == "__main__":
    main()