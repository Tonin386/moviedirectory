var currentIndex = 0;
var el = document.getElementById("autoscrollList");
var elements = document.getElementsByClassName("infinite-x-child");
var scrollSize = 0;

if (window.outerWidth >= 1200) {

    el.onwheel = function (e) {

        if (e.deltaY > 0) {
            currentIndex++;
        }
        else {
            currentIndex--;
        }

        if (currentIndex < 0) currentIndex = 0;
        else if (currentIndex >= elements.length - 5) currentIndex = elements.length - 5;

        scrollSize = elements[currentIndex].getBoundingClientRect().left
        el.scrollLeft += scrollSize;
    }
}
else {

}

function scrollWatchListLeft() {

    currentIndex--;
    if (currentIndex < 0) currentIndex++;
    scrollSize = elements[currentIndex].getBoundingClientRect().left;
    el.scrollLeft += scrollSize;
    
    if(currentIndex < elements.length - 1) {
        document.getElementById("rightButton").style.display = "block";
    }

    if(currentIndex < 1) {
        document.getElementById("leftButton").style.display = "none";
    }
}

function scrollWatchListRight() {
    currentIndex++;
    if (currentIndex >= elements.length) currentIndex--;
    scrollSize = elements[currentIndex].getBoundingClientRect().left;
    el.scrollLeft += scrollSize;

    if(currentIndex >= elements.length - 1) {
        document.getElementById("rightButton").style.display = "none";
    }
    
    if(currentIndex > 0) {
        document.getElementById("leftButton").style.display = "block";
    }
}