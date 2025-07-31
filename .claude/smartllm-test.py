#!/usr/bin/env python3
"""
Test SmartLLM models for security analysis
"""

import json
import time
import requests

def test_smartllm_models():
    """Test both SmartLLM variants"""
    
    models = ['smartllm:latest', 'SmartLLM-OG:latest']
    
    test_code = """
    contract DeFiVault {
        mapping(address => uint256) public balances;
        uint256 public totalSupply;
        
        function deposit() public payable {
            balances[msg.sender] += msg.value;
            totalSupply += msg.value;
        }
        
        function withdraw(uint256 amount) public {
            require(balances[msg.sender] >= amount);
            balances[msg.sender] -= amount;
            totalSupply -= amount;
            
            (bool success,) = msg.sender.call{value: amount}("");
            require(success);
        }
        
        function flashLoan(uint256 amount) public {
            uint256 balanceBefore = address(this).balance;
            
            (bool success,) = msg.sender.call{value: amount}("");
            require(success);
            
            require(address(this).balance >= balanceBefore, "Flash loan not repaid");
        }
    }
    """
    
    prompt = f"""Analyze this DeFi contract for security vulnerabilities. Pay special attention to:
1. Reentrancy attacks
2. Flash loan exploitation
3. State management issues
4. Economic attacks

Code:
{test_code}

Provide specific vulnerabilities and attack scenarios."""
    
    results = []
    
    for model in models:
        print(f"\nTesting {model}...")
        
        start = time.time()
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {'temperature': 0.1, 'num_predict': 800}
                },
                timeout=60
            )
            
            elapsed = time.time() - start
            
            if response.status_code == 200:
                result = response.json()['response']
                result_lower = result.lower()
                
                score = 0
                vulnerabilities_found = []
                
                # Check for reentrancy detection
                if 'reentrancy' in result_lower or 're-entrancy' in result_lower:
                    score += 25
                    vulnerabilities_found.append('reentrancy')
                
                # Check for flash loan exploitation
                if 'flash loan' in result_lower and ('exploit' in result_lower or 'attack' in result_lower):
                    score += 25
                    vulnerabilities_found.append('flash_loan_exploit')
                
                # Check for state management issues
                if 'state' in result_lower and ('before' in result_lower or 'after' in result_lower):
                    score += 20
                    vulnerabilities_found.append('state_management')
                
                # Check for economic attack understanding
                if any(term in result_lower for term in ['drain', 'steal', 'manipulate', 'economic']):
                    score += 15
                    vulnerabilities_found.append('economic_attack')
                
                # Check for fix suggestions
                if any(fix in result_lower for fix in ['nonreentrant', 'mutex', 'check-effects-interactions', 'cei']):
                    score += 15
                
                results.append({
                    'model': model,
                    'score': score,
                    'time': elapsed,
                    'vulnerabilities_found': vulnerabilities_found,
                    'response_length': len(result)
                })
                
                print(f"  Score: {score}/100")
                print(f"  Time: {elapsed:.2f}s")
                print(f"  Vulnerabilities found: {', '.join(vulnerabilities_found)}")
                
            else:
                results.append({'model': model, 'error': f"Status {response.status_code}"})
                print(f"  Error: Status {response.status_code}")
                
        except Exception as e:
            results.append({'model': model, 'error': str(e)})
            print(f"  Error: {str(e)}")
    
    return results

def main():
    print("SmartLLM Security Analysis Test")
    print("=" * 40)
    
    results = test_smartllm_models()
    
    with open('.claude/smartllm-test-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    valid_results = [r for r in results if 'error' not in r]
    if valid_results:
        best = max(valid_results, key=lambda x: x['score'])
        print(f"\nBest SmartLLM model: {best['model']}")
        print(f"Score: {best['score']}/100")

if __name__ == "__main__":
    main()