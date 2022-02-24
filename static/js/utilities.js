var currentIndex = 0;
var el = document.getElementById("autoscrollList");
var elements = document.getElementsByClassName("infinite-x-child");
var scrollSize = 0;

function scrollWatchListLeft() {

    if (window.outerWidth < 1200) {
        currentIndex++;
        if (currentIndex >= elements.length) currentIndex--;
        scrollSize = elements[currentIndex].getBoundingClientRect().left;
        console.log(scrollSize);
    }
    else {
        currentIndex += 6;
        if (currentIndex >= elements.length) currentIndex = elements.length - 1;
        scrollSize = elements[currentIndex].getBoundingClientRect().left;
    }

    el.scrollLeft += scrollSize;
}

function scrollWatchListRight() {

    if (window.outerWidth < 1200) {
        currentIndex--;
        if (currentIndex < 0) currentIndex++;
        scrollSize = elements[currentIndex].getBoundingClientRect().left;
    }
    else {
        currentIndex -= 6;
        if (currentIndex < 0) currentIndex = 0;
        scrollSize = elements[currentIndex].getBoundingClientRect().left;
    }

    el.scrollLeft += scrollSize;
}


// element should be replaced with the actual target element on which you have applied scroll, use window in case of no target element.
el.onwheel = function (e) { // or window.addEventListener("scroll"....
    if(e.deltaY > 0) {
        currentIndex++;
    }
    else {
        currentIndex--;
    }
    if(currentIndex < 0) currentIndex = 0;
    else if(currentIndex >= elements.length - 5) currentIndex = elements.length - 5;

    console.log(currentIndex);

    scrollSize = elements[currentIndex].getBoundingClientRect().left

    el.scrollLeft += scrollSize;
}