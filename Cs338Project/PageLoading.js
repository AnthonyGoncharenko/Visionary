window.onload = $(function() {
    var loc = window.location.href;
       $(".navbar .navbar-nav > li").each(function() {
            if (loc.match('/home')) {
                $(this).addClass("active"); 
            }
       });
});