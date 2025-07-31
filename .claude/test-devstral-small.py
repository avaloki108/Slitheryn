#!/usr/bin/env python3
"""
Test Devstral Small 2507 - the lightweight code-focused model
"""

import json
import time
import requests

def test_devstral_small():
    """Test Devstral Small with security analysis"""
    
    # Quick reentrancy test
    quick_test = """
    contract Test {
        mapping(address => uint) balances;
        
        function withdraw() public {
            uint amt = balances[msg.sender];
            msg.sender.call{value: amt}("");
            balances[msg.sender] = 0;
        }
    }
    """
    
    # More complex test
    complex_test = """
    pragma solidity ^0.8.0;
    
    contract TokenSale {
        mapping(address => uint256) public contributions;
        mapping(address => uint256) public tokens;
        uint256 public rate = 100; // tokens per ETH
        address public owner;
        bool public saleActive = true;
        
        constructor() {
            owner = msg.sender;
        }
        
        function buyTokens() public payable {
            require(saleActive, "Sale not active");
            require(msg.value > 0, "Must send ETH");
            
            uint256 tokenAmount = msg.value * rate;
            tokens[msg.sender] += tokenAmount;
            contributions[msg.sender] += msg.value;
        }
        
        function withdraw() public {
            require(msg.sender == owner, "Only owner");
            payable(owner).transfer(address(this).balance);
        }
        
        function emergencyStop() public {
            require(msg.sender == owner, "Only owner");
            saleActive = false;
            
            // Refund all contributors
            for (uint i = 0; i < 1000; i++) {
                // This would need actual contributor tracking
                break;
            }
        }
    }
    """
    
    test_cases = [
        {
            "name": "Quick Reentrancy Check",
            "code": quick_test,
            "focus": "Basic vulnerability detection speed",
            "expected": "reentrancy"
        },
        {
            "name": "Token Sale Security Review", 
            "code": complex_test,
            "focus": "Multiple vulnerability types",
            "expected": "access control, gas limit, integer overflow potential"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print(f"Focus: {test_case['focus']}")
        
        prompt = f"""Analyze this Solidity smart contract for security vulnerabilities:

{test_case['code']}

Find:
1. Security vulnerabilities
2. Gas optimization issues  
3. Best practice violations
4. Potential attack vectors

Be concise but thorough."""

        start_time = time.time()
        
        try:
            response = requests.post(
                'http://localhost:1234/v1/chat/completions',
                headers={'Content-Type': 'application/json'},
                json={
                    'model': 'mistralai/devstral-small-2507',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.1,
                    'max_tokens': 1000,
                    'stream': False
                },
                timeout=60
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                content_lower = content.lower()
                
                print(f"⚡ Response time: {elapsed:.2f}s")
                print(f"📝 Response length: {len(content)} chars")
                
                # Score the analysis
                score = 0
                findings = []
                
                # Basic vulnerability detection
                if 'reentrancy' in content_lower:
                    score += 25
                    findings.append('reentrancy')
                    
                if any(term in content_lower for term in ['access control', 'owner', 'permission']):
                    score += 20
                    findings.append('access_control')
                    
                if any(term in content_lower for term in ['gas', 'loop', 'dos']):
                    score += 15
                    findings.append('gas_issues')
                    
                if any(term in content_lower for term in ['overflow', 'underflow', 'safeMath']):
                    score += 15
                    findings.append('arithmetic')
                    
                if any(term in content_lower for term in ['check', 'require', 'validation']):
                    score += 10
                    findings.append('validation')
                    
                if any(term in content_lower for term in ['fix', 'recommend', 'should']):
                    score += 15
                    findings.append('recommendations')
                
                test_result = {
                    'test_name': test_case['name'],
                    'score': score,
                    'time': elapsed,
                    'findings': findings,
                    'efficiency': score / elapsed if elapsed > 0 else 0,
                    'response_preview': content[:400] + '...' if len(content) > 400 else content,
                    'model_size': '~3GB'
                }
                
                results.append(test_result)
                
                print(f"🎯 Score: {score}/100")
                print(f"⚡ Efficiency: {score/elapsed:.2f} points/second")
                print(f"🔍 Findings: {', '.join(findings)}")
                print(f"\n📄 Preview:\n{content[:300]}...")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                results.append({'test_name': test_case['name'], 'error': f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({'test_name': test_case['name'], 'error': str(e)})
    
    return results

def compare_lightweight_models(devstral_results):
    """Compare Devstral Small with other lightweight options"""
    
    print("\n" + "="*60)
    print("⚡ LIGHTWEIGHT MODEL COMPARISON")
    print("="*60)
    
    # Calculate Devstral Small performance
    valid_results = [r for r in devstral_results if 'error' not in r]
    if valid_results:
        avg_score = sum(r['score'] for r in valid_results) / len(valid_results)
        avg_time = sum(r['time'] for r in valid_results) / len(valid_results)
        avg_efficiency = sum(r['efficiency'] for r in valid_results) / len(valid_results)
        
        print(f"\n🚀 **Devstral Small 2507** (~3GB)")
        print(f"   Average Score: {avg_score:.1f}/100")
        print(f"   Average Time: {avg_time:.2f}s")
        print(f"   Efficiency: {avg_efficiency:.2f} points/second") 
        print(f"   Memory: ~3GB (VERY lightweight)")
        
        # Compare with our champions
        competitors = {
            'whiterabbitneo:latest': {'size': '8.1GB', 'score': 100, 'time': 12.51, 'eff': 7.99},
            'smartllm:latest': {'size': '8.5GB', 'score': 85, 'time': 22.96, 'eff': 3.70},
            'deepseek-r1:7b': {'size': '8.1GB', 'score': 20, 'time': 15.45, 'eff': 1.29}
        }
        
        print(f"\n🥊 **Versus Similar-Sized Models:**")
        for model, stats in competitors.items():
            if float(stats['size'].replace('GB', '')) <= 10:  # Similar size range
                comparison = "🟢 BETTER" if avg_efficiency > stats['eff'] else "🔴 WORSE"
                print(f"   vs {model} ({stats['size']}): {comparison}")
                print(f"      Competitor: {stats['score']}/100, {stats['time']:.2f}s, {stats['eff']:.2f} eff")
        
        print(f"\n💡 **Key Advantages of Devstral Small:**")
        advantages = []
        if avg_time < 15:
            advantages.append("⚡ Very fast response times")
        if avg_efficiency > 2.0:
            advantages.append("🎯 Good efficiency for its size")
        advantages.append("💾 Minimal memory footprint (3GB)")
        advantages.append("⚙️  Code-specialized training")
        
        for advantage in advantages:
            print(f"   {advantage}")
        
        print(f"\n🎯 **Use Case Recommendations:**")
        if avg_score >= 70 and avg_time <= 10:
            print("   ✅ Excellent for real-time analysis during development")
            print("   ✅ Perfect for CI/CD pipelines with memory constraints")
            print("   ✅ Good for quick pre-commit hooks")
        elif avg_score >= 50:
            print("   ⚠️  Decent for basic vulnerability screening")
            print("   💡 Could be used as first-pass filter before deeper analysis")
        else:
            print("   ❌ Not recommended as primary security analysis tool")
            print("   🤔 Consider for code quality checks only")

def main():
    print("⚡ Testing Devstral Small 2507 - Lightweight Code Analysis")
    print("="*65)
    print("Model: mistralai/devstral-small-2507 (~3GB)")
    print("Focus: Speed vs accuracy trade-off analysis")
    print("-"*65)
    
    results = test_devstral_small()
    
    # Save results
    with open('.claude/devstral-small-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Compare with other lightweight models
    compare_lightweight_models(results)
    
    print(f"\n💾 Results saved to .claude/devstral-small-results.json")
    
    # Final recommendation
    valid_results = [r for r in results if 'error' not in r]
    if valid_results:
        avg_efficiency = sum(r['efficiency'] for r in valid_results) / len(valid_results)
        
        print(f"\n🎯 **FINAL VERDICT FOR SLITHERYN:**")
        if avg_efficiency > 5.0:
            print("   🏆 EXCELLENT lightweight option - consider for fast scanning!")
        elif avg_efficiency > 3.0:
            print("   ✅ GOOD lightweight option - useful for quick checks")
        elif avg_efficiency > 1.5:
            print("   ⚠️  DECENT but not better than existing options")
        else:
            print("   ❌ NOT RECOMMENDED - stick with current models")

if __name__ == "__main__":
    main()