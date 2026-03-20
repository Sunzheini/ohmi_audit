function fShowHideCreateForm() {
    let x = document.getElementById("custom_form");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}