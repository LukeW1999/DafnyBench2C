"""
Configuration models for different components
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class ModelConfig:
    """AI模型配置"""
    name: str
    api_base: str
    api_key: str
    model: str
    timeout: int
    max_tokens: int = 4000
    temperature: float = 0.1

    @classmethod
    def claude_opus(cls, api_key: str) -> 'ModelConfig':
        return cls(
            name="claude-3-opus",
            api_base="https://api.anthropic.com",
            api_key=api_key,
            model="claude-3-opus-20240229",
            timeout=120  # 增加到2分钟
        )

    @classmethod
    def claude_sonnet(cls, api_key: str) -> 'ModelConfig':
        return cls(
            name="claude-3-sonnet",
            api_base="https://api.anthropic.com",
            api_key=api_key,
            model="claude-3-sonnet-20240229",
            timeout=120  # 增加到2分钟
        )

    @classmethod
    def claude_haiku(cls, api_key: str) -> 'ModelConfig':
        return cls(
            name="claude-3-haiku",
            api_base="https://api.anthropic.com",
            api_key=api_key,
            model="claude-3-haiku-20240307",
            timeout=120  # 增加到2分钟
        )

    @classmethod
    def deepseek_chat(cls, api_key: str) -> 'ModelConfig':
        return cls(
            name="deepseek-chat",
            api_base="https://api.deepseek.com",
            api_key=api_key,
            model="deepseek-chat",
            timeout=120  # 增加到2分钟
        )

    @classmethod
    def deepseek_reasoner(cls, api_key: str) -> 'ModelConfig':
        return cls(
            name="deepseek-reasoner",
            api_base="https://api.deepseek.com",
            api_key=api_key,
            model="deepseek-reasoner",
            timeout=180  # 推理模型需要更长时间
        )

@dataclass
class ConverterConfig:
    """Configuration for converter"""
    enable_self_review: bool = True
    enable_validation: bool = True
    enable_test_generation: bool = True
    enable_csv_output: bool = True
    enable_code_cleaning: bool = True
    
    # Prompt templates
    conversion_prompt_template: str = "Convert Dafny to C with ACSL contracts. Return ONLY the C code."
    review_prompt_template: str = "Review Dafny to C conversion. Return ONLY improved C code."
    validation_prompt_template: str = "Validate Dafny to C conversion. Answer only VALID or INVALID."
    test_prompt_template: str = "Generate C test file with main function and 2 test cases."

@dataclass
class TestConfig:
    """测试配置"""
    # 超时设置
    compilation_timeout: int = 60  # 编译超时增加到60秒
    execution_timeout: int = 100   # 执行超时增加到100秒
    
    # 验证规则权重
    validation_rules: Dict[str, float] = None
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = {
                'function_signatures': 0.25,
                'acsl_annotations': 0.35,
                'tests_passed': 0.40
            } 