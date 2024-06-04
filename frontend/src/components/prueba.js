let tareas = await fetch('http://localhost:5000/api/get_tasks').then(response => response.json());

console.log(tareas);