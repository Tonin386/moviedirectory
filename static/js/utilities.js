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

    let touchstartX = 0;
    let touchendX = 0;

    function handleGesture() {
        if (touchendX < touchstartX) currentIndex++;
        if (touchendX > touchstartX) currentIndex--;

        if (currentIndex < 0) currentIndex = 0;
        else if (currentIndex >= elements.length - 1) currentIndex = elements.length - 1;

        scrollSize = elements[currentIndex].getBoundingClientRect().left
        el.scrollLeft += scrollSize;
    }

    el.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
    });

    el.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX;
        handleGesture();
    });
}


// function scrollWatchListLeft() {

//     if (window.outerWidth < 1200) {
//         currentIndex++;
//         if (currentIndex >= elements.length) currentIndex--;
//         scrollSize = elements[currentIndex].getBoundingClientRect().left;
//         console.log(scrollSize);
//     }
//     else {
//         currentIndex += 6;
//         if (currentIndex >= elements.length) currentIndex = elements.length - 1;
//         scrollSize = elements[currentIndex].getBoundingClientRect().left;
//     }

//     el.scrollLeft += scrollSize;
// }

// function scrollWatchListRight() {

//     if (window.outerWidth < 1200) {
//         currentIndex--;
//         if (currentIndex < 0) currentIndex++;
//         scrollSize = elements[currentIndex].getBoundingClientRect().left;
//     }
//     else {
//         currentIndex -= 6;
//         if (currentIndex < 0) currentIndex = 0;
//         scrollSize = elements[currentIndex].getBoundingClientRect().left;
//     }

//     el.scrollLeft += scrollSize;
// }