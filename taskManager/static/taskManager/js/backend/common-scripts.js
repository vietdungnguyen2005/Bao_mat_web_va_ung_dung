/*---LEFT BAR ACCORDION (Thay thế dcAccordion)----*/
jQuery('#sidebar .sub-menu > a').click(function () {
    var last = jQuery('.sub-menu.open', $('#sidebar'));
    
    // Nếu bấm vào cái đang mở -> Đóng nó lại
    last.removeClass("open");
    jQuery('.arrow', last).removeClass("open");
    jQuery('.sub', last).slideUp(200);
    
    var sub = jQuery(this).next();
    // Nếu bấm vào cái mới -> Mở nó ra
    if (sub.is(":visible")) {
        jQuery('.arrow', jQuery(this)).removeClass("open");
        jQuery(this).parent().removeClass("open");
        sub.slideUp(200);
    } else {
        jQuery('.arrow', jQuery(this)).addClass("open");
        jQuery(this).parent().addClass("open");
        sub.slideDown(200);
    }
});

/* Khởi tạo Peity (Thay thế Sparkline) */
$(function() {
    // Vẽ biểu đồ đường
    $(".peity-line").peity("line", {
        fill: null,
        stroke: '#4d90fe',
        width: 100
    });

    // Vẽ biểu đồ cột
    $(".peity-bar").peity("bar", {
        fill: ["#4d90fe"],
        width: 100
    });

    // Vẽ biểu đồ tròn
    $(".peity-pie").peity("pie", {
        fill: ["#4d90fe", "#d7d7d7"]
    });
});

/* Toggle Right Sidebar (Thay thế slidebars.min.js) */
$('.sb-toggle-right').click(function (e) {
    e.preventDefault(); 
    $('.sb-slidebar').toggleClass('active');
});

var Script = function () {

    // Sidebar dropdown menu auto scrolling (Thay thế scrollTo)
    jQuery('#sidebar .sub-menu > a').click(function () {
        var o = ($(this).offset());
        var diff = 250 - o.top;
        if(diff > 0)
            $("#sidebar").animate({ scrollTop: '-=' + Math.abs(diff) }, 500);
        else
            $("#sidebar").animate({ scrollTop: '+=' + Math.abs(diff) }, 500);
    });

    // Sidebar toggle (Responsive)
    $(function() {
        function responsiveView() {
            var wSize = $(window).width();
            if (wSize <= 768) {
                $('#container').addClass('sidebar-close');
                $('#sidebar > ul').hide();
            }
            if (wSize > 768) {
                $('#container').removeClass('sidebar-close');
                $('#sidebar > ul').show();
            }
        }
        $(window).on('load', responsiveView);
        $(window).on('resize', responsiveView);
    });

    $('.fa-bars').click(function () {
        if ($('#sidebar > ul').is(":visible") === true) {
            $('#main-content').css({'margin-left': '0px'});
            $('#sidebar').css({'margin-left': '-210px'});
            $('#sidebar > ul').hide();
            $("#container").addClass("sidebar-closed");
        } else {
            $('#main-content').css({'margin-left': '210px'});
            $('#sidebar > ul').show();
            $('#sidebar').css({'margin-left': '0'});
            $("#container").removeClass("sidebar-closed");
        }
    });

    // Widget tools
    jQuery('.panel .tools .fa-chevron-down').click(function () {
        var el = jQuery(this).parents(".panel").children(".panel-body");
        if (jQuery(this).hasClass("fa-chevron-down")) {
            jQuery(this).removeClass("fa-chevron-down").addClass("fa-chevron-up");
            el.slideUp(200);
        } else {
            jQuery(this).removeClass("fa-chevron-up").addClass("fa-chevron-down");
            el.slideDown(200);
        }
    });

    jQuery('.panel .tools .fa-times').click(function () {
        jQuery(this).parents(".panel").parent().remove();
    });

    // Tooltips & Popovers
    $('.tooltips').tooltip();
    $('.popovers').popover();

    // Custom Bar Chart (Đã sửa XSS)
    if ($(".custom-bar-chart")) {
        $(".bar").each(function () {
            // FIX: Dùng .text() thay vì .html() để chống XSS
            var i = $(this).find(".value").text();
            $(this).find(".value").text("");
            $(this).find(".value").animate({
                height: i
            }, 2000)
        })
    }

}();