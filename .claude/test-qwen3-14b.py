#!/usr/bin/env python3
"""
Test Qwen3-14B - the potential sweet spot model
Mid-size version of our 100/100 Ollama performer
"""

import json
import time
import requests

def test_qwen3_14b():
    """Test Qwen3-14B for security analysis"""
    
    # Same test suite for fair comparison
    test_cases = [
        {
            "name": "Reentrancy Vulnerability Test",
            "code": """
            contract VulnerableBank {
                mapping(address => uint) public balances;
                
                function withdraw() public {
                    uint amount = balances[msg.sender];
                    (bool sent, ) = msg.sender.call{value: amount}("");
                    require(sent, "Failed");
                    balances[msg.sender] = 0;
                }
            }
            """,
            "benchmark": "whiterabbitneo-v3 got 85/100 in 7.90s"
        },
        {
            "name": "Multi-Vulnerability DeFi Contract",
            "code": """
            pragma solidity ^0.8.0;
            
            contract TokenVault {
                mapping(address => uint256) public deposits;
                mapping(address => uint256) public withdrawalTimes;
                uint256 public constant WITHDRAWAL_DELAY = 1 days;
                address public owner;
                
                event Deposit(address user, uint256 amount);
                event Withdrawal(address user, uint256 amount);
                
                constructor() { owner = msg.sender; }
                
                function deposit() external payable {
                    require(msg.value > 0, "Must deposit something");
                    deposits[msg.sender] += msg.value;
                    emit Deposit(msg.sender, msg.value);
                }
                
                function requestWithdrawal() external {
                    require(deposits[msg.sender] > 0, "No deposits");
                    withdrawalTimes[msg.sender] = block.timestamp;
                }
                
                function withdraw(uint256 amount) external {
                    require(deposits[msg.sender] >= amount, "Insufficient balance");
                    require(block.timestamp >= withdrawalTimes[msg.sender] + WITHDRAWAL_DELAY, "Too early");
                    
                    deposits[msg.sender] -= amount;
                    
                    (bool success,) = msg.sender.call{value: amount}("");
                    require(success, "Transfer failed");
                    
                    emit Withdrawal(msg.sender, amount);
                }
                
                function emergencyDrain() external {
                    require(msg.sender == owner);
                    payable(owner).transfer(address(this).balance);
                }
                
                function changeOwner(address newOwner) external {
                    require(msg.sender == owner);
                    owner = newOwner;
                }
            }
            """,
            "benchmark": "Should find multiple issues: reentrancy, access control, time manipulation"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/{len(test_cases)}: {test_case['name']}")
        print(f"📊 Benchmark: {test_case.get('benchmark', 'N/A')}")
        
        prompt = f"""You are an expert smart contract security auditor. Analyze this Solidity code for vulnerabilities.

Code to analyze:
{test_case['code']}

Provide comprehensive analysis:
1. All security vulnerabilities found
2. Specific functions and lines affected  
3. Attack scenarios with step-by-step exploitation
4. Severity levels (Critical/High/Medium/Low)
5. Detailed fix recommendations with code examples
6. Any secure patterns you notice

Be thorough, technical, and specific."""

        start_time = time.time()
        
        try:
            response = requests.post(
                'http://localhost:1234/v1/chat/completions',
                headers={'Content-Type': 'application/json'},
                json={
                    'model': 'qwen/qwen3-14b',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.1,
                    'max_tokens': 2000,
                    'stream': False
                },
                timeout=120
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                content_lower = content.lower()
                
                print(f"⏱️  Response time: {elapsed:.2f}s")
                print(f"📝 Response length: {len(content)} characters")
                
                # Comprehensive scoring system
                score = 0
                findings = []
                details = {}
                
                # Core vulnerability detection (50 points total)
                if 'reentrancy' in content_lower or 're-entrancy' in content_lower:
                    score += 25
                    findings.append('reentrancy')
                    details['reentrancy'] = True
                
                if any(term in content_lower for term in ['access control', 'owner', 'unauthorized']):
                    score += 15
                    findings.append('access_control')
                    details['access_control'] = True
                
                if any(term in content_lower for term in ['timestamp', 'time', 'block.timestamp']):
                    score += 10
                    findings.append('time_manipulation')
                    details['time_issues'] = True
                
                # Analysis quality (30 points total)
                if any(phrase in content_lower for phrase in ['call', 'state', 'balance']) and 'before' in content_lower:
                    score += 15
                    findings.append('understands_call_order')
                
                if 'withdraw' in content_lower and any(word in content_lower for word in ['vulnerable', 'issue', 'problem']):
                    score += 15
                    findings.append('function_specific_analysis')
                
                # Recommendations and fixes (20 points total)
                if any(fix in content_lower for fix in ['nonreentrant', 'mutex', 'check-effects', 'cei']):
                    score += 10
                    findings.append('reentrancy_fixes')
                
                if 'modifier' in content_lower or 'require(' in content_lower:
                    score += 10
                    findings.append('code_examples')
                
                test_result = {
                    'test_name': test_case['name'],
                    'score': score,
                    'time': elapsed,
                    'findings': findings,
                    'efficiency': score / elapsed if elapsed > 0 else 0,
                    'details': details,
                    'response_length': len(content),
                    'response_preview': content[:600] + '...' if len(content) > 600 else content
                }
                
                results.append(test_result)
                
                print(f"🎯 Score: {score}/100")
                print(f"⚡ Efficiency: {score/elapsed:.2f} points/second")
                print(f"🔍 Findings: {', '.join(findings)}")
                print(f"\n📋 Analysis preview:\n{content[:500]}...")
                
            else:
                error_result = {
                    'test_name': test_case['name'],
                    'error': f"HTTP {response.status_code}",
                    'response_text': response.text[:300]
                }
                results.append(error_result)
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            error_result = {
                'test_name': test_case['name'],
                'error': str(e)
            }
            results.append(error_result)
            print(f"❌ Exception: {str(e)}")
    
    return results

def compare_with_current_leaders(qwen14b_results):
    """Compare Qwen3-14B with our current top models"""
    
    print("\n" + "="*70)
    print("🏆 QWEN3-14B vs CURRENT LEADERS")
    print("="*70)
    
    # Current leaderboard
    current_leaders = [
        {
            'name': 'whiterabbitneo-v3-7b-i1',
            'platform': 'LM Studio',
            'size': '6GB',
            'avg_score': 92.5,
            'avg_time': 11.27,
            'efficiency': 8.79,
            'status': '👑 Current Champion'
        },
        {
            'name': 'phi4-reasoning:latest', 
            'platform': 'Ollama',
            'size': '11GB',
            'avg_score': 100.0,
            'avg_time': 27.20,
            'efficiency': 3.68,
            'status': '🧠 Reasoning Expert'
        },
        {
            'name': 'qwen3:30b-a3b',
            'platform': 'Ollama', 
            'size': '18GB',
            'avg_score': 100.0,
            'avg_time': 34.11,
            'efficiency': 2.93,
            'status': '📚 Comprehensive Analysis'
        }
    ]
    
    # Calculate Qwen3-14B performance
    valid_results = [r for r in qwen14b_results if 'error' not in r]
    if not valid_results:
        print("❌ No valid results to compare")
        return
    
    qwen14b_stats = {
        'name': 'qwen3-14b',
        'platform': 'LM Studio',
        'size': '~8GB',  # Estimated for Q4_K_M
        'avg_score': sum(r['score'] for r in valid_results) / len(valid_results),
        'avg_time': sum(r['time'] for r in valid_results) / len(valid_results),
        'efficiency': sum(r['efficiency'] for r in valid_results) / len(valid_results),
        'status': '🆕 New Contender'
    }
    
    print(f"\n🆕 **NEW CHALLENGER: {qwen14b_stats['name']}**")
    print(f"   Platform: {qwen14b_stats['platform']}")
    print(f"   Size: {qwen14b_stats['size']}")
    print(f"   Avg Score: {qwen14b_stats['avg_score']:.1f}/100")
    print(f"   Avg Time: {qwen14b_stats['avg_time']:.2f}s")
    print(f"   Efficiency: {qwen14b_stats['efficiency']:.2f} points/second")
    
    print(f"\n🥊 **VERSUS CURRENT LEADERS:**")
    for leader in current_leaders:
        print(f"\n   vs {leader['name']} ({leader['status']})")
        print(f"      Size: {qwen14b_stats['size']} vs {leader['size']}")
        
        # Score comparison
        score_diff = qwen14b_stats['avg_score'] - leader['avg_score']
        score_result = "🟢 BETTER" if score_diff > 2 else "🟡 SIMILAR" if abs(score_diff) <= 2 else "🔴 WORSE"
        print(f"      Accuracy: {score_result} ({qwen14b_stats['avg_score']:.1f} vs {leader['avg_score']:.1f})")
        
        # Speed comparison
        time_diff = leader['avg_time'] - qwen14b_stats['avg_time']  # Positive means Qwen is faster
        speed_result = "🟢 FASTER" if time_diff > 2 else "🟡 SIMILAR" if abs(time_diff) <= 2 else "🔴 SLOWER"
        print(f"      Speed: {speed_result} ({qwen14b_stats['avg_time']:.1f}s vs {leader['avg_time']:.1f}s)")
        
        # Efficiency comparison
        eff_diff = qwen14b_stats['efficiency'] - leader['efficiency']
        eff_result = "🟢 BETTER" if eff_diff > 0.5 else "🟡 SIMILAR" if abs(eff_diff) <= 0.5 else "🔴 WORSE"
        print(f"      Efficiency: {eff_result} ({qwen14b_stats['efficiency']:.2f} vs {leader['efficiency']:.2f})")
    
    # Overall position assessment
    print(f"\n🎯 **OVERALL ASSESSMENT:**")
    
    # Compare with champion
    champion = current_leaders[0]
    vs_champion = {
        'score': qwen14b_stats['avg_score'] >= champion['avg_score'] - 5,  # Within 5 points
        'speed': qwen14b_stats['avg_time'] <= champion['avg_time'] + 5,     # Within 5 seconds
        'efficiency': qwen14b_stats['efficiency'] >= champion['efficiency'] - 1  # Within 1 point
    }
    
    wins = sum(vs_champion.values())
    
    if wins >= 2:
        print("   🏆 STRONG CONTENDER - Could challenge for the championship!")
        print("   💡 Consider as primary or co-primary model")
        
        # Specific recommendation
        if qwen14b_stats['efficiency'] > champion['efficiency']:
            print("   🔥 RECOMMENDATION: New primary model candidate!")
        else:
            print("   ⚖️  RECOMMENDATION: Excellent secondary model")
            
    elif wins == 1:
        print("   ✅ SOLID PERFORMER - Good addition to the model lineup")
        print("   💡 Consider for specialized use cases")
    else:
        print("   ⚠️  DECENT - But current leaders are better")
        print("   🤔 Stick with existing models unless you prefer LM Studio")
    
    # Memory efficiency analysis
    size_to_performance = qwen14b_stats['avg_score'] / 8  # Assuming 8GB
    print(f"\n💾 **MEMORY EFFICIENCY:**")
    print(f"   Score per GB: {size_to_performance:.1f}")
    
    if size_to_performance > 11:  # WhiteRabbit V3 gets ~15.4
        print("   🟢 EXCELLENT memory efficiency")
    elif size_to_performance > 8:
        print("   🟡 GOOD memory efficiency")
    else:
        print("   🔴 Poor memory efficiency - consider smaller models")

def main():
    print("🧠 TESTING QWEN3-14B: The Sweet Spot Model?")
    print("="*60)
    print("Model: qwen/qwen3-14b (~8GB)")
    print("Theory: Mid-size version of our 100/100 Ollama performer")
    print("Goal: Find the perfect size/performance balance")
    print("-"*60)
    
    results = test_qwen3_14b()
    
    # Save results
    with open('.claude/qwen3-14b-test-results.json', 'w') as f:
        json.dump({
            'model_info': {
                'name': 'qwen/qwen3-14b',
                'platform': 'LM Studio',
                'format': 'GGUF',
                'estimated_size': '~8GB'
            },
            'test_results': results,
            'timestamp': time.time()
        }, f, indent=2)
    
    # Compare with leaders
    compare_with_current_leaders(results)
    
    print(f"\n💾 Results saved to .claude/qwen3-14b-test-results.json")

if __name__ == "__main__":
    main()