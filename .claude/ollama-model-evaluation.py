#!/usr/bin/env python3
"""
Ollama Model Evaluation for Slitheryn Security Analysis
Tests different models for their effectiveness in smart contract vulnerability detection
"""

import json
import time
import requests
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ModelEvaluation:
    model_name: str
    accuracy_score: float
    response_time: float
    security_knowledge: float
    code_understanding: float
    false_positive_detection: float
    
# Test cases for evaluating models
SECURITY_TEST_CASES = [
    {
        "name": "Reentrancy Detection",
        "code": """
        contract Vulnerable {
            mapping(address => uint) balances;
            
            function withdraw() public {
                uint amount = balances[msg.sender];
                (bool success,) = msg.sender.call{value: amount}("");
                require(success);
                balances[msg.sender] = 0;
            }
        }
        """,
        "expected_vulnerability": "reentrancy",
        "prompt": "Analyze this Solidity code for security vulnerabilities. Focus on reentrancy attacks."
    },
    {
        "name": "Integer Overflow",
        "code": """
        contract Token {
            mapping(address => uint256) balances;
            
            function transfer(address to, uint256 amount) public {
                balances[msg.sender] -= amount;
                balances[to] += amount;
            }
        }
        """,
        "expected_vulnerability": "integer_underflow",
        "prompt": "Check this code for arithmetic vulnerabilities in Solidity 0.7.6"
    },
    {
        "name": "Access Control",
        "code": """
        contract Admin {
            address owner;
            
            function setOwner(address newOwner) public {
                owner = newOwner;
            }
        }
        """,
        "expected_vulnerability": "missing_access_control",
        "prompt": "Identify access control issues in this contract"
    },
    {
        "name": "False Positive Test - Safe Code",
        "code": """
        contract Safe {
            address owner;
            modifier onlyOwner() {
                require(msg.sender == owner, "Not owner");
                _;
            }
            
            function withdraw() public onlyOwner {
                payable(owner).transfer(address(this).balance);
            }
        }
        """,
        "expected_vulnerability": "none",
        "prompt": "Analyze this code for vulnerabilities. Note any false positives."
    }
]

def query_ollama(model: str, prompt: str) -> Tuple[str, float]:
    """Query Ollama model and return response with timing"""
    start_time = time.time()
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,  # Low temperature for consistent analysis
                    'top_p': 0.9,
                }
            },
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            return response.json()['response'], elapsed_time
        else:
            return f"Error: {response.status_code}", elapsed_time
            
    except Exception as e:
        return f"Error: {str(e)}", time.time() - start_time

def evaluate_response(response: str, expected_vuln: str) -> Dict[str, float]:
    """Evaluate model response for accuracy"""
    response_lower = response.lower()
    
    scores = {
        'found_vulnerability': 0.0,
        'correct_identification': 0.0,
        'explanation_quality': 0.0,
        'false_positive_handling': 0.0
    }
    
    # Check if vulnerability was found
    vulnerability_keywords = {
        'reentrancy': ['reentrancy', 're-entrancy', 'recursive call', 'state change after call'],
        'integer_underflow': ['underflow', 'overflow', 'arithmetic', 'safeMath'],
        'missing_access_control': ['access control', 'unauthorized', 'permission', 'modifier missing'],
        'none': ['safe', 'no vulnerabilities', 'secure', 'no issues']
    }
    
    if expected_vuln in vulnerability_keywords:
        for keyword in vulnerability_keywords[expected_vuln]:
            if keyword in response_lower:
                scores['found_vulnerability'] = 1.0
                scores['correct_identification'] = 1.0
                break
    
    # Check explanation quality (basic heuristic)
    if len(response) > 100 and any(word in response_lower for word in ['because', 'since', 'due to', 'this means']):
        scores['explanation_quality'] = 0.8
    
    # Check false positive handling
    if expected_vuln == 'none' and 'no vulnerabilities' in response_lower:
        scores['false_positive_handling'] = 1.0
    elif expected_vuln != 'none' and 'false positive' not in response_lower:
        scores['false_positive_handling'] = 0.8
    
    return scores

def evaluate_model(model_name: str) -> ModelEvaluation:
    """Evaluate a single model across all test cases"""
    print(f"\nEvaluating model: {model_name}")
    
    total_scores = {
        'accuracy': 0.0,
        'response_time': 0.0,
        'security_knowledge': 0.0,
        'code_understanding': 0.0,
        'false_positive_detection': 0.0
    }
    
    for test_case in SECURITY_TEST_CASES:
        print(f"  Testing: {test_case['name']}")
        
        # Build comprehensive prompt
        full_prompt = f"""{test_case['prompt']}

Code:
{test_case['code']}

Provide a security analysis focusing on:
1. Specific vulnerabilities found
2. Severity assessment
3. Whether this might be a false positive
4. Recommended fixes
"""
        
        response, elapsed_time = query_ollama(model_name, full_prompt)
        
        if not response.startswith("Error"):
            scores = evaluate_response(response, test_case['expected_vulnerability'])
            
            total_scores['accuracy'] += scores['correct_identification']
            total_scores['response_time'] += elapsed_time
            total_scores['security_knowledge'] += scores['found_vulnerability']
            total_scores['code_understanding'] += scores['explanation_quality']
            total_scores['false_positive_detection'] += scores['false_positive_handling']
            
            print(f"    Response time: {elapsed_time:.2f}s")
            print(f"    Accuracy: {scores['correct_identification']}")
        else:
            print(f"    Error: {response}")
    
    # Calculate averages
    num_tests = len(SECURITY_TEST_CASES)
    return ModelEvaluation(
        model_name=model_name,
        accuracy_score=total_scores['accuracy'] / num_tests,
        response_time=total_scores['response_time'] / num_tests,
        security_knowledge=total_scores['security_knowledge'] / num_tests,
        code_understanding=total_scores['code_understanding'] / num_tests,
        false_positive_detection=total_scores['false_positive_detection'] / num_tests
    )

def rank_models(evaluations: List[ModelEvaluation]) -> List[Tuple[str, float]]:
    """Rank models based on weighted criteria"""
    rankings = []
    
    # Weights for different criteria (optimized for security analysis)
    weights = {
        'accuracy': 0.35,
        'security_knowledge': 0.25,
        'false_positive_detection': 0.20,
        'code_understanding': 0.15,
        'response_time': 0.05  # Lower weight, but still important
    }
    
    for eval in evaluations:
        # Normalize response time (lower is better)
        time_score = 1.0 - min(eval.response_time / 30.0, 1.0)  # 30s as max reasonable time
        
        total_score = (
            weights['accuracy'] * eval.accuracy_score +
            weights['security_knowledge'] * eval.security_knowledge +
            weights['false_positive_detection'] * eval.false_positive_detection +
            weights['code_understanding'] * eval.code_understanding +
            weights['response_time'] * time_score
        )
        
        rankings.append((eval.model_name, total_score, eval))
    
    return sorted(rankings, key=lambda x: x[1], reverse=True)

def main():
    """Run evaluation on all available models"""
    
    # Models to evaluate (from your list)
    models = [
        "deepseek-coder:33b-instruct",  # Specialized for code
        "devstral:latest",              # Code-focused model
        "SmartLLM-OG:latest",           # Your custom models
        "smartllm:latest",
        "neo:latest",
        "whiterabbitneo:latest",
        "deepseek-r1:7b-qwen-distill-q8_0",
        "magistral:latest",
        "qwen3:30b-a3b",
        "phi4-reasoning:latest"
    ]
    
    print("Slitheryn Ollama Model Evaluation")
    print("=" * 50)
    
    evaluations = []
    
    for model in models:
        try:
            eval_result = evaluate_model(model)
            evaluations.append(eval_result)
        except Exception as e:
            print(f"Failed to evaluate {model}: {str(e)}")
    
    # Rank and display results
    print("\n\nFinal Rankings for Slitheryn Security Analysis:")
    print("=" * 50)
    
    rankings = rank_models(evaluations)
    
    for i, (model, score, eval) in enumerate(rankings, 1):
        print(f"\n{i}. {model} (Score: {score:.3f})")
        print(f"   - Accuracy: {eval.accuracy_score:.2f}")
        print(f"   - Security Knowledge: {eval.security_knowledge:.2f}")
        print(f"   - False Positive Detection: {eval.false_positive_detection:.2f}")
        print(f"   - Code Understanding: {eval.code_understanding:.2f}")
        print(f"   - Avg Response Time: {eval.response_time:.2f}s")
    
    # Save results
    with open('.claude/ollama-evaluation-results.json', 'w') as f:
        results = {
            'rankings': [(m, s) for m, s, _ in rankings],
            'detailed_evaluations': [
                {
                    'model': e.model_name,
                    'scores': {
                        'accuracy': e.accuracy_score,
                        'security_knowledge': e.security_knowledge,
                        'false_positive_detection': e.false_positive_detection,
                        'code_understanding': e.code_understanding,
                        'response_time': e.response_time
                    }
                } for e in evaluations
            ],
            'recommendation': rankings[0][0] if rankings else "No models evaluated"
        }
        json.dump(results, f, indent=2)
    
    print(f"\n\nRecommendation: Use '{rankings[0][0]}' for Slitheryn AI integration")
    print("Results saved to .claude/ollama-evaluation-results.json")

if __name__ == "__main__":
    main()