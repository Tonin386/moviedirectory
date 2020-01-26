function footer_adjust() {
	var footer = document.getElementById("footer_wrap"); 
	if (document.documentElement.offsetHeight > window.innerHeight) {
		footer.style.position = "relative";
	} 
	else {
		footer.style.position = "absolute";
	} 
} 
footer_adjust();