#!/usr/bin/env python3
"""
Test the loaded Absolute Zero Reasoner-Coder model for security analysis
"""

import json
import time
import requests

def test_absolute_zero_security():
    """Test the Absolute Zero model with our security test suite"""
    
    # Same test case as used for Ollama models for fair comparison
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
    
    # Also test a more complex case
    complex_test = """
    contract DeFiVault {
        mapping(address => uint256) public balances;
        uint256 public totalSupply;
        bool private locked;
        
        modifier nonReentrant() {
            require(!locked, "Reentrant call");
            locked = true;
            _;
            locked = false;
        }
        
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
        
        function emergencyWithdraw() public nonReentrant {
            uint256 amount = balances[msg.sender];
            balances[msg.sender] = 0;
            totalSupply -= amount;
            
            (bool success,) = msg.sender.call{value: amount}("");
            require(success);
        }
    }
    """
    
    test_cases = [
        {
            "name": "Simple Reentrancy Test",
            "code": test_code,
            "expected_vulns": ["reentrancy"],
            "difficulty": "basic"
        },
        {
            "name": "Complex DeFi Analysis", 
            "code": complex_test,
            "expected_vulns": ["reentrancy in withdraw", "proper protection in emergencyWithdraw"],
            "difficulty": "advanced"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"Difficulty: {test_case['difficulty']}")
        
        prompt = f"""You are an expert smart contract security auditor. Analyze this Solidity code for security vulnerabilities.

Code to analyze:
{test_case['code']}

Provide a comprehensive security analysis including:
1. All vulnerabilities found (be specific about which functions)
2. Severity assessment for each vulnerability  
3. Attack scenarios and potential impact
4. Recommended fixes with code examples
5. Any secure patterns you notice

Be technical, specific, and thorough in your analysis."""

        start_time = time.time()
        
        try:
            response = requests.post(
                'http://localhost:1234/v1/chat/completions',
                headers={'Content-Type': 'application/json'},
                json={
                    'model': 'absolute_zero_reasoner-coder-14b',
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.1,  # Low temperature for consistent analysis
                    'max_tokens': 1500,
                    'stream': False
                },
                timeout=90
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                content_lower = content.lower()
                
                print(f"⏱️  Response time: {elapsed:.2f}s")
                print(f"📝 Response length: {len(content)} characters")
                
                # Analyze the response quality
                score = 0
                findings = []
                
                # Reentrancy detection (30 points)
                if 'reentrancy' in content_lower or 're-entrancy' in content_lower:
                    score += 30
                    findings.append('reentrancy_detected')
                
                # Specific function analysis (20 points)
                if 'withdraw' in content_lower and ('vulnerable' in content_lower or 'issue' in content_lower):
                    score += 20
                    findings.append('function_specific_analysis')
                    
                # Understanding of call-state issue (20 points)
                if any(term in content_lower for term in ['call', 'state', 'balance']) and 'before' in content_lower:
                    score += 20
                    findings.append('understands_call_state_issue')
                
                # Fix suggestions (15 points)
                if any(fix in content_lower for fix in ['nonreentrant', 'mutex', 'check-effects-interactions', 'cei']):
                    score += 15
                    findings.append('provides_fixes')
                
                # Severity assessment (10 points)
                if any(sev in content_lower for sev in ['high', 'critical', 'severe', 'medium', 'low']):
                    score += 10
                    findings.append('severity_assessment')
                
                # Code examples in fixes (5 points)
                if 'modifier' in content_lower or 'require(' in content_lower:
                    score += 5
                    findings.append('code_examples')
                
                test_result = {
                    'test_name': test_case['name'],
                    'difficulty': test_case['difficulty'],
                    'score': score,
                    'time': elapsed,
                    'findings': findings,
                    'response_preview': content[:500] + '...' if len(content) > 500 else content,
                    'full_response': content
                }
                
                results.append(test_result)
                
                print(f"🎯 Score: {score}/100")
                print(f"🔍 Findings: {', '.join(findings)}")
                print(f"📊 Efficiency: {score/elapsed:.2f} points/second")
                print(f"\n📋 Response preview:\n{content[:300]}...")
                
            else:
                error_result = {
                    'test_name': test_case['name'],
                    'error': f"HTTP {response.status_code}",
                    'response': response.text
                }
                results.append(error_result)
                print(f"❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            error_result = {
                'test_name': test_case['name'], 
                'error': str(e)
            }
            results.append(error_result)
            print(f"❌ Error: {str(e)}")
    
    return results

def compare_with_ollama_champions(absolute_zero_results):
    """Compare Absolute Zero results with our Ollama champions"""
    
    # Our Ollama champion results for comparison
    ollama_champions = {
        'whiterabbitneo:latest': {'score': 100, 'time': 12.51, 'size': '8.1 GB'},
        'phi4-reasoning:latest': {'score': 100, 'time': 27.20, 'size': '11 GB'},
        'smartllm:latest': {'score': 85, 'time': 22.96, 'size': '8.5 GB'}
    }
    
    print("\n" + "="*60)
    print("🏆 COMPARISON WITH OLLAMA CHAMPIONS")
    print("="*60)
    
    # Calculate Absolute Zero average performance
    valid_results = [r for r in absolute_zero_results if 'error' not in r]
    if valid_results:
        avg_score = sum(r['score'] for r in valid_results) / len(valid_results)
        avg_time = sum(r['time'] for r in valid_results) / len(valid_results)
        
        print(f"\n🤖 **Absolute_Zero_Reasoner-Coder-14B** (~10 GB)")
        print(f"   Average Score: {avg_score:.1f}/100")
        print(f"   Average Time: {avg_time:.2f}s")
        print(f"   Efficiency: {avg_score/avg_time:.2f} points/second")
        
        print(f"\n🥊 **Versus Ollama Champions:**")
        for model, stats in ollama_champions.items():
            efficiency = stats['score'] / stats['time']
            comparison = "🟢 BETTER" if avg_score/avg_time > efficiency else "🔴 WORSE"
            print(f"   vs {model}: {comparison}")
            print(f"      Ollama: {stats['score']}/100, {stats['time']:.2f}s, {efficiency:.2f} eff")
        
        # Overall assessment
        best_ollama_efficiency = max(stats['score']/stats['time'] for stats in ollama_champions.values())
        absolute_zero_efficiency = avg_score / avg_time
        
        print(f"\n🎯 **VERDICT:**")
        if absolute_zero_efficiency > best_ollama_efficiency:
            print("   ✅ Absolute Zero Reasoner-Coder is the NEW CHAMPION!")
            print("   🔥 Recommended as primary model for Slitheryn")
        elif abs(absolute_zero_efficiency - best_ollama_efficiency) < 0.5:
            print("   ⚖️  Absolute Zero performs similarly to top Ollama models")
            print("   💡 Consider it as a strong alternative, especially for complex analysis")
        else:
            print("   📉 Absolute Zero doesn't beat the Ollama champions")
            print("   🤔 Stick with whiterabbitneo:latest for now")

def main():
    print("🧠 Testing Absolute Zero Reasoner-Coder-14B for Security Analysis")
    print("="*70)
    
    results = test_absolute_zero_security()
    
    # Save detailed results
    with open('.claude/absolute-zero-test-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Compare with our Ollama champions
    compare_with_ollama_champions(results)
    
    print(f"\n💾 Detailed results saved to .claude/absolute-zero-test-results.json")

if __name__ == "__main__":
    main()