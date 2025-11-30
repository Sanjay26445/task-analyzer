// Task storage
let tasks = [];

// API Base URL - change this if your Django runs on different port
const API_BASE_URL = 'http://localhost:8000/api';

// DOM elements
const taskForm = document.getElementById('task-form');
const clearFormBtn = document.getElementById('clear-form');
const jsonInput = document.getElementById('json-input');
const pasteJsonBtn = document.getElementById('paste-json');
const clearJsonBtn = document.getElementById('clear-json');
const analyzeBtn = document.getElementById('analyze');
const tasksList = document.getElementById('tasks-list');
const analysisResult = document.getElementById('analysis-result');
const strategySelect = document.getElementById('strategy');

// Form inputs
const titleInput = document.getElementById('title');
const dueDateInput = document.getElementById('due_date');
const estimatedHoursInput = document.getElementById('estimated_hours');
const importanceInput = document.getElementById('importance');
const dependenciesInput = document.getElementById('dependencies');

// Add task from form
taskForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const title = titleInput.value.trim();
  if (!title) return;
  
  const task = {
    id: Date.now(),
    title: title,
    due_date: dueDateInput.value || null,
    estimated_hours: parseFloat(estimatedHoursInput.value) || 0,
    importance: parseInt(importanceInput.value) || 5,
    dependencies: dependenciesInput.value 
      ? dependenciesInput.value.split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d))
      : []
  };
  
  tasks.push(task);
  renderTasks();
  taskForm.reset();
  titleInput.focus();
});

// Clear form
clearFormBtn.addEventListener('click', () => {
  taskForm.reset();
  titleInput.focus();
});

// Load JSON
pasteJsonBtn.addEventListener('click', () => {
  try {
    const jsonData = JSON.parse(jsonInput.value);
    
    if (!Array.isArray(jsonData)) {
      alert('JSON must be an array of tasks');
      return;
    }
    
    jsonData.forEach((item, index) => {
      const task = {
        id: Date.now() + index,
        title: item.title || 'Untitled Task',
        due_date: item.due_date || null,
        estimated_hours: parseFloat(item.estimated_hours) || 0,
        importance: parseInt(item.importance) || 5,
        dependencies: Array.isArray(item.dependencies) ? item.dependencies : []
      };
      tasks.push(task);
    });
    
    renderTasks();
    jsonInput.value = '';
    alert(`Added ${jsonData.length} task(s) successfully!`);
    
  } catch (error) {
    alert('Invalid JSON format. Please check your input.');
    console.error(error);
  }
});

// Clear JSON
clearJsonBtn.addEventListener('click', () => {
  jsonInput.value = '';
});

// Analyze tasks - NOW CALLS BACKEND API
analyzeBtn.addEventListener('click', async () => {
  if (tasks.length === 0) {
    alert('Please add some tasks first!');
    return;
  }
  
  const strategy = strategySelect.value;
  
  // Show loading state
  analysisResult.innerHTML = '<div class="empty">Analyzing tasks...</div>';
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = 'Analyzing...';
  
  try {
    // Call Django API
    const response = await fetch(`${API_BASE_URL}/tasks/analyze/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tasks: tasks,
        strategy: strategy
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to analyze tasks');
    }
    
    const data = await response.json();
    renderAnalysis(data, strategy);
    
    // Show warnings if any (e.g., circular dependencies)
    if (data.warnings && data.warnings.length > 0) {
      alert('⚠️ Warnings:\n' + data.warnings.join('\n'));
    }
    
  } catch (error) {
    console.error('Error analyzing tasks:', error);
    analysisResult.innerHTML = `
      <div class="empty" style="color: #fca5a5;">
        ❌ Error: ${error.message}<br><br>
        Make sure Django server is running on ${API_BASE_URL}
      </div>
    `;
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Analyze';
  }
});

// Render tasks list
function renderTasks() {
  if (tasks.length === 0) {
    tasksList.innerHTML = '<div class="empty">No tasks added.</div>';
    tasksList.classList.add('empty');
    return;
  }
  
  tasksList.classList.remove('empty');
  tasksList.innerHTML = tasks.map(task => {
    const priorityClass = task.importance >= 8 ? 'priority-high' 
      : task.importance >= 5 ? 'priority-medium' 
      : 'priority-low';
    
    const priorityLabel = task.importance >= 8 ? 'High' 
      : task.importance >= 5 ? 'Medium' 
      : 'Low';
    
    return `
      <div class="task-item">
        <div class="task-title">
          ${task.title}
          <span class="task-priority ${priorityClass}">${priorityLabel}</span>
        </div>
        ${task.due_date ? `<div class="task-meta">📅 Due: ${formatDate(task.due_date)}</div>` : ''}
        ${task.estimated_hours > 0 ? `<div class="task-meta">⏱️ Estimated: ${task.estimated_hours}h</div>` : ''}
        <div class="task-meta">⭐ Importance: ${task.importance}/10</div>
        ${task.dependencies.length > 0 ? `<div class="task-meta">🔗 Dependencies: ${task.dependencies.join(', ')}</div>` : ''}
      </div>
    `;
  }).join('');
}

// Render analysis results from API
function renderAnalysis(data, strategy) {
  const strategyNames = {
    'smart': 'Smart Balance',
    'fastest': 'Fastest Wins',
    'impact': 'High Impact',
    'deadline': 'Deadline Driven'
  };
  
  const strategyDescriptions = {
    'smart': 'Optimized balance of urgency, importance, and effort',
    'fastest': 'Tasks sorted by shortest estimated time',
    'impact': 'Tasks sorted by highest importance rating',
    'deadline': 'Tasks sorted by closest deadline first'
  };
  
  const sortedTasks = data.tasks;
  
  analysisResult.classList.remove('empty');
  analysisResult.innerHTML = `
    <div style="margin-bottom: 16px; padding: 12px; background: rgba(59, 130, 246, 0.15); border-radius: 8px; border-left: 4px solid var(--primary);">
      <div style="font-weight: 700; font-size: 15px; margin-bottom: 4px;">
        ${strategyNames[strategy]}
      </div>
      <div style="font-size: 13px; color: var(--muted);">
        ${strategyDescriptions[strategy]}
      </div>
      <div style="font-size: 12px; color: var(--muted); margin-top: 8px;">
        Analyzed ${data.total_tasks} task(s)
      </div>
    </div>
    ${sortedTasks.map((task, index) => {
      const priorityClass = task.importance >= 8 ? 'priority-high' 
        : task.importance >= 5 ? 'priority-medium' 
        : 'priority-low';
      
      const priorityLabel = task.importance >= 8 ? 'High' 
        :task.importance >= 5 ? 'Medium'
: 'Low';
return `
    <div class="result-item">
      <div class="result-number">${index + 1}</div>
      <div class="task-title">
        ${task.title}
        <span class="task-priority ${priorityClass}">${priorityLabel}</span>
      </div>
      <div style="margin: 8px 0; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 6px; font-size: 13px;">
        <strong>Priority Score:</strong> ${task.priority_score} <br>
        <strong>Why:</strong> ${task.explanation}
      </div>
      ${task.due_date ? `<div class="task-meta">📅 Due: ${formatDate(task.due_date)}</div>` : ''}
      ${task.estimated_hours > 0 ? `<div class="task-meta">⏱️ Estimated: ${task.estimated_hours}h</div>` : ''}
      <div class="task-meta">⭐ Importance: ${task.importance}/10</div>
      ${task.dependencies.length > 0 ? `<div class="task-meta">🔗 Dependencies: ${task.dependencies.join(', ')}</div>` : ''}
    </div>
  `;
}).join('')}
`;
}
// Format date helper
function formatDate(dateString) {
const date = new Date(dateString);
const options = { month: 'short', day: 'numeric', year: 'numeric' };
return date.toLocaleDateString('en-US', options);
}
// Initialize
renderTasks();