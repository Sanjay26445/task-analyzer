from datetime import date, datetime
from typing import List, Dict, Set

class TaskScorer:
    """
    Core algorithm for calculating task priority scores.
    
    Algorithm Design (4 factors from assignment):
    - Importance: Base score from user rating (0-100 points)
    - Urgency: Time-based scoring for due dates (0-100 points)
    - Effort: Quick win bonus for low-effort tasks (0-40 points)
    - Dependencies: Bonus for blocking tasks (0-50 points)
    """
    
    STRATEGY_WEIGHTS = {
        'smart': {
            'importance': 1.0,
            'urgency': 1.0,
            'effort': 0.6,
            'dependencies': 0.8
        },
        'fastest': {
            'importance': 0.2,
            'urgency': 0.3,
            'effort': 2.5,
            'dependencies': 0.1
        },
        'impact': {
            'importance': 2.5,
            'urgency': 0.3,
            'effort': 0.1,
            'dependencies': 0.5
        },
        'deadline': {
            'importance': 0.3,
            'urgency': 2.5,
            'effort': 0.1,
            'dependencies': 0.3
        }
    }
    
    def __init__(self, strategy='smart'):
        self.strategy = strategy
        self.weights = self.STRATEGY_WEIGHTS.get(strategy, self.STRATEGY_WEIGHTS['smart'])
    
    def calculate_score(self, task: Dict, all_tasks: List[Dict]) -> tuple:
        score_breakdown = {}
        
        # 1. IMPORTANCE
        importance_score = task.get('importance', 5) * 10
        score_breakdown['importance'] = importance_score * self.weights['importance']
        
        # 2. URGENCY
        urgency_score, urgency_reason = self._calculate_urgency(task)
        score_breakdown['urgency'] = urgency_score * self.weights['urgency']
        score_breakdown['urgency_reason'] = urgency_reason
        
        # 3. EFFORT (Quick Wins)
        effort_score, effort_reason = self._calculate_effort_bonus(task)
        score_breakdown['effort'] = effort_score * self.weights['effort']
        score_breakdown['effort_reason'] = effort_reason
        
        # 4. DEPENDENCIES
        dependency_score, dep_reason = self._calculate_dependency_bonus(task, all_tasks)
        score_breakdown['dependencies'] = dependency_score * self.weights['dependencies']
        score_breakdown['dependency_reason'] = dep_reason
        
        total_score = sum([
            score_breakdown['importance'],
            score_breakdown['urgency'],
            score_breakdown['effort'],
            score_breakdown['dependencies']
        ])
        
        return round(total_score, 2), score_breakdown
    
    def _calculate_urgency(self, task: Dict) -> tuple:
        if not task.get('due_date'):
            return 0, "No deadline set"
        
        try:
            if isinstance(task['due_date'], str):
                due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
            else:
                due_date = task['due_date']
            
            today = date.today()
            days_until_due = (due_date - today).days
            
            if days_until_due < 0:
                return 100, f"Overdue by {abs(days_until_due)} days!"
            elif days_until_due == 0:
                return 90, "Due today!"
            elif days_until_due == 1:
                return 80, "Due tomorrow"
            elif days_until_due <= 3:
                return 60, f"Due in {days_until_due} days"
            elif days_until_due <= 7:
                return 40, f"Due in {days_until_due} days"
            elif days_until_due <= 14:
                return 20, f"Due in {days_until_due} days"
            else:
                return 10, f"Due in {days_until_due} days"
        except (ValueError, TypeError):
            return 0, "Invalid date format"
    
    def _calculate_effort_bonus(self, task: Dict) -> tuple:
        hours = task.get('estimated_hours', 0)
        
        if hours == 0:
            return 0, "No time estimate"
        elif hours <= 1:
            return 40, "Quick win (≤1hr)"
        elif hours <= 2:
            return 30, "Short task (≤2hrs)"
        elif hours <= 4:
            return 20, "Medium task (≤4hrs)"
        elif hours <= 8:
            return 10, "Standard task (≤8hrs)"
        else:
            return 5, f"Large task ({hours}hrs)"
    
    def _calculate_dependency_bonus(self, task: Dict, all_tasks: List[Dict]) -> tuple:
        task_id = task.get('id')
        if not task_id:
            return 0, "No ID to check dependencies"
        
        blocked_count = 0
        for other_task in all_tasks:
            if task_id in other_task.get('dependencies', []):
                blocked_count += 1
        
        if blocked_count == 0:
            return 0, "No tasks blocked"
        elif blocked_count == 1:
            return 25, "Blocks 1 task"
        elif blocked_count == 2:
            return 35, "Blocks 2 tasks"
        else:
            score = min(50, 25 + (blocked_count * 10))
            return score, f"Blocks {blocked_count} tasks"
    
    def detect_circular_dependencies(self, tasks: List[Dict]) -> List[str]:
        warnings = []
        task_map = {task['id']: task for task in tasks if 'id' in task}
        
        def has_cycle(task_id: int, visited: Set[int], path: Set[int]) -> bool:
            if task_id in path:
                return True
            if task_id in visited:
                return False
            
            visited.add(task_id)
            path.add(task_id)
            
            task = task_map.get(task_id)
            if task:
                for dep_id in task.get('dependencies', []):
                    if has_cycle(dep_id, visited, path):
                        return True
            
            path.remove(task_id)
            return False
        
        visited = set()
        for task_id in task_map.keys():
            if task_id not in visited:
                if has_cycle(task_id, visited, set()):
                    task_title = task_map[task_id]['title']
                    warnings.append(f"Circular dependency detected involving task: {task_title}")
        
        return warnings


def generate_explanation(task: Dict, score_breakdown: Dict, strategy: str) -> str:
    explanations = []
    
    importance = task.get('importance', 5)
    explanations.append(f"Importance: {importance}/10")
    
    if 'urgency_reason' in score_breakdown:
        explanations.append(score_breakdown['urgency_reason'])
    
    if 'effort_reason' in score_breakdown:
        explanations.append(score_breakdown['effort_reason'])
    
    if 'dependency_reason' in score_breakdown and score_breakdown.get('dependencies', 0) > 0:
        explanations.append(score_breakdown['dependency_reason'])
    
    return " • ".join(explanations)