var currentIndex = 0;

function scrollWatchListLeft() {

    console.log(currentIndex);

    var elements = document.getElementsByClassName("infinite-x-child");
    var scrollSize = 0;

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

    var el = document.getElementById("watchlist");
    el.scrollLeft += scrollSize;
}

function scrollWatchListRight() {

    console.log(currentIndex);

    var elements = document.getElementsByClassName("infinite-x-child");
    var scrollSize = 0;

    if (window.outerWidth < 1200) {
        currentIndex--;
        if (currentIndex < 0) currentIndex++;
        scrollSize = elements[currentIndex].getBoundingClientRect().left;
    }
    else {
        currentIndex -= 6;
        if (currentIndex < 0) currentIndex = 0;
        scrollSize += elements[currentIndex].getBoundingClientRect().left;
    }

    var el = document.getElementById("watchlist");
    el.scrollLeft += scrollSize;
}