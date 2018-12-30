/* automatically load dependents */
(function() {
var scripts = document.getElementsByTagName("script");
var src = scripts[scripts.length-1].src;
var folder = src.substr(0, src.lastIndexOf('/'));
document.write('<script src="' + folder + '/jquery.js"></script>');
document.write('<script src="' + folder + '/jquery.cookie.js"></script>');
})();
