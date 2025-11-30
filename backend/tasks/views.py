from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from .scoring import TaskScorer, generate_explanation

@api_view(['POST'])
def analyze_tasks(request):
    tasks_data = request.data.get('tasks', [])
    strategy = request.data.get('strategy', 'smart')
    
    if not tasks_data:
        return Response({'error': 'No tasks provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not isinstance(tasks_data, list):
        return Response({'error': 'Tasks must be an array'}, status=status.HTTP_400_BAD_REQUEST)
    
    validated_tasks = []
    errors = []
    
    for idx, task_data in enumerate(tasks_data):
        serializer = TaskSerializer(data=task_data)
        if serializer.is_valid():
            validated_tasks.append(serializer.validated_data)
        else:
            errors.append({'task_index': idx, 'errors': serializer.errors})
    
    if errors:
        return Response(
            {'error': 'Validation failed for some tasks', 'details': errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    scorer = TaskScorer(strategy=strategy)
    circular_warnings = scorer.detect_circular_dependencies(validated_tasks)
    
    scored_tasks = []
    for task in validated_tasks:
        score, breakdown = scorer.calculate_score(task, validated_tasks)
        explanation = generate_explanation(task, breakdown, strategy)
        
        task_with_score = {
            **task,
            'priority_score': score,
            'explanation': explanation
        }
        scored_tasks.append(task_with_score)
    
    scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    
    response_data = {
        'strategy': strategy,
        'tasks': scored_tasks,
        'total_tasks': len(scored_tasks)
    }
    
    if circular_warnings:
        response_data['warnings'] = circular_warnings
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def suggest_tasks(request):
    tasks_data = request.data.get('tasks', [])
    strategy = request.data.get('strategy', 'smart')
    
    if not tasks_data:
        return Response({'error': 'No tasks provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    validated_tasks = []
    for task_data in tasks_data:
        serializer = TaskSerializer(data=task_data)
        if serializer.is_valid():
            validated_tasks.append(serializer.validated_data)
    
    if not validated_tasks:
        return Response({'error': 'No valid tasks to suggest'}, status=status.HTTP_400_BAD_REQUEST)
    
    scorer = TaskScorer(strategy=strategy)
    scored_tasks = []
    
    for task in validated_tasks:
        score, breakdown = scorer.calculate_score(task, validated_tasks)
        explanation = generate_explanation(task, breakdown, strategy)
        
        task_with_score = {
            **task,
            'priority_score': score,
            'explanation': explanation,
            'score_breakdown': breakdown
        }
        scored_tasks.append(task_with_score)
    
    scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    top_tasks = scored_tasks[:3]
    
    return Response({
        'strategy': strategy,
        'suggested_tasks': top_tasks,
        'total_analyzed': len(scored_tasks)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'message': 'Task Analyzer API is running'})