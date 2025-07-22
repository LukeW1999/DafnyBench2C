"""
Heuristic-based validator implementation
"""

import re
from typing import Dict, Any, Optional
from src.interfaces import IValidator, ValidationResult
from src.config import TestConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)

class HeuristicValidator(IValidator):
    """Heuristic-based validator for Dafny to C conversion"""
    
    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or TestConfig()
        logger.info("Initialized HeuristicValidator")
    
    def validate_conversion(self, dafny_code: str, c_code: str, **kwargs) -> ValidationResult:
        """Validate Dafny to C conversion using heuristics"""
        logger.info("Starting heuristic validation")
        
        score = 0.0
        details = []
        issues = []
        validation_reasons = {}  # 存储每个评分项的具体依据
        
        # 1. Check function signatures (25%) - 可判断：方法名是否保留
        sig_score, sig_reasons = self._check_function_signatures_detailed(dafny_code, c_code)
        score += sig_score * self.config.validation_rules["function_signatures"]
        validation_reasons['function_signatures'] = sig_reasons
        if sig_score > 0.8:
            details.append("✅ Function signatures preserved")
        elif sig_score > 0.5:
            details.append("⚠️ Function signatures partially preserved")
        else:
            issues.append("❌ Function signatures not preserved")
        
        # 2. Check ACSL annotations (35%) - 可判断：Dafny契约到ACSL的转换
        acsl_score, acsl_reasons = self._check_acsl_annotations_detailed(dafny_code, c_code)
        score += acsl_score * self.config.validation_rules["acsl_annotations"]
        validation_reasons['acsl_annotations'] = acsl_reasons
        if acsl_score > 0.8:
            details.append("✅ ACSL annotations well preserved")
        elif acsl_score > 0.5:
            details.append("⚠️ ACSL annotations partially preserved")
        else:
            issues.append("❌ ACSL annotations missing or poor")
        
        # 3. Check tests passed (40%) - 可判断：测试是否通过
        test_score = kwargs.get('test_score', 0.0)
        score += test_score * self.config.validation_rules["tests_passed"]
        validation_reasons['tests_passed'] = {
            'score': test_score,
            'reasons': ['Tests passed successfully' if test_score == 1.0 else 'Tests failed or partially passed']
        }
        if test_score > 0.8:
            details.append("✅ Tests passed")
        elif test_score > 0.5:
            details.append("⚠️ Some tests passed")
        else:
            issues.append("❌ Tests failed")
        
        # 创建验证结果
        validation_result = ValidationResult(
            score=score,
            is_valid=score > 0.5,  # 简单的有效性判断
            details=[f"Total score: {score:.3f}"],
            issues=[] if score > 0.5 else ["Validation score too low"],
            metadata={
                'detailed_scores': {
                    'function_signatures': sig_score,
                    'acsl_annotations': acsl_score,
                    'tests_passed': test_score
                },
                'validation_reasons': validation_reasons
            }
        )
        
        logger.info(f"Validation completed. Score: {score:.2f}, Valid: {validation_result.is_valid}")
        
        return validation_result
    
    def validate_syntax(self, c_code: str, **kwargs) -> ValidationResult:
        """Validate C code syntax (basic checks)"""
        logger.info("Starting syntax validation")
        
        issues = []
        details = []
        
        # Check for basic C syntax patterns
        if not re.search(r'#include\s+<[^>]+>', c_code):
            issues.append("Missing include statements")
        else:
            details.append("Include statements present")
        
        if not re.search(r'/\*@.*?\*/', c_code, re.DOTALL):
            issues.append("Missing ACSL annotations")
        else:
            details.append("ACSL annotations present")
        
        if not re.search(r'\w+\s+\w+\s*\([^)]*\)\s*{', c_code):
            issues.append("No function definitions found")
        else:
            details.append("Function definitions present")
        
        is_valid = len(issues) == 0
        score = 1.0 if is_valid else 0.0
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            details=details,
            issues=issues,
            metadata={'validation_type': 'syntax'}
        )
    
    def validate_semantics(self, dafny_code: str, c_code: str, **kwargs) -> ValidationResult:
        """Validate semantic equivalence (basic checks)"""
        logger.info("Starting semantic validation")
        
        # This is a simplified semantic validation
        # In a real implementation, this would be more sophisticated
        
        details = []
        issues = []
        
        # Check if both codes have similar structure
        dafny_functions = re.findall(r'method\s+(\w+)', dafny_code)
        c_functions = re.findall(r'\w+\s+(\w+)\s*\([^)]*\)\s*{', c_code)
        
        if dafny_functions and c_functions:
            details.append("Function structure preserved")
        else:
            issues.append("Function structure mismatch")
        
        # Check for similar variable names
        dafny_vars = re.findall(r'var\s+(\w+)', dafny_code)
        c_vars = re.findall(r'int\s+(\w+)', c_code)
        
        if dafny_vars and c_vars:
            details.append("Variable declarations present")
        else:
            issues.append("Variable declarations missing")
        
        is_valid = len(issues) == 0
        score = 1.0 if is_valid else 0.0
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            details=details,
            issues=issues,
            metadata={'validation_type': 'semantic'}
        )
    
    def get_validation_rules(self) -> Dict[str, float]:
        """Get validation rules and their weights"""
        return self.config.validation_rules.copy()
    
    def _has_function_signatures(self, dafny_code: str, c_code: str) -> bool:
        """Check if function signatures are preserved"""
        dafny_methods = re.findall(r'method\s+(\w+)\s*\([^)]*\)', dafny_code)
        c_functions = re.findall(r'\w+\s+(\w+)\s*\([^)]*\)\s*{', c_code)
        
        # Check if at least one method was converted
        return len(dafny_methods) > 0 and len(c_functions) > 0
    
    def _has_acsl_annotations(self, c_code: str) -> bool:
        """Check if ACSL annotations are present"""
        return bool(re.search(r'/\*@.*?\*/', c_code, re.DOTALL))
    
    def _has_array_length_params(self, dafny_code: str, c_code: str) -> bool:
        """Check if array length parameters were added"""
        # Look for array parameters in Dafny
        dafny_arrays = re.findall(r'array<[^>]+>', dafny_code)
        
        if not dafny_arrays:
            return True  # No arrays to check
        
        # Look for length parameters in C
        c_length_params = re.findall(r'\w+_length', c_code)
        
        return len(c_length_params) > 0
    
    def _has_loop_invariants(self, dafny_code: str, c_code: str) -> bool:
        """Check if loop invariants were converted"""
        dafny_invariants = re.findall(r'invariant\s+[^;]+;', dafny_code)
        
        if not dafny_invariants:
            return True  # No invariants to check
        
        # Look for loop invariants in C ACSL
        c_invariants = re.findall(r'loop\s+invariant', c_code)
        
        return len(c_invariants) > 0 
    
    def _check_acsl_annotations(self, dafny_code: str, c_code: str) -> float:
        """Check ACSL annotations quality (0.0-1.0)"""
        # Count ACSL annotations in C code
        c_acsl_count = len(re.findall(r'/\*@.*?\*/', c_code, re.DOTALL))
        
        # Count Dafny contracts
        dafny_contracts = len(re.findall(r'requires|ensures|invariant', dafny_code))
        
        if dafny_contracts == 0:
            return 1.0 if c_acsl_count == 0 else 0.5  # No contracts to convert
        
        # Calculate conversion ratio
        conversion_ratio = min(c_acsl_count / dafny_contracts, 1.0)
        
        # Bonus for having ACSL annotations
        if c_acsl_count > 0:
            conversion_ratio = min(conversion_ratio + 0.2, 1.0)
        
        return conversion_ratio
    
    def _check_type_conversion(self, dafny_code: str, c_code: str) -> float:
        """Check type conversion correctness (0.0-1.0)"""
        score = 0.0
        
        # Check for basic type mappings
        type_mappings = {
            'int': 'int',
            'bool': 'int',  # bool -> int in C
            'real': 'double',
            'char': 'char'
        }
        
        for dafny_type, c_type in type_mappings.items():
            if re.search(rf'\b{dafny_type}\b', dafny_code) and re.search(rf'\b{c_type}\b', c_code):
                score += 0.25
        
        # Check for array type conversions
        if re.search(r'array<[^>]+>', dafny_code) and re.search(r'\w+\s*\*', c_code):
            score += 0.25
        
        return min(score, 1.0)
    
    def _check_logic_structure(self, dafny_code: str, c_code: str) -> float:
        """Check logic structure preservation (0.0-1.0)"""
        score = 0.0
        
        # Check for control structures
        structures = ['if', 'while', 'for']
        for struct in structures:
            dafny_count = len(re.findall(rf'\b{struct}\b', dafny_code))
            c_count = len(re.findall(rf'\b{struct}\b', c_code))
            
            if dafny_count > 0 and c_count > 0:
                score += 0.3
            elif dafny_count == 0 and c_count == 0:
                score += 0.1  # No control structures to convert
        
        # Check for return statements
        dafny_returns = len(re.findall(r'\breturn\b', dafny_code))
        c_returns = len(re.findall(r'\breturn\b', c_code))
        
        if dafny_returns > 0 and c_returns > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_array_handling(self, dafny_code: str, c_code: str) -> float:
        """Check array handling (0.0-1.0)"""
        score = 0.0
        
        # Check if arrays exist in Dafny
        dafny_arrays = re.findall(r'array<[^>]+>', dafny_code)
        
        if not dafny_arrays:
            return 1.0  # No arrays to handle
        
        # Check for array parameters in C
        c_array_params = re.findall(r'\w+\s*\*', c_code)
        if c_array_params:
            score += 0.5
        
        # Check for length parameters
        c_length_params = re.findall(r'\w+_length', c_code)
        if c_length_params:
            score += 0.5
        
        return score
    
    def _check_loop_conversion(self, dafny_code: str, c_code: str) -> float:
        """Check loop conversion (0.0-1.0)"""
        score = 0.0
        
        # Count loops in both codes
        dafny_loops = len(re.findall(r'\bwhile\b|\bfor\b', dafny_code))
        c_loops = len(re.findall(r'\bwhile\b|\bfor\b', c_code))
        
        if dafny_loops == 0:
            return 1.0  # No loops to convert
        
        # Check loop count preservation
        if c_loops > 0:
            score += 0.5
        
        # Check for loop invariants
        dafny_invariants = len(re.findall(r'invariant\s+[^;]+;', dafny_code))
        c_invariants = len(re.findall(r'loop\s+invariant', c_code))
        
        if dafny_invariants > 0 and c_invariants > 0:
            score += 0.5
        elif dafny_invariants == 0:
            score += 0.5  # No invariants to convert
        
        return score 
    
    def _check_function_signatures_detailed(self, dafny_code: str, c_code: str) -> tuple[float, dict]:
        """Check function signatures with detailed reasons"""
        dafny_methods = re.findall(r'method\s+(\w+)\s*\([^)]*\)', dafny_code)
        c_functions = re.findall(r'\w+\s+(\w+)\s*\([^)]*\)\s*{', c_code)
        
        reasons = {
            'score': 0.0,
            'reasons': [],
            'dafny_methods': dafny_methods,
            'c_functions': c_functions
        }
        
        if not dafny_methods:
            reasons['reasons'].append("No Dafny methods found")
            return 0.0, reasons
        
        if not c_functions:
            reasons['reasons'].append("No C functions found")
            return 0.0, reasons
        
        # Check if method names are preserved
        preserved_count = 0
        for dafny_method in dafny_methods:
            if dafny_method in c_functions:
                preserved_count += 1
                reasons['reasons'].append(f"Method '{dafny_method}' preserved")
            else:
                reasons['reasons'].append(f"Method '{dafny_method}' not found in C code")
        
        score = preserved_count / len(dafny_methods)
        reasons['score'] = score
        
        if score == 1.0:
            reasons['reasons'].append("All function signatures perfectly preserved")
        elif score > 0.5:
            reasons['reasons'].append(f"Partially preserved: {preserved_count}/{len(dafny_methods)} methods")
        else:
            reasons['reasons'].append(f"Poor preservation: {preserved_count}/{len(dafny_methods)} methods")
        
        return score, reasons
    
    def _check_acsl_annotations_detailed(self, dafny_code: str, c_code: str) -> tuple[float, dict]:
        """Check ACSL annotations with detailed reasons - 只检查可比较的契约转换"""
        # Count ACSL annotations in C code
        c_acsl_blocks = re.findall(r'/\*@.*?\*/', c_code, re.DOTALL)
        c_acsl_count = len(c_acsl_blocks)
        
        # Count Dafny contracts (只检查基本的requires/ensures)
        dafny_requires = len(re.findall(r'requires\s+[^;]+;', dafny_code))
        dafny_ensures = len(re.findall(r'ensures\s+[^;]+;', dafny_code))
        dafny_contracts = dafny_requires + dafny_ensures
        
        reasons = {
            'score': 0.0,
            'reasons': [],
            'dafny_contracts': dafny_contracts,
            'c_acsl_blocks': c_acsl_count,
            'dafny_requires': dafny_requires,
            'dafny_ensures': dafny_ensures
        }
        
        if dafny_contracts == 0:
            if c_acsl_count == 0:
                reasons['reasons'].append("No contracts in Dafny, no ACSL needed")
                return 1.0, reasons
            else:
                reasons['reasons'].append("No contracts in Dafny but ACSL found (bonus)")
                return 0.8, reasons
        
        # 检查requires和ensures的转换
        c_requires = len(re.findall(r'requires\s+[^;]+;', c_code))
        c_ensures = len(re.findall(r'ensures\s+[^;]+;', c_code))
        
        # 计算转换比例
        requires_ratio = c_requires / dafny_requires if dafny_requires > 0 else 1.0
        ensures_ratio = c_ensures / dafny_ensures if dafny_ensures > 0 else 1.0
        
        # 平均转换比例
        if dafny_requires > 0 and dafny_ensures > 0:
            conversion_ratio = (requires_ratio + ensures_ratio) / 2
        elif dafny_requires > 0:
            conversion_ratio = requires_ratio
        elif dafny_ensures > 0:
            conversion_ratio = ensures_ratio
        else:
            conversion_ratio = 1.0
        
        reasons['score'] = conversion_ratio
        
        # 详细说明
        if dafny_requires > 0:
            if c_requires > 0:
                reasons['reasons'].append(f"Requires: {c_requires}/{dafny_requires} converted")
            else:
                reasons['reasons'].append(f"Requires: 0/{dafny_requires} converted")
        
        if dafny_ensures > 0:
            if c_ensures > 0:
                reasons['reasons'].append(f"Ensures: {c_ensures}/{dafny_ensures} converted")
            else:
                reasons['reasons'].append(f"Ensures: 0/{dafny_ensures} converted")
        
        # 奖励有ACSL注释
        if c_acsl_count > 0:
            conversion_ratio = min(conversion_ratio + 0.1, 1.0)
            reasons['reasons'].append("Bonus: ACSL annotations present")
        
        reasons['score'] = conversion_ratio
        return conversion_ratio, reasons
    
    def _check_type_conversion_detailed(self, dafny_code: str, c_code: str) -> tuple[float, dict]:
        """Check type conversion with detailed reasons"""
        score = 0.0
        reasons = {
            'score': 0.0,
            'reasons': [],
            'type_mappings': {}
        }
        
        # Check for basic type mappings
        type_mappings = {
            'int': 'int',
            'bool': 'int',  # bool -> int in C
            'real': 'double',
            'char': 'char'
        }
        
        for dafny_type, c_type in type_mappings.items():
            dafny_count = len(re.findall(rf'\b{dafny_type}\b', dafny_code))
            c_count = len(re.findall(rf'\b{c_type}\b', c_code))
            
            if dafny_count > 0:
                if c_count > 0:
                    score += 0.25
                    reasons['reasons'].append(f"Type '{dafny_type}' correctly mapped to '{c_type}'")
                    reasons['type_mappings'][dafny_type] = {'found': True, 'count': c_count}
                else:
                    reasons['reasons'].append(f"Type '{dafny_type}' not found in C code")
                    reasons['type_mappings'][dafny_type] = {'found': False, 'count': 0}
        
        # Check for array type conversions
        dafny_arrays = re.findall(r'array<[^>]+>', dafny_code)
        c_pointers = re.findall(r'\w+\s*\*', c_code)
        
        if dafny_arrays:
            if c_pointers:
                score += 0.25
                reasons['reasons'].append(f"Array types converted to pointers: {len(c_pointers)} found")
                reasons['type_mappings']['array'] = {'found': True, 'count': len(c_pointers)}
            else:
                reasons['reasons'].append("Array types not converted to pointers")
                reasons['type_mappings']['array'] = {'found': False, 'count': 0}
        else:
            reasons['reasons'].append("No arrays to convert")
        
        reasons['score'] = min(score, 1.0)
        return min(score, 1.0), reasons
    
    def _check_logic_structure_detailed(self, dafny_code: str, c_code: str) -> tuple[float, dict]:
        """Check logic structure preservation with detailed reasons"""
        score = 0.0
        reasons = {
            'score': 0.0,
            'reasons': [],
            'structures': {}
        }
        
        # Check for control structures
        structures = ['if', 'while', 'for']
        for struct in structures:
            dafny_count = len(re.findall(rf'\b{struct}\b', dafny_code))
            c_count = len(re.findall(rf'\b{struct}\b', c_code))
            
            reasons['structures'][struct] = {'dafny': dafny_count, 'c': c_count}
            
            if dafny_count > 0 and c_count > 0:
                score += 0.3
                reasons['reasons'].append(f"'{struct}' statements preserved: {c_count} in C")
            elif dafny_count == 0 and c_count == 0:
                score += 0.1  # No control structures to convert
                reasons['reasons'].append(f"No '{struct}' statements to convert")
            else:
                reasons['reasons'].append(f"'{struct}' statements mismatch: {dafny_count} in Dafny, {c_count} in C")
        
        # Check for return statements
        dafny_returns = len(re.findall(r'\breturn\b', dafny_code))
        c_returns = len(re.findall(r'\breturn\b', c_code))
        
        reasons['structures']['return'] = {'dafny': dafny_returns, 'c': c_returns}
        
        if dafny_returns > 0 and c_returns > 0:
            score += 0.2
            reasons['reasons'].append(f"Return statements preserved: {c_returns} in C")
        elif dafny_returns == 0 and c_returns == 0:
            reasons['reasons'].append("No return statements to convert")
        else:
            reasons['reasons'].append(f"Return statements mismatch: {dafny_returns} in Dafny, {c_returns} in C")
        
        reasons['score'] = min(score, 1.0)
        return min(score, 1.0), reasons
    
    def _check_array_handling_detailed(self, dafny_code: str, c_code: str) -> tuple[float, dict]:
        """Check array handling with detailed reasons"""
        score = 0.0
        reasons = {
            'score': 0.0,
            'reasons': [],
            'array_info': {}
        }
        
        # Check if arrays exist in Dafny
        dafny_arrays = re.findall(r'array<[^>]+>', dafny_code)
        
        if not dafny_arrays:
            reasons['reasons'].append("No arrays in Dafny code")
            reasons['array_info'] = {'has_arrays': False}
            return 1.0, reasons
        
        reasons['array_info']['has_arrays'] = True
        reasons['array_info']['dafny_arrays'] = len(dafny_arrays)
        
        # Check for array parameters in C
        c_array_params = re.findall(r'\w+\s*\*', c_code)
        if c_array_params:
            score += 0.5
            reasons['reasons'].append(f"Array parameters found: {len(c_array_params)} pointer parameters")
            reasons['array_info']['c_pointers'] = len(c_array_params)
        else:
            reasons['reasons'].append("No array parameters found in C code")
            reasons['array_info']['c_pointers'] = 0
        
        # Check for length parameters
        c_length_params = re.findall(r'\w+_length', c_code)
        if c_length_params:
            score += 0.5
            reasons['reasons'].append(f"Length parameters found: {len(c_length_params)} length parameters")
            reasons['array_info']['length_params'] = len(c_length_params)
        else:
            reasons['reasons'].append("No length parameters found")
            reasons['array_info']['length_params'] = 0
        
        reasons['score'] = score
        return score, reasons
    
    def _check_loop_conversion_detailed(self, dafny_code: str, c_code: str) -> tuple[float, dict]:
        """Check loop conversion with detailed reasons"""
        score = 0.0
        reasons = {
            'score': 0.0,
            'reasons': [],
            'loop_info': {}
        }
        
        # Count loops in both codes
        dafny_loops = len(re.findall(r'\bwhile\b|\bfor\b', dafny_code))
        c_loops = len(re.findall(r'\bwhile\b|\bfor\b', c_code))
        
        reasons['loop_info']['dafny_loops'] = dafny_loops
        reasons['loop_info']['c_loops'] = c_loops
        
        if dafny_loops == 0:
            reasons['reasons'].append("No loops in Dafny code")
            return 1.0, reasons
        
        # Check loop count preservation
        if c_loops > 0:
            score += 0.5
            reasons['reasons'].append(f"Loops preserved: {c_loops} loops in C code")
        else:
            reasons['reasons'].append("No loops found in C code")
        
        # Check for loop invariants
        dafny_invariants = len(re.findall(r'invariant\s+[^;]+;', dafny_code))
        c_invariants = len(re.findall(r'loop\s+invariant', c_code))
        
        reasons['loop_info']['dafny_invariants'] = dafny_invariants
        reasons['loop_info']['c_invariants'] = c_invariants
        
        if dafny_invariants > 0 and c_invariants > 0:
            score += 0.5
            reasons['reasons'].append(f"Loop invariants converted: {c_invariants}/{dafny_invariants}")
        elif dafny_invariants == 0:
            score += 0.5  # No invariants to convert
            reasons['reasons'].append("No loop invariants to convert")
        else:
            reasons['reasons'].append(f"Loop invariants not converted: {c_invariants}/{dafny_invariants}")
        
        reasons['score'] = score
        return score, reasons 