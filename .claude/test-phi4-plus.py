#!/usr/bin/env python3
"""
Test microsoft/phi-4-reasoning-plus vs our Ollama phi4-reasoning champion
Championship match for the reasoning crown
"""

import json
import time
import requests

def test_phi4_plus():
    """Test the LM Studio Phi-4 Plus model for security analysis"""
    
    # Same exact tests we used for the Ollama champion
    test_cases = [
        {
            "name": "Classic Reentrancy Analysis",
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
            "benchmark": "Ollama phi4-reasoning got 100/100",
            "focus": "Basic vulnerability detection"
        },
        {
            "name": "Complex Reasoning Challenge", 
            "code": """
            pragma solidity ^0.8.0;
            
            contract GovernanceVault {
                mapping(address => uint256) public stakes;
                mapping(address => uint256) public votingPower;
                mapping(uint256 => Proposal) public proposals;
                uint256 public proposalCounter;
                uint256 public constant MIN_STAKE = 1000;
                uint256 public constant VOTING_PERIOD = 7 days;
                
                struct Proposal {
                    address proposer;
                    string description;
                    uint256 votesFor;
                    uint256 votesAgainst;
                    uint256 startTime;
                    bool executed;
                    bytes callData;
                }
                
                function stake() external payable {
                    require(msg.value >= MIN_STAKE, "Insufficient stake");
                    stakes[msg.sender] += msg.value;
                    votingPower[msg.sender] = stakes[msg.sender] / MIN_STAKE;
                }
                
                function createProposal(string memory description, bytes memory callData) external {
                    require(votingPower[msg.sender] > 0, "No voting power");
                    
                    proposals[proposalCounter] = Proposal({
                        proposer: msg.sender,
                        description: description,
                        votesFor: 0,
                        votesAgainst: 0,
                        startTime: block.timestamp,
                        executed: false,
                        callData: callData
                    });
                    
                    proposalCounter++;
                }
                
                function vote(uint256 proposalId, bool support) external {
                    Proposal storage proposal = proposals[proposalId];
                    require(block.timestamp < proposal.startTime + VOTING_PERIOD, "Voting ended");
                    require(votingPower[msg.sender] > 0, "No voting power");
                    
                    uint256 power = votingPower[msg.sender];
                    
                    if (support) {
                        proposal.votesFor += power;
                    } else {
                        proposal.votesAgainst += power;
                    }
                }
                
                function executeProposal(uint256 proposalId) external {
                    Proposal storage proposal = proposals[proposalId];
                    require(block.timestamp >= proposal.startTime + VOTING_PERIOD, "Voting active");
                    require(!proposal.executed, "Already executed");
                    require(proposal.votesFor > proposal.votesAgainst, "Proposal failed");
                    
                    proposal.executed = true;
                    
                    (bool success,) = address(this).call(proposal.callData);
                    require(success, "Execution failed");
                }
                
                function emergencyWithdraw() external {
                    uint256 amount = stakes[msg.sender];
                    stakes[msg.sender] = 0;
                    votingPower[msg.sender] = 0;
                    
                    (bool success,) = msg.sender.call{value: amount}("");
                    require(success, "Withdrawal failed");
                }
            }
            """,
            "benchmark": "Complex reasoning test - governance vulnerabilities",
            "focus": "Multi-step attack reasoning, governance exploits"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/{len(test_cases)}: {test_case['name']}")
        print(f"🎯 Focus: {test_case['focus']}")
        print(f"📊 Benchmark: {test_case['benchmark']}")
        
        prompt = f"""You are an expert smart contract security auditor with advanced reasoning capabilities. Analyze this Solidity code for vulnerabilities.

Code:
{test_case['code']}

Provide comprehensive analysis with step-by-step reasoning:

1. **Vulnerability Identification**: What specific vulnerabilities exist?
2. **Root Cause Analysis**: Why do these vulnerabilities exist?
3. **Attack Vector Reasoning**: How would an attacker exploit these?
4. **Step-by-Step Exploitation**: Detailed attack sequence
5. **Impact Assessment**: What damage could be done?
6. **Fix Recommendations**: Specific code changes needed
7. **Prevention Strategy**: How to avoid similar issues

Use logical reasoning throughout your analysis. Show your thinking process."""

        start_time = time.time()
        
        try:
            response = requests.post(
                'http://localhost:1234/v1/chat/completions',
                headers={'Content-Type': 'application/json'},
                json={
                    'model': 'microsoft/phi-4-reasoning-plus',
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
                
                # Advanced reasoning-focused scoring
                score = 0
                reasoning_indicators = []
                
                # Core vulnerability detection (30 points)
                if 'reentrancy' in content_lower or 're-entrancy' in content_lower:
                    score += 15
                    reasoning_indicators.append('reentrancy_detected')
                
                if any(term in content_lower for term in ['governance', 'voting', 'proposal']):
                    score += 15
                    reasoning_indicators.append('governance_understanding')
                
                # Reasoning quality indicators (40 points)
                reasoning_keywords = [
                    ('step-by-step', 10, 'systematic_analysis'),
                    ('because', 5, 'causal_reasoning'),
                    ('therefore', 5, 'logical_conclusion'),
                    ('root cause', 10, 'root_cause_analysis'),
                    ('attack sequence', 10, 'attack_methodology')
                ]
                
                for keyword, points, indicator in reasoning_keywords:
                    if keyword in content_lower:
                        score += points
                        reasoning_indicators.append(indicator)
                
                # Technical depth (20 points)
                if any(term in content_lower for term in ['call', 'state', 'balance']) and 'before' in content_lower:
                    score += 10
                    reasoning_indicators.append('technical_understanding')
                
                if any(term in content_lower for term in ['block.timestamp', 'voting period', 'calldata']):
                    score += 10
                    reasoning_indicators.append('context_awareness')
                
                # Fix quality (10 points)
                if any(fix in content_lower for fix in ['nonreentrant', 'modifier', 'access control', 'timelock']):
                    score += 10
                    reasoning_indicators.append('quality_fixes')
                
                test_result = {
                    'test_name': test_case['name'],
                    'score': score,
                    'time': elapsed,
                    'reasoning_indicators': reasoning_indicators,
                    'reasoning_score': len([r for r in reasoning_indicators if 'reasoning' in r or 'analysis' in r]),
                    'efficiency': score / elapsed if elapsed > 0 else 0,
                    'response_preview': content[:500] + '...' if len(content) > 500 else content,
                    'full_response_length': len(content)
                }
                
                results.append(test_result)
                
                print(f"🎯 Score: {score}/100")
                print(f"🧠 Reasoning Quality: {test_result['reasoning_score']}/5")
                print(f"⚡ Efficiency: {score/elapsed:.2f} points/second")
                print(f"🔍 Reasoning Indicators: {', '.join(reasoning_indicators)}")
                print(f"\n📋 Analysis preview:\n{content[:400]}...")
                
            else:
                error_result = {
                    'test_name': test_case['name'],
                    'error': f"HTTP {response.status_code}",
                    'response_text': response.text[:200]
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

def championship_comparison(phi4_plus_results):
    """Compare Phi-4 Plus with our Ollama champion"""
    
    print("\n" + "="*70)
    print("🏆 PHI-4 REASONING CHAMPIONSHIP")
    print("="*70)
    
    # Ollama champion stats
    ollama_phi4 = {
        'name': 'phi4-reasoning:latest',
        'platform': 'Ollama',
        'size': '11GB',
        'score': 100,
        'time': 27.20,
        'efficiency': 3.68,
        'status': '👑 Current Reasoning Champion'
    }
    
    # Calculate Phi-4 Plus performance
    valid_results = [r for r in phi4_plus_results if 'error' not in r]
    if not valid_results:
        print("❌ No valid results to compare")
        return
    
    phi4_plus_stats = {
        'name': 'microsoft/phi-4-reasoning-plus',
        'platform': 'LM Studio',
        'size': '~8GB',
        'score': sum(r['score'] for r in valid_results) / len(valid_results),
        'time': sum(r['time'] for r in valid_results) / len(valid_results),
        'efficiency': sum(r['efficiency'] for r in valid_results) / len(valid_results),
        'reasoning_quality': sum(r['reasoning_score'] for r in valid_results) / len(valid_results),
        'status': '🆕 Enhanced Plus Version'
    }
    
    print(f"\n🆕 **CHALLENGER: {phi4_plus_stats['name']}**")
    print(f"   Platform: {phi4_plus_stats['platform']}")
    print(f"   Size: {phi4_plus_stats['size']}")
    print(f"   Avg Score: {phi4_plus_stats['score']:.1f}/100")
    print(f"   Avg Time: {phi4_plus_stats['time']:.2f}s")
    print(f"   Efficiency: {phi4_plus_stats['efficiency']:.2f} points/second")
    print(f"   Reasoning Quality: {phi4_plus_stats['reasoning_quality']:.1f}/5")
    
    print(f"\n👑 **CHAMPION: {ollama_phi4['name']}**")
    print(f"   Platform: {ollama_phi4['platform']}")
    print(f"   Size: {ollama_phi4['size']}")
    print(f"   Score: {ollama_phi4['score']}/100")
    print(f"   Time: {ollama_phi4['time']:.2f}s")
    print(f"   Efficiency: {ollama_phi4['efficiency']:.2f} points/second")
    
    # Head-to-head comparison
    print(f"\n🥊 **HEAD-TO-HEAD BATTLE:**")
    
    # Accuracy
    accuracy_winner = "PLUS" if phi4_plus_stats['score'] > ollama_phi4['score'] else "OLLAMA" if ollama_phi4['score'] > phi4_plus_stats['score'] else "TIE"
    print(f"   🎯 Accuracy: {accuracy_winner} wins ({phi4_plus_stats['score']:.1f} vs {ollama_phi4['score']})")
    
    # Speed
    speed_winner = "PLUS" if phi4_plus_stats['time'] < ollama_phi4['time'] else "OLLAMA"
    print(f"   ⚡ Speed: {speed_winner} wins ({phi4_plus_stats['time']:.1f}s vs {ollama_phi4['time']:.1f}s)")
    
    # Efficiency
    efficiency_winner = "PLUS" if phi4_plus_stats['efficiency'] > ollama_phi4['efficiency'] else "OLLAMA"
    print(f"   🏃 Efficiency: {efficiency_winner} wins ({phi4_plus_stats['efficiency']:.2f} vs {ollama_phi4['efficiency']:.2f})")
    
    # Size advantage
    print(f"   💾 Memory: PLUS wins (~8GB vs 11GB)")
    
    # Overall verdict
    wins = {'PLUS': 0, 'OLLAMA': 0}
    if accuracy_winner == 'PLUS': wins['PLUS'] += 1
    elif accuracy_winner == 'OLLAMA': wins['OLLAMA'] += 1
    
    if speed_winner == 'PLUS': wins['PLUS'] += 1
    else: wins['OLLAMA'] += 1
    
    if efficiency_winner == 'PLUS': wins['PLUS'] += 1
    else: wins['OLLAMA'] += 1
    
    wins['PLUS'] += 1  # Memory advantage
    
    print(f"\n🏆 **CHAMPIONSHIP VERDICT:**")
    if wins['PLUS'] > wins['OLLAMA']:
        print("   🔥 NEW REASONING CHAMPION: microsoft/phi-4-reasoning-plus!")
        print("   🎊 The 'Plus' version dethrones the Ollama champion!")
        recommendation = "phi-4-reasoning-plus"
    elif wins['PLUS'] == wins['OLLAMA']:
        print("   ⚖️  It's a TIE! Both are excellent reasoning models")
        print("   💡 Choose based on platform preference")
        recommendation = "either_model"
    else:
        print("   👑 Ollama champion retains the reasoning crown")
        print("   💪 phi4-reasoning:latest remains the best reasoning model")
        recommendation = "phi4-reasoning-ollama"
    
    # Updated Slitheryn recommendation
    print(f"\n🎯 **UPDATED SLITHERYN ACCURACY STACK:**")
    if recommendation == "phi-4-reasoning-plus":
        print("   1. SmartLLM-OG:latest (Ollama, 16GB) - PRIMARY")
        print("   2. microsoft/phi-4-reasoning-plus (LM Studio, ~8GB) - REASONING")
        print("   3. qwen3:30b-a3b (Ollama, 18GB) - COMPREHENSIVE")
        print(f"   💾 Total: ~42GB (3GB savings!)")
    else:
        print("   1. SmartLLM-OG:latest (Ollama, 16GB) - PRIMARY")
        print("   2. phi4-reasoning:latest (Ollama, 11GB) - REASONING")
        print("   3. qwen3:30b-a3b (Ollama, 18GB) - COMPREHENSIVE")
        print(f"   💾 Total: 45GB")
    
    return recommendation

def main():
    print("🧠 PHI-4 REASONING PLUS CHAMPIONSHIP TEST")
    print("="*60)
    print("Testing: microsoft/phi-4-reasoning-plus (LM Studio)")
    print("Versus: phi4-reasoning:latest (Ollama) - Current Champion")
    print("Stakes: Reasoning model crown for Slitheryn")
    print("-"*60)
    
    results = test_phi4_plus()
    
    # Save results
    with open('.claude/phi4-plus-championship-results.json', 'w') as f:
        json.dump({
            'model_info': {
                'name': 'microsoft/phi-4-reasoning-plus',
                'platform': 'LM Studio',
                'format': 'GGUF',
                'estimated_size': '~8GB'
            },
            'test_results': results,
            'timestamp': time.time()
        }, f, indent=2)
    
    # Championship comparison
    recommendation = championship_comparison(results)
    
    print(f"\n💾 Results saved to .claude/phi4-plus-championship-results.json")
    print(f"\n🎯 **FINAL RECOMMENDATION:** {recommendation}")

if __name__ == "__main__":
    main()