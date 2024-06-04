import React, { useState, useEffect } from 'react';
import Tarea from './Tarea.jsx';
import AddTask from './AddTask.jsx';

const TaskList = () => {
  const [tasks, setTasks] = useState([]);

  const fetchTasks = async () => {
    console.log('fetching tasks');
    const data = await fetch('http://localhost:5000/api/get_tasks').then(response => response.json());
    setTasks(data);
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
  <>
    <div className='divTasks'>
        {tasks.map(task => (
        <Tarea key={task.id} id={task.id} titulo={task.title} descripcion={task.description} completado={task.done} onTaskDeleted={fetchTasks} />
        ))}
    </div>
    <AddTask onTaskAdded={fetchTasks} />
  </>
);

};

export default TaskList;