"""
Planning Examples and Templates

This module contains detailed prompts for task analysis and breakdown into modular steps.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class PlanningExamples:
    """Examples and templates for task planning and breakdown"""
    
    @staticmethod
    def get_task_breakdown_prompt(task_description: str, complexity_level: str = "medium") -> str:
        """Generate a comprehensive task breakdown prompt"""
        return f"""# Task Analysis and Breakdown: {task_description}

## SECTIONS
## Task Overview
## Complexity Assessment
## Sub-task Identification
## Dependencies and Sequencing
## Resource Requirements
## Timeline and Milestones
## Risk Assessment
## Success Criteria

## PROMPT VARIABLES
- task_description: "{task_description}"
- complexity_level: "{complexity_level}"
- available_resources
- timeline_constraints
- team_capabilities
- success_metrics

## INSTRUCTIONS
1. **Analyze the main task** - Break down the high-level objective into its core components
2. **Assess complexity** - Evaluate the difficulty and scope of each component
3. **Identify sub-tasks** - Create specific, actionable sub-tasks that can be completed independently
4. **Map dependencies** - Determine the order and relationships between sub-tasks
5. **Estimate resources** - Identify what resources (time, people, tools) each sub-task needs
6. **Create timeline** - Develop a realistic schedule with milestones
7. **Assess risks** - Identify potential obstacles and mitigation strategies
8. **Define success** - Establish clear criteria for task completion

## CONTEXT
You are a project management expert analyzing a {complexity_level}-complexity task. The breakdown should be:
- **Modular**: Each sub-task should be independently completable
- **Sequential**: Clear order and dependencies between tasks
- **Measurable**: Each sub-task should have clear deliverables
- **Realistic**: Appropriate scope and timeline for available resources
- **Flexible**: Allow for adjustments as the project progresses

## EXAMPLES

**Example 1: Website Redesign Project**
Input: "Redesign our company website to improve user experience and increase conversions"

Output:
- **Task Overview**: Complete website redesign focusing on UX improvements and conversion optimization
- **Complexity Assessment**: High complexity - involves design, development, content, and testing
- **Sub-task Identification**:
  1. User research and persona development
  2. Information architecture planning
  3. Wireframe and prototype creation
  4. Visual design and branding
  5. Frontend development
  6. Backend integration
  7. Content creation and migration
  8. Testing and quality assurance
  9. Launch and deployment
  10. Post-launch monitoring and optimization
- **Dependencies**: Research → Architecture → Wireframes → Design → Development → Content → Testing → Launch
- **Resource Requirements**: UX designer, UI designer, 2 developers, content writer, QA tester
- **Timeline**: 12 weeks with weekly milestones
- **Risk Assessment**: Technical challenges, stakeholder approval delays, content migration issues
- **Success Criteria**: 20% increase in conversion rate, improved user satisfaction scores

**Example 2: Data Analysis Project**
Input: "Analyze customer behavior data to identify opportunities for product improvement"

Output:
- **Task Overview**: Comprehensive analysis of customer behavior data to drive product decisions
- **Complexity Assessment**: Medium complexity - requires data skills, analytical thinking, and business knowledge
- **Sub-task Identification**:
  1. Data collection and validation
  2. Data cleaning and preprocessing
  3. Exploratory data analysis
  4. Statistical analysis and modeling
  5. Visualization and reporting
  6. Insight generation and recommendations
  7. Presentation and stakeholder communication
- **Dependencies**: Collection → Cleaning → EDA → Analysis → Visualization → Insights → Presentation
- **Resource Requirements**: Data analyst, business analyst, visualization tools
- **Timeline**: 6 weeks with bi-weekly checkpoints
- **Risk Assessment**: Data quality issues, incomplete datasets, unclear business requirements
- **Success Criteria**: Actionable insights that lead to measurable product improvements

Please analyze the provided task and break it down into modular, actionable sub-tasks following this structured approach."""

    @staticmethod
    def get_agile_sprint_planning_prompt(epic_description: str, sprint_duration: int = 2) -> str:
        """Generate an Agile sprint planning prompt"""
        return f"""# Agile Sprint Planning: {epic_description}

## SECTIONS
## Epic Overview
## User Story Breakdown
## Story Points Estimation
## Sprint Backlog Creation
## Task Dependencies
## Sprint Goals
## Definition of Done

## PROMPT VARIABLES
- epic_description: "{epic_description}"
- sprint_duration: "{sprint_duration} weeks"
- team_velocity
- available_capacity
- technical_debt
- stakeholder_priorities

## INSTRUCTIONS
1. **Break down the epic** into user stories that deliver value
2. **Estimate story points** using relative sizing (Fibonacci sequence)
3. **Create sprint backlog** based on team capacity and velocity
4. **Identify dependencies** between stories and tasks
5. **Define sprint goals** that align with business objectives
6. **Establish acceptance criteria** for each story
7. **Plan for testing and deployment** within the sprint

## CONTEXT
You are an Agile coach planning a {sprint_duration}-week sprint. The planning should be:
- **User-focused**: Stories should deliver value to end users
- **Sized appropriately**: Stories should be completable within the sprint
- **Well-defined**: Clear acceptance criteria and definition of done
- **Realistic**: Based on team capacity and historical velocity
- **Flexible**: Allow for adjustments during the sprint

## EXAMPLES

**Example 1: E-commerce Checkout Improvement**
Input: "Improve the checkout process to reduce cart abandonment"

Output:
- **Epic Overview**: Enhance checkout flow to increase conversion rates
- **User Story Breakdown**:
  - As a customer, I want to save my payment info for faster checkout
  - As a customer, I want to see progress indicators during checkout
  - As a customer, I want to edit my cart without losing my place
  - As a customer, I want to see shipping costs before entering payment
- **Story Points**: 5, 3, 2, 8 points respectively
- **Sprint Backlog**: Focus on progress indicators and cart editing (5 points total)
- **Dependencies**: Progress indicators can be done independently, cart editing needs backend support
- **Sprint Goals**: Reduce checkout abandonment by 10%
- **Definition of Done**: Code reviewed, tested, deployed, and monitored

Please create a detailed sprint plan following this Agile methodology."""

    @staticmethod
    def get_workflow_optimization_prompt(current_process: str, optimization_goals: List[str]) -> str:
        """Generate a workflow optimization prompt"""
        goals_text = "\n".join([f"- {goal}" for goal in optimization_goals])
        
        return f"""# Workflow Optimization: {current_process}

## SECTIONS
## Current State Analysis
## Bottleneck Identification
## Optimization Opportunities
## Process Redesign
## Implementation Plan
## Success Metrics
## Change Management

## PROMPT VARIABLES
- current_process: "{current_process}"
- optimization_goals: {optimization_goals}
- team_size
- technology_stack
- budget_constraints
- timeline_requirements

## INSTRUCTIONS
1. **Map current process** - Document each step and decision point
2. **Identify bottlenecks** - Find where delays and inefficiencies occur
3. **Analyze optimization opportunities** - Look for automation, parallelization, and elimination
4. **Redesign the process** - Create an improved workflow
5. **Plan implementation** - Break down changes into manageable phases
6. **Define success metrics** - Establish measurable improvements
7. **Address change management** - Plan for team adoption and training

## CONTEXT
You are a process improvement expert optimizing a workflow. The optimization should be:
- **Data-driven**: Based on actual performance metrics
- **Practical**: Implementable with available resources
- **Measurable**: Clear before/after comparisons
- **Sustainable**: Long-term improvements, not quick fixes
- **User-focused**: Improves experience for all stakeholders

## EXAMPLES

**Example 1: Customer Support Ticket Resolution**
Input: "Optimize our customer support ticket resolution process"

Output:
- **Current State Analysis**: 5-step process with average 48-hour resolution time
- **Bottleneck Identification**: Manual triage, limited knowledge base access, escalation delays
- **Optimization Opportunities**:
  - Automated ticket categorization
  - Self-service knowledge base
  - Tiered support structure
  - Real-time collaboration tools
- **Process Redesign**: 3-step process with automated routing and self-service options
- **Implementation Plan**: 4-week phased rollout with training
- **Success Metrics**: 50% reduction in resolution time, 30% increase in first-call resolution
- **Change Management**: Team training, gradual rollout, feedback collection

Please analyze and optimize the provided workflow following this structured approach."""

    @staticmethod
    def get_project_roadmap_prompt(project_vision: str, timeline_months: int = 12) -> str:
        """Generate a project roadmap planning prompt"""
        return f"""# Project Roadmap: {project_vision}

## SECTIONS
## Vision and Objectives
## Key Milestones
## Feature Prioritization
## Resource Allocation
## Risk Mitigation
## Success Metrics
## Communication Plan

## PROMPT VARIABLES
- project_vision: "{project_vision}"
- timeline_months: "{timeline_months} months"
- budget_constraints
- team_capabilities
- market_requirements
- stakeholder_expectations

## INSTRUCTIONS
1. **Define clear vision** - Establish the project's long-term goals and success criteria
2. **Identify key milestones** - Break the timeline into major deliverables
3. **Prioritize features** - Use value vs. effort matrix to prioritize development
4. **Allocate resources** - Assign team members and budget to different phases
5. **Plan risk mitigation** - Identify potential obstacles and contingency plans
6. **Establish metrics** - Define how success will be measured
7. **Create communication plan** - Regular updates and stakeholder engagement

## CONTEXT
You are a project manager creating a {timeline_months}-month roadmap. The roadmap should be:
- **Strategic**: Aligned with business objectives and market needs
- **Realistic**: Based on available resources and capabilities
- **Flexible**: Allow for adjustments based on feedback and changes
- **Measurable**: Clear milestones and success criteria
- **Communicable**: Easy to understand and share with stakeholders

## EXAMPLES

**Example 1: Mobile App Development**
Input: "Develop a mobile app for food delivery with real-time tracking"

Output:
- **Vision**: Become the leading food delivery app in our market with superior user experience
- **Key Milestones**:
  - Month 3: MVP with basic ordering functionality
  - Month 6: Real-time tracking and payment integration
  - Month 9: Advanced features and restaurant partnerships
  - Month 12: Market expansion and optimization
- **Feature Prioritization**: Core ordering → Tracking → Payments → Advanced features
- **Resource Allocation**: 2 mobile developers, 1 backend developer, 1 designer
- **Risk Mitigation**: Technical challenges, market competition, regulatory compliance
- **Success Metrics**: 10K downloads, 4.5+ app store rating, 25% monthly active users
- **Communication Plan**: Weekly team standups, monthly stakeholder reviews

Please create a comprehensive project roadmap following this structured approach."""

    @staticmethod
    def get_task_delegation_prompt(task_description: str, team_members: List[str]) -> str:
        """Generate a task delegation prompt"""
        team_text = "\n".join([f"- {member}" for member in team_members])
        
        return f"""# Task Delegation: {task_description}

## SECTIONS
## Task Analysis
## Team Capability Assessment
## Delegation Strategy
## Responsibility Matrix
## Communication Plan
## Progress Monitoring
## Success Criteria

## PROMPT VARIABLES
- task_description: "{task_description}"
- team_members: {team_members}
- deadline_constraints
- quality_requirements
- budget_limitations
- reporting_frequency

## INSTRUCTIONS
1. **Analyze the task** - Break down into components and identify required skills
2. **Assess team capabilities** - Match team members' skills to task requirements
3. **Create delegation strategy** - Assign tasks based on skills, availability, and development goals
4. **Define responsibilities** - Clear ownership and accountability for each component
5. **Plan communication** - Regular check-ins and progress updates
6. **Establish monitoring** - Track progress and identify issues early
7. **Set success criteria** - Clear deliverables and quality standards

## CONTEXT
You are a team lead delegating a complex task. The delegation should be:
- **Skill-matched**: Assign tasks to people with appropriate capabilities
- **Development-focused**: Provide growth opportunities for team members
- **Clear**: Unambiguous responsibilities and expectations
- **Supportive**: Provide necessary resources and guidance
- **Accountable**: Clear ownership and progress tracking

## EXAMPLES

**Example 1: Website Redesign Project**
Input: "Redesign company website with team of 4 developers"

Output:
- **Task Analysis**: Frontend design, backend integration, content management, testing
- **Team Capability Assessment**: Senior frontend, junior backend, content specialist, QA tester
- **Delegation Strategy**:
  - Senior frontend: Lead design and frontend development
  - Junior backend: API integration and database work
  - Content specialist: Content creation and CMS setup
  - QA tester: Testing strategy and quality assurance
- **Responsibility Matrix**: RACI chart with clear roles and responsibilities
- **Communication Plan**: Daily standups, weekly reviews, milestone checkpoints
- **Progress Monitoring**: Jira tickets, code reviews, demo sessions
- **Success Criteria**: Responsive design, fast loading, accessible, SEO-optimized

Please create a detailed delegation plan following this structured approach."""
