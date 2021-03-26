function footer_adjust() {
	var footer = document.getElementById("footer_wrap"); 
	if (document.documentElement.offsetHeight > window.innerHeight) {
		footer.style.position = "relative";
	} 
	else {
		footer.style.position = "absolute";
	} 
} 
window.onload = footer_adjust();

$(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.document.location = $(this).data("href");
    });
});
