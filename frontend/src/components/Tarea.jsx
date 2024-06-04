import '/public/styles/tasks.css';

const Tarea = ({ id, titulo, descripcion, completado, onTaskDeleted }) => {

    const deleteTask = async () => {
        console.log(`key: ${id}`);
        const response = await fetch(`http://localhost:5000/api/delete_task/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ })
        });

        if (response.ok) {
            onTaskDeleted();
        }
    }

    return (
        <>
        <div className='divTarea'>
            <div>
                <h3>{titulo}</h3>
                <p>{descripcion}</p>
                <p>{completado ? 'Completado' : 'Pendiente'}</p>
            </div>
            <button onClick={deleteTask}>Eliminar</button>
        </div>
        </>
    );
}

export default Tarea;