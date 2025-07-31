#!/usr/bin/env python3
"""
WhiteRabbitNeo Model Comparison for Security Analysis
Compares whiterabbitneo:latest (8.1 GB) vs neo:latest (15 GB)
"""

import json
import time
import requests
from typing import Dict, List, Tuple
import statistics

# Advanced security test cases to differentiate model capabilities
SECURITY_TEST_SUITE = [
    {
        "name": "Complex Reentrancy with Multiple Entry Points",
        "code": """
        contract ComplexVault {
            mapping(address => uint256) private balances;
            mapping(address => bool) private locked;
            
            modifier noReentrant() {
                require(!locked[msg.sender]);
                locked[msg.sender] = true;
                _;
                locked[msg.sender] = false;
            }
            
            function deposit() public payable {
                balances[msg.sender] += msg.value;
            }
            
            function withdraw(uint256 amount) public {
                require(balances[msg.sender] >= amount);
                (bool success,) = msg.sender.call{value: amount}("");
                require(success);
                balances[msg.sender] -= amount;
            }
            
            function transfer(address to, uint256 amount) public noReentrant {
                require(balances[msg.sender] >= amount);
                balances[msg.sender] -= amount;
                balances[to] += amount;
                if (to.code.length > 0) {
                    (bool success,) = to.call{value: amount}("");
                    require(success);
                }
            }
        }
        """,
        "vulnerabilities": ["reentrancy in withdraw", "cross-function reentrancy", "incorrect modifier usage"],
        "complexity": "high"
    },
    {
        "name": "Subtle Access Control Bypass",
        "code": """
        contract AccessControl {
            address public owner;
            mapping(address => bool) public admins;
            uint256 private secret;
            
            constructor() {
                owner = msg.sender;
            }
            
            modifier onlyOwner() {
                require(msg.sender == owner);
                _;
            }
            
            modifier onlyAdmin() {
                require(admins[msg.sender] || msg.sender == owner);
                _;
            }
            
            function setAdmin(address admin, bool status) public {
                require(msg.sender == owner || admins[msg.sender]);
                admins[admin] = status;
            }
            
            function updateSecret(uint256 _secret) public onlyAdmin {
                secret = _secret;
            }
            
            function emergencyWithdraw() public {
                require(tx.origin == owner);
                payable(owner).transfer(address(this).balance);
            }
        }
        """,
        "vulnerabilities": ["tx.origin authentication", "privilege escalation in setAdmin", "missing zero address check"],
        "complexity": "medium"
    },
    {
        "name": "DeFi Protocol Economic Attack Vector",
        "code": """
        contract SimpleDEX {
            uint256 public reserveToken0;
            uint256 public reserveToken1;
            uint256 public totalLiquidity;
            mapping(address => uint256) public liquidity;
            
            function addLiquidity(uint256 amount0, uint256 amount1) public returns (uint256) {
                uint256 liquidityMinted;
                
                if (totalLiquidity == 0) {
                    liquidityMinted = amount0 * amount1;
                } else {
                    liquidityMinted = (amount0 * totalLiquidity) / reserveToken0;
                }
                
                liquidity[msg.sender] += liquidityMinted;
                totalLiquidity += liquidityMinted;
                
                reserveToken0 += amount0;
                reserveToken1 += amount1;
                
                return liquidityMinted;
            }
            
            function swap(uint256 amountIn, bool zeroForOne) public returns (uint256) {
                uint256 amountOut;
                
                if (zeroForOne) {
                    amountOut = (amountIn * reserveToken1) / (reserveToken0 + amountIn);
                    reserveToken0 += amountIn;
                    reserveToken1 -= amountOut;
                } else {
                    amountOut = (amountIn * reserveToken0) / (reserveToken1 + amountIn);
                    reserveToken1 += amountIn;
                    reserveToken0 -= amountOut;
                }
                
                return amountOut;
            }
        }
        """,
        "vulnerabilities": ["integer overflow in liquidity calculation", "price manipulation", "front-running vulnerability", "missing slippage protection"],
        "complexity": "high"
    },
    {
        "name": "Storage Collision and Proxy Pattern Issues",
        "code": """
        contract StorageContract {
            uint256[50] private __gap;
            mapping(bytes32 => uint256) private data;
            
            function setValue(bytes32 key, uint256 value) public {
                data[key] = value;
            }
            
            function getValue(bytes32 key) public view returns (uint256) {
                return data[key];
            }
        }
        
        contract Logic is StorageContract {
            address public implementation;
            address public admin;
            uint256 public version;
            
            function upgrade(address newImplementation) public {
                require(msg.sender == admin);
                implementation = newImplementation;
                version++;
            }
            
            function initialize(address _admin) public {
                admin = _admin;
            }
        }
        """,
        "vulnerabilities": ["storage collision", "unprotected initialize", "missing gap in Logic contract", "delegatecall context issues"],
        "complexity": "high"
    },
    {
        "name": "False Positive Test - Secure Pattern",
        "code": """
        contract SecureVault {
            using SafeMath for uint256;
            
            mapping(address => uint256) private balances;
            mapping(address => uint256) private withdrawalTimestamps;
            uint256 constant WITHDRAWAL_DELAY = 24 hours;
            
            event Withdrawal(address indexed user, uint256 amount);
            
            modifier nonReentrant() {
                uint256 flag;
                assembly { flag := sload(0x1234) }
                require(flag == 0, "Reentrant call");
                assembly { sstore(0x1234, 1) }
                _;
                assembly { sstore(0x1234, 0) }
            }
            
            function requestWithdrawal(uint256 amount) public {
                require(balances[msg.sender] >= amount, "Insufficient balance");
                withdrawalTimestamps[msg.sender] = block.timestamp;
            }
            
            function executeWithdrawal(uint256 amount) public nonReentrant {
                require(balances[msg.sender] >= amount, "Insufficient balance");
                require(block.timestamp >= withdrawalTimestamps[msg.sender].add(WITHDRAWAL_DELAY), "Withdrawal delay not met");
                
                balances[msg.sender] = balances[msg.sender].sub(amount);
                withdrawalTimestamps[msg.sender] = 0;
                
                (bool success,) = msg.sender.call{value: amount}("");
                require(success, "Transfer failed");
                
                emit Withdrawal(msg.sender, amount);
            }
        }
        """,
        "vulnerabilities": [],
        "complexity": "medium",
        "is_secure": True
    }
]

def query_model(model: str, prompt: str, temperature: float = 0.1) -> Tuple[str, float, bool]:
    """Query a specific model and return response with timing"""
    start_time = time.time()
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': temperature,
                    'top_p': 0.95,
                    'num_predict': 2000,  # Allow longer responses for complex analysis
                }
            },
            timeout=120
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            return response.json()['response'], elapsed_time, True
        else:
            return f"Error: {response.status_code}", elapsed_time, False
            
    except Exception as e:
        return f"Error: {str(e)}", time.time() - start_time, False

def analyze_response_quality(response: str, test_case: Dict) -> Dict[str, float]:
    """Analyze the quality and accuracy of model response"""
    response_lower = response.lower()
    
    metrics = {
        'vulnerabilities_found': 0,
        'false_positives': 0,
        'missed_vulnerabilities': 0,
        'explanation_depth': 0,
        'code_understanding': 0,
        'actionable_advice': 0,
        'confidence_calibration': 0
    }
    
    # Check for each expected vulnerability
    if 'vulnerabilities' in test_case:
        for vuln in test_case['vulnerabilities']:
            vuln_keywords = vuln.lower().split()
            if any(keyword in response_lower for keyword in vuln_keywords):
                metrics['vulnerabilities_found'] += 1
            else:
                metrics['missed_vulnerabilities'] += 1
    
    # Check for false positives in secure code
    if test_case.get('is_secure', False):
        vuln_indicators = ['vulnerability', 'vulnerable', 'exploit', 'attack', 'unsafe']
        false_positive_count = sum(1 for indicator in vuln_indicators if indicator in response_lower)
        metrics['false_positives'] = false_positive_count
    
    # Evaluate explanation depth
    explanation_indicators = [
        'because', 'since', 'due to', 'this means', 'specifically',
        'line', 'function', 'contract', 'impact', 'severity'
    ]
    metrics['explanation_depth'] = sum(1 for indicator in explanation_indicators if indicator in response_lower) / len(explanation_indicators)
    
    # Code understanding - check if specific functions/variables are mentioned
    code_elements = ['withdraw', 'balance', 'transfer', 'owner', 'admin', 'liquidity', 'swap']
    mentioned_elements = sum(1 for element in code_elements if element in response_lower)
    metrics['code_understanding'] = min(mentioned_elements / 3, 1.0)  # Normalize
    
    # Actionable advice
    action_indicators = ['should', 'recommend', 'fix', 'change', 'update', 'use', 'implement']
    metrics['actionable_advice'] = sum(1 for indicator in action_indicators if indicator in response_lower) / len(action_indicators)
    
    # Confidence calibration (does the model express uncertainty when appropriate?)
    uncertainty_indicators = ['might', 'could', 'possibly', 'potentially', 'may']
    if test_case.get('complexity') == 'high':
        metrics['confidence_calibration'] = 1.0 if any(indicator in response_lower for indicator in uncertainty_indicators) else 0.5
    else:
        metrics['confidence_calibration'] = 0.8
    
    return metrics

def comprehensive_comparison():
    """Run comprehensive comparison between WhiteRabbitNeo models"""
    
    models = {
        'whiterabbitneo:latest': {'size': '8.1 GB', 'type': 'compact'},
        'neo:latest': {'size': '15 GB', 'type': 'full'}
    }
    
    results = {model: {'scores': [], 'times': [], 'errors': 0} for model in models}
    
    print("WhiteRabbitNeo Model Comparison for Security Analysis")
    print("=" * 60)
    
    for test_case in SECURITY_TEST_SUITE:
        print(f"\nTest Case: {test_case['name']}")
        print(f"Complexity: {test_case['complexity']}")
        
        prompt = f"""You are an expert smart contract security auditor. Analyze the following Solidity code for security vulnerabilities.

Code:
{test_case['code']}

Provide a detailed security analysis including:
1. All vulnerabilities found (with specific line references)
2. Severity assessment for each issue
3. Attack scenarios and potential impact
4. Recommended fixes with code examples
5. Any potential false positives or secure patterns recognized

Be specific and technical in your analysis. Format your response clearly.
"""
        
        for model in models:
            print(f"\n  Testing {model} ({models[model]['size']})...")
            
            # Run multiple times for consistency
            model_scores = []
            model_times = []
            
            for run in range(3):
                response, elapsed_time, success = query_model(model, prompt, temperature=0.1)
                
                if success:
                    metrics = analyze_response_quality(response, test_case)
                    
                    # Calculate overall score
                    if test_case.get('is_secure', False):
                        # For secure code, penalize false positives heavily
                        score = 1.0 - (metrics['false_positives'] * 0.2)
                    else:
                        # For vulnerable code, weight finding vulnerabilities highly
                        total_vulns = len(test_case.get('vulnerabilities', []))
                        if total_vulns > 0:
                            vuln_score = metrics['vulnerabilities_found'] / total_vulns
                        else:
                            vuln_score = 0
                        
                        score = (
                            vuln_score * 0.4 +
                            metrics['explanation_depth'] * 0.2 +
                            metrics['code_understanding'] * 0.15 +
                            metrics['actionable_advice'] * 0.15 +
                            metrics['confidence_calibration'] * 0.1
                        )
                    
                    model_scores.append(score)
                    model_times.append(elapsed_time)
                    
                    if run == 0:  # Print first response summary
                        print(f"    Found {metrics['vulnerabilities_found']} vulnerabilities")
                        print(f"    Response time: {elapsed_time:.2f}s")
                        print(f"    Score: {score:.3f}")
                else:
                    results[model]['errors'] += 1
                    print(f"    Error in run {run + 1}")
            
            if model_scores:
                results[model]['scores'].append(statistics.mean(model_scores))
                results[model]['times'].append(statistics.mean(model_times))
    
    # Final analysis
    print("\n" + "=" * 60)
    print("FINAL COMPARISON RESULTS")
    print("=" * 60)
    
    for model in models:
        if results[model]['scores']:
            avg_score = statistics.mean(results[model]['scores'])
            avg_time = statistics.mean(results[model]['times'])
            
            print(f"\n{model} ({models[model]['size']})")
            print(f"  Average Score: {avg_score:.3f}")
            print(f"  Average Response Time: {avg_time:.2f}s")
            print(f"  Errors: {results[model]['errors']}")
            print(f"  Score/Time Ratio: {avg_score/avg_time:.3f}")
            print(f"  Memory Efficiency: {avg_score / float(models[model]['size'].split()[0]):.3f} score/GB")
    
    # Recommendation
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    
    # Calculate best model
    best_model = None
    best_score = 0
    
    for model in models:
        if results[model]['scores']:
            avg_score = statistics.mean(results[model]['scores'])
            if avg_score > best_score:
                best_score = avg_score
                best_model = model
    
    if best_model:
        print(f"\nBest Model for Security Analysis: {best_model}")
        
        # Additional insights
        small_score = statistics.mean(results['whiterabbitneo:latest']['scores']) if results['whiterabbitneo:latest']['scores'] else 0
        large_score = statistics.mean(results['neo:latest']['scores']) if results['neo:latest']['scores'] else 0
        
        if abs(small_score - large_score) < 0.05:  # Within 5% performance
            print("\nBoth models perform similarly!")
            print("Recommendation: Use whiterabbitneo:latest (8.1 GB) for:")
            print("  - Faster response times")
            print("  - Lower memory usage")
            print("  - Similar accuracy to the larger model")
        else:
            print(f"\nThe larger neo:latest model shows {((large_score/small_score - 1) * 100):.1f}% better accuracy")
            print("Consider using it for:")
            print("  - Critical security audits")
            print("  - Complex vulnerability analysis")
            print("  - When accuracy is more important than speed")
    
    # Save detailed results
    with open('.claude/whiterabbitneo-comparison-results.json', 'w') as f:
        json.dump({
            'models': models,
            'results': results,
            'recommendation': best_model,
            'test_cases': len(SECURITY_TEST_SUITE)
        }, f, indent=2)
    
    print("\nDetailed results saved to .claude/whiterabbitneo-comparison-results.json")

if __name__ == "__main__":
    comprehensive_comparison()