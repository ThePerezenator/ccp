function openSideBar(){
    var isOpen = false;
    var sideBar = document.getElementById("sideBar");
    if (sideBar.style.left == "0px"){
        isOpen = true;
    }
    else{
         isOpen = false;
    }
    if (!isOpen) {
        sideBar.style.left = "0px";
    }
    else if (isOpen) {
        sideBar.style.left = "-200px";
    }

}