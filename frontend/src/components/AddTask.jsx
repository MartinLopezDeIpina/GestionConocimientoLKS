const AddTask = ({onTaskAdded}) => {
    const handleSubmit = async (event) => {
        event.preventDefault();
        const form = event.target;
        const title = form.elements.title.value;
        const description = form.elements.description.value;

        const response = await fetch('http://localhost:5000/api/post_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, description })
        });

        if (response.ok) {
            onTaskAdded();
        }
    };

    return(
        <form onSubmit={handleSubmit}>
            <input type="text" placeholder="Title" name="title"/>
            <input type="text" placeholder="Description" name="description"/>
            <button type="submit">Add task</button>
        </form>
    )
}

export default AddTask;