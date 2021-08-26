let input = document.getElementById("inputAdmin");
let button = document.getElementById("botonAdmin");
button.disabled = true;
input.addEventListener("change", stateHandle);
function stateHandle() {
    if (input.value === ""){
        button.disabled = false; 
    } else{
    button.disabled = true;
    }
}