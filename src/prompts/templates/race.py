"""
RACE Framework Prompt Templates

RACE: Research, Analysis, Conclusion, Evaluation
Used for: Research projects, academic writing, evidence-based decision making
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class RACETemplate:
    """RACE framework prompt template"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for RACE framework"""
        return """You are a research expert using the RACE framework. Your role is to conduct thorough, evidence-based analysis by following:

1. RESEARCH: Gather relevant information and data
2. ANALYSIS: Examine and interpret the information
3. CONCLUSION: Draw evidence-based conclusions
4. EVALUATION: Assess the quality and reliability of findings

Provide rigorous, well-supported analysis with proper citations and evidence."""

    @staticmethod
    def get_research_prompt(research_question: str, scope: Optional[str] = None) -> str:
        """Generate a RACE research prompt"""
        base_prompt = f"""Conduct a comprehensive research analysis using the RACE framework for the following question:

RESEARCH QUESTION:
{research_question}

Please provide a structured analysis covering:

**RESEARCH:**
- Key information sources and data points
- Relevant studies, reports, and literature
- Statistical data and metrics
- Expert opinions and case studies
- Historical context and trends

**ANALYSIS:**
- Critical examination of the information gathered
- Identification of patterns, trends, and relationships
- Comparison of different perspectives and findings
- Identification of gaps or limitations in available data
- Statistical analysis and interpretation

**CONCLUSION:**
- Evidence-based conclusions drawn from the analysis
- Key findings and insights
- Implications of the research findings
- Recommendations based on the evidence
- Confidence level in the conclusions

**EVALUATION:**
- Assessment of source quality and reliability
- Evaluation of methodology and data collection
- Identification of potential biases or limitations
- Strength of evidence supporting conclusions
- Areas requiring further research

Please ensure all claims are supported by evidence and properly evaluated for reliability."""

        if scope:
            base_prompt += f"\n\nRESEARCH SCOPE:\n{scope}"
        
        return base_prompt

    @staticmethod
    def get_literature_review_prompt(topic: str, focus_areas: Optional[List[str]] = None) -> str:
        """Generate a RACE-based literature review prompt"""
        focus_text = ""
        if focus_areas:
            focus_text = "\n".join([f"- {area}" for area in focus_areas])
            focus_text = f"\n\nFOCUS AREAS:\n{focus_text}"
        
        return f"""Conduct a literature review using the RACE framework for the following topic:

TOPIC: {topic}{focus_text}

**RESEARCH:**
- Comprehensive search of relevant literature
- Key studies, papers, and reports identified
- Chronological overview of research development
- Different schools of thought and perspectives
- Methodological approaches used in the field

**ANALYSIS:**
- Critical analysis of key findings and arguments
- Comparison of different research approaches
- Identification of consensus and disagreements
- Analysis of methodological strengths and weaknesses
- Synthesis of findings across studies

**CONCLUSION:**
- Current state of knowledge in the field
- Key insights and patterns across the literature
- Gaps and limitations in existing research
- Emerging trends and future directions
- Practical implications of the research

**EVALUATION:**
- Quality assessment of sources and studies
- Evaluation of research methodologies
- Assessment of bias and limitations
- Strength of evidence for different claims
- Recommendations for future research

Provide a comprehensive, critical analysis of the literature with proper evaluation of source quality."""

    @staticmethod
    def get_evidence_assessment_prompt(claim: str, evidence: List[str]) -> str:
        """Generate a RACE-based evidence assessment prompt"""
        evidence_text = "\n".join([f"- {item}" for item in evidence])
        
        return f"""Assess the evidence for the following claim using the RACE framework:

CLAIM: {claim}

EVIDENCE PROVIDED:
{evidence_text}

**RESEARCH:**
- Additional evidence that should be considered
- Counter-evidence or opposing viewpoints
- Context and background information needed
- Expert opinions and authoritative sources

**ANALYSIS:**
- Critical examination of each piece of evidence
- Assessment of evidence quality and reliability
- Identification of logical connections and gaps
- Analysis of potential biases or limitations
- Statistical or methodological evaluation

**CONCLUSION:**
- Overall assessment of the claim's validity
- Strength of evidence supporting the claim
- Confidence level in the conclusion
- Key factors supporting or undermining the claim
- Qualifications or limitations to the conclusion

**EVALUATION:**
- Quality rating of the evidence provided
- Assessment of source credibility and authority
- Evaluation of methodology and data collection
- Identification of potential biases or conflicts of interest
- Recommendations for strengthening the evidence

Provide a rigorous, objective assessment of the evidence and claim validity."""
```

```python:src/prompt_templates/example_usage.py
"""
Example usage of prompt templates
"""

from .spice import SPICETemplate
from .costar import COSTARTemplate
from .race import RACETemplate

def example_usage():
    """Demonstrate how to use the prompt templates"""
    
    # SPICE Example
    spice = SPICETemplate()
    situation = "Our company's customer satisfaction scores have dropped 15% over the last quarter"
    spice_prompt = spice.get_analysis_prompt(situation)
    print("SPICE Analysis Prompt:")
    print(spice_prompt)
    print("\n" + "="*50 + "\n")
    
    # COSTAR Example
    costar = COSTARTemplate()
    objective = "Increase customer satisfaction scores by 20% within 6 months"
    costar_prompt = costar.get_planning_prompt(objective)
    print("COSTAR Planning Prompt:")
    print(costar_prompt)
    print("\n" + "="*50 + "\n")
    
    # RACE Example
    race = RACETemplate()
    research_question = "What are the most effective strategies for improving customer satisfaction in the software industry?"
    race_prompt = race.get_research_prompt(research_question)
    print("RACE Research Prompt:")
    print(race_prompt)

if __name__ == "__main__":
    example_usage()
```

These templates provide:

## **SPICE Framework**
- **Situation**: Current state and context
- **Problem**: Specific issues identified
- **Implication**: What it means for stakeholders
- **Consequence**: Potential outcomes
- **Evidence**: Supporting data and facts

## **COSTAR Framework**
- **Context**: Environment and circumstances
- **Objective**: Clear goals and success criteria
- **Strategy**: High-level approach
- **Tactics**: Specific methods and techniques
- **Actions**: Concrete implementation steps
- **Results**: Expected outcomes and metrics

## **RACE Framework**
- **Research**: Information gathering and sources
- **Analysis**: Critical examination and interpretation
- **Conclusion**: Evidence-based findings
- **Evaluation**: Quality assessment of evidence

Each template includes multiple specialized prompts for different use cases like project management, strategic planning, literature reviews, and evidence assessment.

