$(function(){
    //弹窗关闭
    $(".zg17_fix h3 span").click(function(){
        $(".zg17_fix,.zg17_fix_bj").hide();
    })


    $(".up").hover(function(){
        var index=$(this).index();
        $(this).css("box-shadow", "0px 5px 15px #e4e4e4")
        $(".down").eq(index-1).show();
    },function(){
        var index=$(this).index();
        $(".down").eq(index-1).hide();
        $(this).css("box-shadow","")
    });

    $(".down a").click(function(){
        $(".up").removeClass("on");
        $(this).parents(".up").addClass("on");

    })


    $(".xk_xp").click(function(){
        var index=$(this).index();
        $(".xk_xp").removeClass("xk_xl_hover").eq(index-1).addClass("xk_xl_hover")
        $(".xk_zh").removeClass("diyi")
    });
    $(".xk_zh").click(function(){
        $(".xk_xp").removeClass("xk_xl_hover")
        $(".xk_zh").addClass("diyi")
    });

    $(".zhibo2").click(function(){

        if($(this).attr("hove")!="1"){
            $(".zhibo2").addClass("on").attr("hove","1")
        }else{
            $(".zhibo2").removeClass("on").attr("hove","2")
        }

    });

    $(".zibi .zhibo1").click(function(){
        var index=$(this).index();
        if($(this).attr("hove")!="1"){
            $(".xk_nav1_zb .zhibo1").eq(index).addClass("on").attr("hove","1")
        }else{
            $(".xk_nav1_zb .zhibo1").eq(index).removeClass("on").attr("hove","2")
        }

    });

   $(".xk_nav_zb .aa").click(function(){
        var indexs=$(this).index();
        console.log(indexs)
        $(".xk_nav_zb .aa").removeClass("on").eq(indexs).addClass("on")
    })

    $(".mfkc.aa").click(function(){
        var indexs=$(this).index();
        $(".mfkc.aa").removeClass("on").eq(indexs-5).addClass("on")
    })


    var time=new Date();
    var year=time.getFullYear();
    $(".year").html(year)

    $(".jgqj").hover(function(){
        $(".price-select").show();
        $(".jgqj .jiage").addClass("on")
    },function(){
        $(".price-select").hide();
        $(".jiage").removeClass("on")
    })

    $(".off_zhen_right .m_lisr").hover(function(){
        var index=$(this).index();
        $(".lists").eq(index/2-1).css("display","block")
    },function(){
        var index=$(this).index();
        $(".lists").eq(index/2-1).css("display","none")
    })

    $(".zb_nav a").click(function(){
        var index=$(this).index();
        $(".zb_nav a").removeClass("active").eq(index).addClass("active");
    })

    $('.xk_nav_zb span').live('click',function(){
        location.href = $(this).attr('data_url');
    });
    $(".zb_nav a").eq(2).addClass("gk");
$(".up").eq(1).addClass("shiye");


})
