
async function addToCart(id){
    let response = await fetch(`/add-to-cart/${id}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie('csrftoken')
        }
    });
    return await response.json();
}

function getCookie(name){
    let v=null;
    document.cookie.split(';').forEach(c=>{
        c=c.trim();
        if(c.startsWith(name+'=')) v=decodeURIComponent(c.split('=')[1]);
    });
    return v;
}
