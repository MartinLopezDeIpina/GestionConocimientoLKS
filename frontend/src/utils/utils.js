
//todo: usarlo en treecall también

export async function getUser(BACKEND_URL){
    let response = await fetch(`${BACKEND_URL}/protected`, {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
        },
    });
    if(!response.ok){
        throw new Error("Error en el protected");
    }
    return await response.json();
}