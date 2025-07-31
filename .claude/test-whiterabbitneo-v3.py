#!/usr/bin/env python3
"""
Test WhiteRabbitNeo V3 - potentially the new champion!
This is the most important test - V3 vs our current Ollama champion
"""

import json
import time
import requests

def test_whiterabbitneo_v3():
    """Test the V3 model with our proven test suite"""
    
    # Same exact tests we used for the Ollama champion
    test_cases = [
        {
            "name": "Classic Reentrancy Challenge",
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
            "expected_score": 100,  # Our Ollama champion got 100/100
            "difficulty": "basic"
        },
        {
            "name": "Complex Multi-Function Analysis",
            "code": """
            pragma solidity ^0.8.0;
            
            contract ComplexDeFi {
                mapping(address => uint256) public balances;
                mapping(address => uint256) public rewards;
                uint256 public totalLocked;
                address public owner;
                bool private _locked;
                
                modifier nonReentrant() {
                    require(!_locked, "Reentrant");
                    _locked = true;
                    _;
                    _locked = false;
                }
                
                constructor() { owner = msg.sender; }
                
                function deposit() external payable {
                    balances[msg.sender] += msg.value;
                    totalLocked += msg.value;
                    rewards[msg.sender] += msg.value / 100; // 1% reward
                }
                
                function withdraw(uint256 amount) external {
                    require(balances[msg.sender] >= amount, "Insufficient balance");
                    
                    balances[msg.sender] -= amount;
                    totalLocked -= amount;
                    
                    (bool success,) = msg.sender.call{value: amount}("");
                    require(success, "Transfer failed");
                }
                
                function claimRewards() external nonReentrant {
                    uint256 reward = rewards[msg.sender];
                    rewards[msg.sender] = 0;
                    
                    (bool success,) = msg.sender.call{value: reward}("");
                    require(success, "Reward transfer failed");
                }
                
                function emergencyWithdraw() external {
                    require(msg.sender == owner, "Only owner");
                    payable(owner).transfer(address(this).balance);
                }
            }
            """,
            "expected_score": 80,  # Complex case
            "difficulty": "advanced"
        }
    ]
    
    results = []
    total_start = time.time()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/2: {test_case['name']}")
        print(f"🎯 Target Score: {test_case['expected_score']}/100")
        print(f"⚡ Difficulty: {test_case['difficulty']}")
        
        prompt = f"""You are an expert smart contract security auditor. Analyze this Solidity code for security vulnerabilities.

Code:
{test_case['code']}

Provide detailed analysis including:
1. All security vulnerabilities found
2. Specific functions affected
3. Attack scenarios and impact
4. Severity assessment (Critical/High/Medium/Low)
5. Recommended fixes with code examples

Be thorough and technical."""

        start_time = time.time()
        
        try:
            response = requests.post(
                'http://localhost:1234/v1/chat/completions',
                headers={'Content-Type': 'application/json'},
                json={
                    'model': 'whiterabbitneo-v3-7b-i1',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.1,  # Consistent with Ollama tests
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
                
                print(f"⚡ Response time: {elapsed:.2f}s")
                print(f"📝 Response length: {len(content)} characters")
                
                # Detailed scoring (same system as Ollama tests)
                score = 0
                findings = []
                
                # Reentrancy detection (30 points)
                if 'reentrancy' in content_lower or 're-entrancy' in content_lower:
                    score += 30
                    findings.append('reentrancy')
                
                # Function-specific analysis (25 points)
                if 'withdraw' in content_lower and any(word in content_lower for word in ['vulnerable', 'issue', 'problem']):
                    score += 25
                    findings.append('function_analysis')
                
                # Understanding call-state issues (20 points)
                if any(phrase in content_lower for phrase in ['call', 'state', 'balance']) and 'before' in content_lower:
                    score += 20
                    findings.append('call_state_understanding')
                
                # Fix recommendations (15 points)
                if any(fix in content_lower for fix in ['nonreentrant', 'mutex', 'check-effects', 'cei', 'modifier']):
                    score += 15
                    findings.append('fix_recommendations')
                
                # Severity assessment (10 points)
                if any(sev in content_lower for sev in ['critical', 'high', 'medium', 'low', 'severe']):
                    score += 10
                    findings.append('severity_assessment')
                
                test_result = {
                    'test_name': test_case['name'],
                    'difficulty': test_case['difficulty'],
                    'score': score,
                    'expected_score': test_case['expected_score'],
                    'time': elapsed,
                    'findings': findings,
                    'efficiency': score / elapsed if elapsed > 0 else 0,
                    'response_preview': content[:500] + '...' if len(content) > 500 else content
                }
                
                results.append(test_result)
                
                # Performance vs expectation
                performance = "🔥 EXCEEDED" if score > test_case['expected_score'] else "✅ MET" if score >= test_case['expected_score'] else "⚠️ BELOW"
                
                print(f"🎯 Score: {score}/100 ({performance} expectations)")
                print(f"⚡ Efficiency: {score/elapsed:.2f} points/second")
                print(f"🔍 Findings: {', '.join(findings)}")
                print(f"\n📄 Analysis preview:\n{content[:400]}...")
                
            else:
                error_result = {
                    'test_name': test_case['name'],
                    'error': f"HTTP {response.status_code}",
                    'response': response.text[:200]
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
    
    total_time = time.time() - total_start
    return results, total_time

def championship_comparison(v3_results):
    """Compare V3 with our reigning Ollama champion"""
    
    print("\n" + "="*70)
    print("🏆 CHAMPIONSHIP MATCH: V3 vs OLLAMA CHAMPION")
    print("="*70)
    
    # Ollama Champion stats (from our previous testing)
    ollama_champion = {
        'name': 'whiterabbitneo:latest',
        'platform': 'Ollama',
        'size': '8.1 GB',
        'score': 100,
        'time': 12.51,
        'efficiency': 7.99
    }
    
    # Calculate V3 performance
    valid_results = [r for r in v3_results if 'error' not in r]
    if not valid_results:
        print("❌ No valid V3 results to compare")
        return
    
    v3_stats = {
        'name': 'whiterabbitneo-v3-7b-i1',
        'platform': 'LM Studio (GGUF)',
        'size': '~6 GB',
        'score': sum(r['score'] for r in valid_results) / len(valid_results),
        'time': sum(r['time'] for r in valid_results) / len(valid_results),
        'efficiency': sum(r['efficiency'] for r in valid_results) / len(valid_results)
    }
    
    print(f"\n🥊 **CONTENDER: {v3_stats['name']}**")
    print(f"   Platform: {v3_stats['platform']}")
    print(f"   Size: {v3_stats['size']}")
    print(f"   Avg Score: {v3_stats['score']:.1f}/100")
    print(f"   Avg Time: {v3_stats['time']:.2f}s")
    print(f"   Efficiency: {v3_stats['efficiency']:.2f} points/second")
    
    print(f"\n👑 **CHAMPION: {ollama_champion['name']}**")
    print(f"   Platform: {ollama_champion['platform']}")
    print(f"   Size: {ollama_champion['size']}")
    print(f"   Score: {ollama_champion['score']}/100")
    print(f"   Time: {ollama_champion['time']:.2f}s")
    print(f"   Efficiency: {ollama_champion['efficiency']:.2f} points/second")
    
    # Head-to-head comparison
    print(f"\n🥊 **HEAD-TO-HEAD COMPARISON:**")
    
    score_winner = "V3" if v3_stats['score'] > ollama_champion['score'] else "OLLAMA" if ollama_champion['score'] > v3_stats['score'] else "TIE"
    speed_winner = "V3" if v3_stats['time'] < ollama_champion['time'] else "OLLAMA"
    efficiency_winner = "V3" if v3_stats['efficiency'] > ollama_champion['efficiency'] else "OLLAMA"
    memory_winner = "V3"  # V3 is smaller
    
    print(f"   🎯 Accuracy: {score_winner} wins")
    print(f"   ⚡ Speed: {speed_winner} wins") 
    print(f"   🏃 Efficiency: {efficiency_winner} wins")
    print(f"   💾 Memory Usage: {memory_winner} wins")
    
    # Overall verdict
    wins = {'V3': 0, 'OLLAMA': 0}
    if score_winner == 'V3': wins['V3'] += 1
    elif score_winner == 'OLLAMA': wins['OLLAMA'] += 1
    
    if speed_winner == 'V3': wins['V3'] += 1
    else: wins['OLLAMA'] += 1
    
    if efficiency_winner == 'V3': wins['V3'] += 1
    else: wins['OLLAMA'] += 1
    
    wins['V3'] += 1  # Memory advantage
    
    print(f"\n🏆 **FINAL VERDICT:**")
    if wins['V3'] > wins['OLLAMA']:
        print("   🔥 NEW CHAMPION: WhiteRabbitNeo V3!")
        print("   🎊 V3 is the new recommended primary model for Slitheryn")
        print(f"   💡 Advantages: Smaller size ({v3_stats['size']} vs {ollama_champion['size']}), GGUF efficiency")
    elif wins['V3'] == wins['OLLAMA']:
        print("   ⚖️  It's a TIE! Both models are excellent")
        print("   💡 Choose based on preference: Ollama vs LM Studio")
    else:
        print("   👑 Ollama Champion retains the title")
        print("   💪 The original whiterabbitneo:latest remains supreme")
    
    # Practical recommendation
    print(f"\n💡 **PRACTICAL RECOMMENDATION:**")
    if v3_stats['efficiency'] > ollama_champion['efficiency'] * 0.9:  # Within 10%
        print("   ✅ V3 is competitive enough to consider switching")
        print("   🎯 Benefits: Smaller memory footprint, GGUF format efficiency")
    else:
        print("   🤔 Stick with Ollama champion unless you prefer LM Studio workflow")

def main():
    print("🐰 ULTIMATE CHAMPIONSHIP TEST: WhiteRabbitNeo V3")
    print("="*60)
    print("Testing: whiterabbitneo-v3-7b-i1 (~6GB)")
    print("Versus: whiterabbitneo:latest (Ollama, 8.1GB)")
    print("Stakes: Potential new Slitheryn champion!")
    print("-"*60)
    
    results, total_time = test_whiterabbitneo_v3()
    
    # Save results
    with open('.claude/whiterabbitneo-v3-championship-results.json', 'w') as f:
        json.dump({
            'results': results,
            'total_test_time': total_time,
            'model_info': {
                'name': 'whiterabbitneo-v3-7b-i1',
                'platform': 'LM Studio',
                'format': 'GGUF',
                'estimated_size': '~6GB'
            }
        }, f, indent=2)
    
    # Championship comparison
    championship_comparison(results)
    
    print(f"\n💾 Championship results saved to .claude/whiterabbitneo-v3-championship-results.json")
    print(f"⏱️  Total test time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()