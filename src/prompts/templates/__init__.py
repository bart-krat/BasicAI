"""
Prompt Templates for BasicAI Agent Framework

This module contains industry-standard prompt templates for various frameworks:
- SPICE: Situation, Problem, Implication, Consequence, Evidence
- COSTAR: Context, Objective, Strategy, Tactics, Actions, Results
- RACE: Research, Analysis, Conclusion, Evaluation
"""

from .spice import SPICETemplate
from .costar import COSTARTemplate
from .race import RACETemplate

__all__ = ['SPICETemplate', 'COSTARTemplate', 'RACETemplate']
