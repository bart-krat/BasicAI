"""
SPICE Framework Prompt Templates

SPICE: Sections, Prompt Variables, Instructions, Context, Examples
Used for: Prompt engineering, structured prompt design, template creation
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class SPICETemplate:
    """SPICE framework for prompt engineering"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for SPICE framework"""
        return """You are an expert prompt engineer using the SPICE framework. Your role is to create well-structured, effective prompts by organizing:

1. SECTIONS: Clear organizational structure and flow
2. PROMPT VARIABLES: Placeholders for dynamic content
3. INSTRUCTIONS: Clear, actionable guidance
4. CONTEXT: Relevant background information
5. EXAMPLES: Concrete demonstrations of expected output

Create prompts that are clear, structured, and easy to follow."""

    @staticmethod
    def create_prompt_template(
        task_description: str,
        sections: List[str],
        variables: List[str],
        instructions: str,
        context: str,
        examples: List[Dict[str, str]]
    ) -> str:
        """Create a SPICE-structured prompt template"""
        
        # Build sections
        sections_text = "\n".join([f"## {section}" for section in sections])
        
        # Build variables
        variables_text = "\n".join([f"- {var}" for var in variables])
        
        # Build examples
        examples_text = ""
        for i, example in enumerate(examples, 1):
            examples_text += f"\n**Example {i}:**\n"
            examples_text += f"Input: {example.get('input', 'N/A')}\n"
            examples_text += f"Output: {example.get('output', 'N/A')}\n"
        
        prompt = f"""# {task_description}

## SECTIONS
{sections_text}

## PROMPT VARIABLES
{variables_text}

## INSTRUCTIONS
{instructions}

## CONTEXT
{context}

## EXAMPLES
{examples_text}

Please follow this structure when responding to similar tasks."""

        return prompt

    @staticmethod
    def get_analysis_prompt(analysis_task: str, variables: Optional[List[str]] = None) -> str:
        """Generate a SPICE analysis prompt"""
        default_variables = ["data", "criteria", "timeframe", "stakeholders"]
        variables = variables or default_variables
        
        variables_text = "\n".join([f"- {var}" for var in variables])
        
        return f"""# Analysis Task: {analysis_task}

## SECTIONS
## Data Overview
## Analysis Framework
## Key Findings
## Recommendations
## Next Steps

## PROMPT VARIABLES
{variables_text}

## INSTRUCTIONS
1. Review the provided data thoroughly
2. Apply the specified analysis framework
3. Identify key patterns and insights
4. Provide actionable recommendations
5. Suggest concrete next steps

## CONTEXT
You are conducting a professional analysis that will inform decision-making. Ensure your analysis is:
- Evidence-based and objective
- Clear and well-structured
- Actionable and specific
- Appropriate for the target audience

## EXAMPLES

**Example 1:**
Input: Sales data showing 15% decline over 3 months
Output: 
- Data Overview: Sales declined from $100K to $85K over Q2
- Analysis Framework: Trend analysis, market comparison
- Key Findings: Decline correlates with competitor price cuts
- Recommendations: Implement competitive pricing strategy
- Next Steps: Conduct pricing analysis by next Friday

**Example 2:**
Input: Customer feedback with mixed satisfaction scores
Output:
- Data Overview: 60% positive, 30% neutral, 10% negative feedback
- Analysis Framework: Sentiment analysis, theme identification
- Key Findings: Support response time is main concern
- Recommendations: Implement faster support ticket system
- Next Steps: Present findings to support team by month-end

Please analyze the provided information following this structure."""

    @staticmethod
    def get_creative_prompt(creative_task: str, style: str = "professional") -> str:
        """Generate a SPICE creative prompt"""
        return f"""# Creative Task: {creative_task}

## SECTIONS
## Brief Overview
## Creative Direction
## Key Elements
## Tone and Style
## Deliverables

## PROMPT VARIABLES
- target_audience
- brand_guidelines
- project_timeline
- budget_constraints
- success_metrics

## INSTRUCTIONS
1. Understand the creative brief and requirements
2. Develop a clear creative direction
3. Identify key visual and content elements
4. Ensure consistency with brand guidelines
5. Create compelling, engaging content

## CONTEXT
You are a creative professional working on a {style} project. The output should be:
- Original and innovative
- Aligned with brand identity
- Engaging for the target audience
- Feasible within given constraints
- Measurable against success criteria

## EXAMPLES

**Example 1:**
Input: Social media campaign for eco-friendly product launch
Output:
- Brief Overview: Launch campaign for new sustainable product line
- Creative Direction: Earthy tones, natural imagery, sustainability focus
- Key Elements: Product shots, environmental benefits, call-to-action
- Tone and Style: Inspiring, educational, action-oriented
- Deliverables: 5 social posts, 1 video, 1 infographic

**Example 2:**
Input: Website redesign for tech startup
Output:
- Brief Overview: Modern, clean website for B2B SaaS platform
- Creative Direction: Minimalist design, tech-forward aesthetic
- Key Elements: Hero section, feature highlights, testimonials
- Tone and Style: Professional, innovative, trustworthy
- Deliverables: Homepage design, 3 key pages, mobile responsive

Please create content following this structured approach."""

    @staticmethod
    def get_technical_prompt(technical_task: str, complexity: str = "intermediate") -> str:
        """Generate a SPICE technical prompt"""
        return f"""# Technical Task: {technical_task}

## SECTIONS
## Problem Statement
## Technical Approach
## Implementation Details
## Testing Strategy
## Documentation

## PROMPT VARIABLES
- requirements
- constraints
- technology_stack
- performance_requirements
- security_considerations

## INSTRUCTIONS
1. Analyze the technical requirements thoroughly
2. Propose a clear technical approach
3. Provide detailed implementation guidance
4. Include comprehensive testing strategy
5. Ensure proper documentation

## CONTEXT
You are a {complexity}-level technical expert. The solution should be:
- Technically sound and scalable
- Well-documented and maintainable
- Secure and performant
- Following best practices
- Ready for production deployment

## EXAMPLES

**Example 1:**
Input: Build REST API for user management
Output:
- Problem Statement: Need secure API for user CRUD operations
- Technical Approach: Node.js with Express, JWT authentication
- Implementation Details: 5 endpoints, middleware, validation
- Testing Strategy: Unit tests, integration tests, load testing
- Documentation: API docs, setup guide, deployment instructions

**Example 2:**
Input: Optimize database query performance
Output:
- Problem Statement: Slow query affecting user experience
- Technical Approach: Index optimization, query rewriting
- Implementation Details: Specific index recommendations
- Testing Strategy: Performance benchmarks, monitoring
- Documentation: Performance report, optimization guide

Please provide technical solutions following this structured approach."""

    @staticmethod
    def get_conversation_prompt(conversation_type: str, tone: str = "professional") -> str:
        """Generate a SPICE conversation prompt"""
        return f"""# Conversation Task: {conversation_type}

## SECTIONS
## Opening
## Main Discussion
## Key Points
## Closing
## Follow-up

## PROMPT VARIABLES
- participant_names
- meeting_objective
- time_allocation
- decision_points
- action_items

## INSTRUCTIONS
1. Set clear expectations and agenda
2. Facilitate productive discussion
3. Ensure all key points are covered
4. Summarize decisions and next steps
5. Plan appropriate follow-up

## CONTEXT
You are facilitating a {tone} conversation. The interaction should be:
- Well-structured and focused
- Inclusive and engaging
- Productive and outcome-oriented
- Professional and respectful
- Clear and actionable

## EXAMPLES

**Example 1:**
Input: Team meeting to discuss project delays
Output:
- Opening: Welcome, agenda review, ground rules
- Main Discussion: Root cause analysis, impact assessment
- Key Points: Resource constraints, timeline adjustments
- Closing: Decisions made, responsibilities assigned
- Follow-up: Weekly check-ins, progress reports

**Example 2:**
Input: Client presentation for new proposal
Output:
- Opening: Introduction, presentation overview
- Main Discussion: Proposal details, benefits, pricing
- Key Points: Unique value proposition, implementation plan
- Closing: Q&A, next steps, timeline
- Follow-up: Proposal document, contract discussion

Please facilitate conversations following this structured approach."""

    @staticmethod
    def get_learning_prompt(learning_objective: str, level: str = "beginner") -> str:
        """Generate a SPICE learning prompt"""
        return f"""# Learning Objective: {learning_objective}

## SECTIONS
## Learning Goals
## Prerequisites
## Learning Path
## Practice Exercises
## Assessment

## PROMPT VARIABLES
- current_skill_level
- learning_style
- time_available
- preferred_format
- success_criteria

## INSTRUCTIONS
1. Define clear learning objectives
2. Assess current knowledge and skills
3. Create structured learning path
4. Provide hands-on practice opportunities
5. Include progress assessment methods

## CONTEXT
You are designing a learning experience for a {level}-level learner. The content should be:
- Clear and well-structured
- Appropriate for skill level
- Engaging and interactive
- Practical and applicable
- Measurable and assessable

## EXAMPLES

**Example 1:**
Input: Learn Python programming basics
Output:
- Learning Goals: Variables, functions, control structures
- Prerequisites: Basic computer skills, logical thinking
- Learning Path: Syntax → Variables → Functions → Control Flow
- Practice Exercises: 10 coding challenges, 1 project
- Assessment: Code review, practical project

**Example 2:**
Input: Master data analysis with Excel
Output:
- Learning Goals: Formulas, charts, pivot tables, VBA basics
- Prerequisites: Basic Excel knowledge, data understanding
- Learning Path: Advanced formulas → Charts → Pivot Tables → VBA
- Practice Exercises: 5 datasets, 3 analysis projects
- Assessment: Practical analysis project, certification

Please create learning experiences following this structured approach."""
```

```python:src/prompt_templates/costar.py
"""
COSTAR Framework Prompt Templates

COSTAR: Context, Objective, Strategy, Tactics, Actions, Results
Used for: Strategic planning, project management, goal setting
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class COSTARTemplate:
    """COSTAR framework prompt template"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for COSTAR framework"""
        return """You are a strategic planning expert using the COSTAR framework. Your role is to help develop comprehensive plans by examining:

1. CONTEXT: The environment and circumstances
2. OBJECTIVE: What we want to achieve
3. STRATEGY: High-level approach to achieve the objective
4. TACTICS: Specific methods and techniques
5. ACTIONS: Concrete steps to implement tactics
6. RESULTS: Expected outcomes and success metrics

Provide clear, actionable plans with measurable outcomes."""

    @staticmethod
    def get_planning_prompt(objective: str, context: Optional[str] = None) -> str:
        """Generate a COSTAR planning prompt"""
        base_prompt = f"""Develop a comprehensive plan using the COSTAR framework for the following objective:

OBJECTIVE:
{objective}

Please provide a structured plan covering:

**CONTEXT:**
- Current environment and circumstances
- Key stakeholders and their interests
- Constraints and opportunities
- Market/industry conditions

**OBJECTIVE:**
- Clear, specific, and measurable goal
- Success criteria and key performance indicators
- Timeline and milestones
- Resource requirements

**STRATEGY:**
- High-level approach to achieve the objective
- Core principles and methodologies
- Competitive advantages or unique approaches
- Risk management strategy

**TACTICS:**
- Specific methods and techniques to implement the strategy
- Tools, technologies, and resources needed
- Process improvements or innovations
- Partnership or collaboration approaches

**ACTIONS:**
- Concrete, actionable steps
- Responsibility assignments
- Timeline and dependencies
- Resource allocation

**RESULTS:**
- Expected outcomes and deliverables
- Success metrics and KPIs
- Measurement and monitoring approach
- Contingency plans

Please ensure the plan is realistic, actionable, and measurable."""

        if context:
            base_prompt += f"\n\nCONTEXT INFORMATION:\n{context}"
        
        return base_prompt

    @staticmethod
    def get_project_management_prompt(project_description: str, constraints: Optional[List[str]] = None) -> str:
        """Generate a COSTAR-based project management prompt"""
        constraints_text = ""
        if constraints:
            constraints_text = "\n".join([f"- {constraint}" for constraint in constraints])
            constraints_text = f"\n\nCONSTRAINTS:\n{constraints_text}"
        
        return f"""Create a project management plan using the COSTAR framework:

PROJECT DESCRIPTION:
{project_description}{constraints_text}

**CONTEXT:**
- Project environment and stakeholders
- Organizational context and culture
- External factors and dependencies

**OBJECTIVE:**
- Project goals and deliverables
- Success criteria and acceptance criteria
- Project scope and boundaries

**STRATEGY:**
- Project approach and methodology
- Risk management strategy
- Quality assurance approach
- Communication strategy

**TACTICS:**
- Project management tools and techniques
- Team structure and roles
- Work breakdown structure approach
- Change management approach

**ACTIONS:**
- Detailed project schedule
- Resource allocation and assignments
- Communication plan and meetings
- Quality control and testing procedures

**RESULTS:**
- Deliverables and milestones
- Performance metrics and reporting
- Project closure criteria
- Lessons learned and knowledge transfer

Provide a comprehensive project plan with clear timelines and responsibilities."""

    @staticmethod
    def get_strategic_analysis_prompt(organization: str, challenge: str) -> str:
        """Generate a COSTAR-based strategic analysis prompt"""
        return f"""Conduct a strategic analysis using the COSTAR framework for:

ORGANIZATION: {organization}
CHALLENGE: {challenge}

**CONTEXT:**
- Organizational environment and culture
- Market position and competitive landscape
- External factors and trends
- Internal capabilities and resources

**OBJECTIVE:**
- Strategic goals and vision
- Key performance indicators
- Success metrics and targets
- Timeline for achievement

**STRATEGY:**
- Strategic approach and direction
- Competitive positioning
- Value proposition and differentiation
- Strategic partnerships and alliances

**TACTICS:**
- Implementation approaches
- Key initiatives and programs
- Technology and innovation strategy
- Market penetration strategies

**ACTIONS:**
- Specific implementation steps
- Resource requirements and allocation
- Organizational changes needed
- Communication and change management

**RESULTS:**
- Expected business outcomes
- Financial projections and ROI
- Market share and growth targets
- Long-term sustainability goals

Provide actionable recommendations with clear implementation guidance."""
```

```python:src/prompt_templates/race.py
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

Now let me create a simple usage example:

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
- **Evidence**: Supporting data
