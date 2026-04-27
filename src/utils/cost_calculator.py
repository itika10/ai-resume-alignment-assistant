"""
Token usage and cost tracking utilities.

Pricing reflects gpt-4.1-mini at the time of writing.
Update the constants below if you change models or OpenAI changes pricing.
"""

from dataclasses import dataclass, field
from typing import Dict


# gpt-4.1-mini pricing (USD per 1M tokens)
MODEL_NAME = "gpt-4.1-mini"
PRICE_INPUT_PER_1M = 0.40
PRICE_OUTPUT_PER_1M = 1.60


def compute_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Compute USD cost for the given token counts using the configured pricing.
    """
    input_cost = (input_tokens / 1_000_000) * PRICE_INPUT_PER_1M
    output_cost = (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_1M
    return input_cost + output_cost


@dataclass
class ChainUsage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost(self) -> float:
        return compute_cost(self.input_tokens, self.output_tokens)


@dataclass
class UsageTracker:
    """
    Accumulates token usage per chain across a single resume generation run.
    """
    breakdown: Dict[str, ChainUsage] = field(default_factory=dict)

    def record(self, chain_name: str, input_tokens: int, output_tokens: int) -> None:
        existing = self.breakdown.get(chain_name, ChainUsage())
        existing.input_tokens += int(input_tokens or 0)
        existing.output_tokens += int(output_tokens or 0)
        self.breakdown[chain_name] = existing

    @property
    def total_input(self) -> int:
        return sum(u.input_tokens for u in self.breakdown.values())

    @property
    def total_output(self) -> int:
        return sum(u.output_tokens for u in self.breakdown.values())

    @property
    def total_tokens(self) -> int:
        return self.total_input + self.total_output

    @property
    def total_cost(self) -> float:
        return compute_cost(self.total_input, self.total_output)
