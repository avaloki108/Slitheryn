#!/usr/bin/env python3
"""
SmartLLM Championship: Determine the absolute best SmartLLM model
Head-to-head comparison with comprehensive Web3 security tests
"""

import json
import time
import requests

def comprehensive_smartllm_test():
    """Test both SmartLLM models with advanced Web3 scenarios"""
    
    # Advanced Web3 security test cases
    test_cases = [
        {
            "name": "Classic Reentrancy",
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
            "difficulty": "basic",
            "expected_findings": ["reentrancy"],
            "max_score": 100
        },
        {
            "name": "DeFi Flash Loan Attack Vector",
            "code": """
            pragma solidity ^0.8.0;
            
            interface IERC20 {
                function transfer(address to, uint256 amount) external returns (bool);
                function balanceOf(address account) external view returns (uint256);
            }
            
            contract DeFiProtocol {
                mapping(address => uint256) public userBalances;
                IERC20 public token;
                uint256 public exchangeRate = 100; // 1 ETH = 100 tokens
                
                constructor(address _token) {
                    token = _token;
                }
                
                function deposit() external payable {
                    userBalances[msg.sender] += msg.value;
                }
                
                function flashLoan(uint256 amount) external {
                    uint256 balanceBefore = address(this).balance;
                    require(balanceBefore >= amount, "Insufficient liquidity");
                    
                    // Send flash loan
                    (bool success,) = msg.sender.call{value: amount}("");
                    require(success, "Flash loan transfer failed");
                    
                    // Check repayment
                    require(address(this).balance >= balanceBefore, "Flash loan not repaid");
                }
                
                function swapETHForTokens() external payable {
                    uint256 tokensToMint = msg.value * exchangeRate;
                    token.transfer(msg.sender, tokensToMint);
                }
                
                function updateExchangeRate(uint256 newRate) external {
                    exchangeRate = newRate;
                }
            }
            """,
            "difficulty": "advanced",
            "expected_findings": ["flash_loan_manipulation", "price_oracle_manipulation", "access_control"],
            "max_score": 100
        },
        {
            "name": "Governance Attack Scenario",
            "code": """
            pragma solidity ^0.8.0;
            
            contract DAOGovernance {
                mapping(address => uint256) public votingPower;
                mapping(uint256 => Proposal) public proposals;
                uint256 public proposalCount;
                uint256 public constant VOTING_PERIOD = 3 days;
                
                struct Proposal {
                    string description;
                    uint256 votesFor;
                    uint256 votesAgainst;
                    uint256 endTime;
                    bool executed;
                    address proposer;
                }
                
                function createProposal(string memory description) external {
                    require(votingPower[msg.sender] >= 1000, "Insufficient voting power");
                    
                    proposals[proposalCount] = Proposal({
                        description: description,
                        votesFor: 0,
                        votesAgainst: 0,
                        endTime: block.timestamp + VOTING_PERIOD,
                        executed: false,
                        proposer: msg.sender
                    });
                    
                    proposalCount++;
                }
                
                function vote(uint256 proposalId, bool support) external {
                    Proposal storage proposal = proposals[proposalId];
                    require(block.timestamp < proposal.endTime, "Voting ended");
                    
                    uint256 power = votingPower[msg.sender];
                    
                    if (support) {
                        proposal.votesFor += power;
                    } else {
                        proposal.votesAgainst += power;
                    }
                }
                
                function executeProposal(uint256 proposalId) external {
                    Proposal storage proposal = proposals[proposalId];
                    require(block.timestamp >= proposal.endTime, "Voting still active");
                    require(!proposal.executed, "Already executed");
                    require(proposal.votesFor > proposal.votesAgainst, "Proposal failed");
                    
                    proposal.executed = true;
                    
                    // Execute proposal logic here
                    (bool success,) = address(this).call(abi.encodeWithSignature("emergencyDrain()"));
                }
                
                function delegateVotingPower(address to, uint256 amount) external {
                    require(votingPower[msg.sender] >= amount, "Insufficient power");
                    votingPower[msg.sender] -= amount;
                    votingPower[to] += amount;
                }
                
                function emergencyDrain() external {
                    payable(msg.sender).transfer(address(this).balance);
                }
            }
            """,
            "difficulty": "expert",
            "expected_findings": ["governance_attack", "double_voting", "delegation_manipulation", "emergency_function_exposure"],
            "max_score": 100
        }
    ]
    
    # Test both SmartLLM models
    models_to_test = [
        {
            "name": "smartllm:latest",
            "platform": "Ollama",
            "size": "8.5GB",
            "api_url": "http://localhost:11434/api/generate"
        },
        {
            "name": "SmartLLM-OG:latest", 
            "platform": "Ollama",
            "size": "16GB",
            "api_url": "http://localhost:11434/api/generate"
        }
    ]
    
    all_results = {}
    
    for model in models_to_test:
        print(f"\n{'='*60}")
        print(f"🤖 TESTING: {model['name']} ({model['size']})")
        print(f"{'='*60}")
        
        model_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}/{len(test_cases)}: {test_case['name']}")
            print(f"🎯 Difficulty: {test_case['difficulty']}")
            print(f"🔍 Expected findings: {', '.join(test_case['expected_findings'])}")
            
            prompt = f"""You are an expert Web3 security auditor specializing in smart contract vulnerabilities, DeFi exploits, and governance attacks.

Analyze this Solidity smart contract for security vulnerabilities:

{test_case['code']}

Focus on:
1. Smart contract vulnerabilities (reentrancy, access control, etc.)
2. DeFi-specific attack vectors (flash loans, price manipulation, MEV)
3. Governance vulnerabilities (voting manipulation, proposal attacks)
4. Economic exploits and tokenomics issues
5. Specific attack scenarios with step-by-step exploitation

Provide:
- Detailed vulnerability analysis
- Severity assessment (Critical/High/Medium/Low)
- Attack scenarios with exploitation steps
- Economic impact assessment
- Specific fix recommendations with code

Be thorough and Web3-focused in your analysis."""

            start_time = time.time()
            
            try:
                response = requests.post(
                    model['api_url'],
                    json={
                        'model': model['name'],
                        'prompt': prompt,
                        'stream': False,
                        'options': {
                            'temperature': 0.1,
                            'num_predict': 2000
                        }
                    },
                    timeout=120
                )
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    content = response.json()['response']
                    content_lower = content.lower()
                    
                    print(f"⏱️  Response time: {elapsed:.2f}s")
                    print(f"📝 Response length: {len(content)} chars")
                    
                    # Advanced Web3-focused scoring
                    score = 0
                    findings = []
                    
                    # Core vulnerability detection (40 points)
                    if 'reentrancy' in content_lower:
                        score += 20
                        findings.append('reentrancy')
                    
                    if any(term in content_lower for term in ['flash loan', 'flashloan']):
                        score += 10
                        findings.append('flash_loan_understanding')
                    
                    if any(term in content_lower for term in ['governance', 'voting', 'proposal']):
                        score += 10
                        findings.append('governance_analysis')
                    
                    # Web3-specific knowledge (30 points)
                    if any(term in content_lower for term in ['mev', 'front-run', 'sandwich']):
                        score += 10
                        findings.append('mev_awareness')
                    
                    if any(term in content_lower for term in ['oracle', 'price manipulation', 'exchange rate']):
                        score += 10
                        findings.append('price_manipulation')
                    
                    if any(term in content_lower for term in ['defi', 'liquidity', 'slippage']):
                        score += 10
                        findings.append('defi_expertise')
                    
                    # Attack scenario quality (20 points)
                    if 'attack' in content_lower and 'step' in content_lower:
                        score += 10
                        findings.append('attack_scenarios')
                    
                    if any(term in content_lower for term in ['economic', 'profit', 'drain']):
                        score += 10
                        findings.append('economic_impact')
                    
                    # Fix quality (10 points)
                    if any(fix in content_lower for fix in ['nonreentrant', 'timelock', 'multisig', 'access control']):
                        score += 10
                        findings.append('quality_fixes')
                    
                    test_result = {
                        'test_name': test_case['name'],
                        'difficulty': test_case['difficulty'],
                        'score': score,
                        'max_score': test_case['max_score'],
                        'time': elapsed,
                        'findings': findings,
                        'efficiency': score / elapsed if elapsed > 0 else 0,
                        'web3_expertise': len([f for f in findings if f in ['mev_awareness', 'price_manipulation', 'defi_expertise', 'governance_analysis']]),
                        'response_preview': content[:400] + '...' if len(content) > 400 else content
                    }
                    
                    model_results.append(test_result)
                    
                    print(f"🎯 Score: {score}/100")
                    print(f"⚡ Efficiency: {score/elapsed:.2f} points/second")
                    print(f"🌐 Web3 expertise score: {test_result['web3_expertise']}/4")
                    print(f"🔍 Findings: {', '.join(findings)}")
                    
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    model_results.append({
                        'test_name': test_case['name'],
                        'error': f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
                model_results.append({
                    'test_name': test_case['name'],
                    'error': str(e)
                })
        
        all_results[model['name']] = {
            'model_info': model,
            'test_results': model_results
        }
    
    return all_results

def determine_smartllm_champion(results):
    """Analyze results and declare the SmartLLM champion"""
    
    print(f"\n{'='*70}")
    print("🏆 SMARTLLM CHAMPIONSHIP RESULTS")
    print(f"{'='*70}")
    
    model_summaries = {}
    
    for model_name, model_data in results.items():
        valid_results = [r for r in model_data['test_results'] if 'error' not in r]
        
        if valid_results:
            summary = {
                'model_info': model_data['model_info'],
                'avg_score': sum(r['score'] for r in valid_results) / len(valid_results),
                'avg_time': sum(r['time'] for r in valid_results) / len(valid_results),
                'avg_efficiency': sum(r['efficiency'] for r in valid_results) / len(valid_results),
                'avg_web3_expertise': sum(r['web3_expertise'] for r in valid_results) / len(valid_results),
                'total_tests': len(valid_results),
                'best_score': max(r['score'] for r in valid_results),
                'consistency': min(r['score'] for r in valid_results) / max(r['score'] for r in valid_results) if max(r['score'] for r in valid_results) > 0 else 0
            }
            model_summaries[model_name] = summary
    
    # Display results
    for model_name, summary in model_summaries.items():
        print(f"\n🤖 **{model_name}** ({summary['model_info']['size']})")
        print(f"   📊 Average Score: {summary['avg_score']:.1f}/100")
        print(f"   ⏱️  Average Time: {summary['avg_time']:.2f}s")
        print(f"   ⚡ Efficiency: {summary['avg_efficiency']:.2f} points/second")
        print(f"   🌐 Web3 Expertise: {summary['avg_web3_expertise']:.1f}/4")
        print(f"   🎯 Best Score: {summary['best_score']}/100")
        print(f"   📈 Consistency: {summary['consistency']:.2f}")
    
    # Determine champion
    print(f"\n🥊 **HEAD-TO-HEAD COMPARISON:**")
    
    models = list(model_summaries.keys())
    if len(models) == 2:
        model1, model2 = models
        summary1, summary2 = model_summaries[model1], model_summaries[model2]
        
        categories = [
            ('Accuracy', 'avg_score', 'higher'),
            ('Speed', 'avg_time', 'lower'),
            ('Efficiency', 'avg_efficiency', 'higher'),
            ('Web3 Expertise', 'avg_web3_expertise', 'higher'),
            ('Consistency', 'consistency', 'higher')
        ]
        
        wins = {model1: 0, model2: 0}
        
        for category, metric, direction in categories:
            val1, val2 = summary1[metric], summary2[metric]
            
            if direction == 'higher':
                winner = model1 if val1 > val2 else model2 if val2 > val1 else 'tie'
            else:
                winner = model1 if val1 < val2 else model2 if val2 < val1 else 'tie'
            
            if winner != 'tie':
                wins[winner] += 1
                
            print(f"   {category}: {winner.upper() if winner != 'tie' else 'TIE'} wins")
    
    # Declare champion
    print(f"\n🏆 **SMARTLLM CHAMPION:**")
    
    if wins[model1] > wins[model2]:
        champion = model1
        runner_up = model2
    elif wins[model2] > wins[model1]:
        champion = model2
        runner_up = model1
    else:
        # Tie-breaker: Web3 expertise + efficiency
        champion = model1 if (summary1['avg_web3_expertise'] + summary1['avg_efficiency']) > (summary2['avg_web3_expertise'] + summary2['avg_efficiency']) else model2
        runner_up = model2 if champion == model1 else model1
    
    champ_summary = model_summaries[champion]
    
    print(f"   🔥 **{champion}** ({champ_summary['model_info']['size']})")
    print(f"   🎊 NEW SLITHERYN PRIMARY MODEL RECOMMENDATION!")
    
    print(f"\n💡 **WHY {champion.upper()} WINS:**")
    strengths = []
    if champ_summary['avg_score'] >= 85:
        strengths.append("🎯 Excellent accuracy")
    if champ_summary['avg_efficiency'] >= 3:
        strengths.append("⚡ Good efficiency")
    if champ_summary['avg_web3_expertise'] >= 2:
        strengths.append("🌐 Strong Web3 knowledge")
    if champ_summary['consistency'] >= 0.8:
        strengths.append("📈 Consistent performance")
    
    for strength in strengths:
        print(f"   {strength}")
    
    return champion, model_summaries

def main():
    print("🧠 SMARTLLM CHAMPIONSHIP: Finding the Ultimate Web3 Security Model")
    print("="*75)
    print("Goal: Determine which SmartLLM is best for Slitheryn")
    print("Tests: Advanced Web3 security scenarios")
    print("Stakes: Primary model recommendation for Web3 security analysis")
    print("-"*75)
    
    # Run comprehensive tests
    results = comprehensive_smartllm_test()
    
    # Determine champion
    champion, summaries = determine_smartllm_champion(results)
    
    # Save results
    with open('.claude/smartllm-championship-results.json', 'w') as f:
        json.dump({
            'championship_results': results,
            'model_summaries': summaries,
            'champion': champion,
            'timestamp': time.time(),
            'recommendation': f"{champion} is the recommended primary model for Slitheryn Web3 security analysis"
        }, f, indent=2)
    
    print(f"\n💾 Championship results saved to .claude/smartllm-championship-results.json")
    print(f"\n🎯 **FINAL SLITHERYN RECOMMENDATION: {champion}**")

if __name__ == "__main__":
    main()