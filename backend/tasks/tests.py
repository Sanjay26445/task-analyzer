from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScorer

class TaskScorerTests(TestCase):
    
    def setUp(self):
        self.scorer = TaskScorer(strategy='smart')
        self.today = date.today()
    
    def test_overdue_task_gets_high_urgency_score(self):
        task = {
            'id': 1,
            'title': 'Overdue task',
            'due_date': (self.today - timedelta(days=5)).isoformat(),
            'estimated_hours': 3,
            'importance': 7,
            'dependencies': []
        }
        
        score, breakdown = self.scorer.calculate_score(task, [task])
        self.assertGreater(breakdown['urgency'], 80)
        self.assertIn('Overdue', breakdown['urgency_reason'])
    
    def test_quick_win_bonus(self):
        task = {
            'id': 2,
            'title': 'Quick task',
            'due_date': None,
            'estimated_hours': 0.5,
            'importance': 5,
            'dependencies': []
        }
        
        score, breakdown = self.scorer.calculate_score(task, [task])
        self.assertGreater(breakdown['effort'], 0)
        self.assertIn('Quick win', breakdown['effort_reason'])
    
    def test_dependency_blocking_bonus(self):
        task1 = {
            'id': 1,
            'title': 'Blocker task',
            'due_date': None,
            'estimated_hours': 2,
            'importance': 6,
            'dependencies': []
        }
        
        task2 = {
            'id': 2,
            'title': 'Dependent task',
            'due_date': None,
            'estimated_hours': 3,
            'importance': 7,
            'dependencies': [1]
        }
        
        all_tasks = [task1, task2]
        score, breakdown = self.scorer.calculate_score(task1, all_tasks)
        self.assertGreater(breakdown['dependencies'], 0)
    
    def test_circular_dependency_detection(self):
        task1 = {'id': 1, 'title': 'Task A', 'dependencies': [2]}
        task2 = {'id': 2, 'title': 'Task B', 'dependencies': [1]}
        
        warnings = self.scorer.detect_circular_dependencies([task1, task2])
        self.assertTrue(len(warnings) > 0)
        self.assertIn('Circular dependency', warnings[0])
    
    def test_strategy_affects_scoring(self):
        task = {
            'id': 1,
            'title': 'Test task',
            'due_date': (self.today + timedelta(days=1)).isoformat(),
            'estimated_hours': 5,
            'importance': 9,
            'dependencies': []
        }
        
        smart_scorer = TaskScorer(strategy='smart')
        impact_scorer = TaskScorer(strategy='impact')
        
        smart_score, _ = smart_scorer.calculate_score(task, [task])
        impact_score, _ = impact_scorer.calculate_score(task, [task])
        
        self.assertNotEqual(smart_score, impact_score)