//meishi开始
// $(document).ready(function(){
    // $(".meishi").click(function(){
        // if ($('.meishi22').hasClass('grade-w-roll')) {
            // $('.meishi22').removeClass('grade-w-roll');
			// $(this).removeClass('current');
			// $('.screening').attr('style',' ');
        // } else {
            // $('.meishi22').addClass('grade-w-roll');
			// $(this).addClass('current');
			// $(".Regional").removeClass('current');
			// $(".Brand").removeClass('current');
			// $(".Sort").removeClass('current');
			// $('.screening').attr('style','position: fixed;top:0;');
        // }
    // });
// });

// $(document).ready(function(){
    // $(".meishia-w>li").click(function(){
        // $(".meishia-t")
            // .css("left","50%")
    // });
// });

// $(document).ready(function(){
    // $(".meishia-t>li").click(function(){
        // $(".meishia-s")
            // .css("left","50%")
    // });
// });





//Regional开始
$(document).ready(function(){
    $(".Regional").click(function(){
        if ($('.grade-eject').hasClass('grade-w-roll')) {
            $('.grade-eject').removeClass('grade-w-roll');
			$(this).removeClass('current');
			$('.screening').attr('style',' ');
        } else {
            $('.grade-eject').addClass('grade-w-roll');
			$(this).addClass('current');
			$(".meishi").removeClass('current');
			$(".Brand").removeClass('current');
			$(".Sort").removeClass('current');
			$('.screening').attr('style','position: fixed;');
        }
    });
});

$(document).ready(function(){
    $(".grade-w>li").click(function(){
        $(".grade-t")
            .css("left","50%")
    });
});

// $(document).ready(function(){
    // $(".grade-t>li").click(function(){
        // $(".grade-s")
            // .css("left","50%")
    // });
// });

//Brand开始

// $(document).ready(function(){
    // $(".Brand").click(function(){
        // if ($('.Category-eject').hasClass('grade-w-roll')) {
            // $('.Category-eject').removeClass('grade-w-roll');
			// $(this).removeClass('current');
			// $('.screening').attr('style',' ');
        // } else {
            // $('.Category-eject').addClass('grade-w-roll');
			// $(this).addClass('current');
			// $(".meishi").removeClass('current');
			// $(".Regional").removeClass('current');
			// $(".Sort").removeClass('current');
			// $('.screening').attr('style','position: fixed;');
        // }
    // });
// });



//Sort开始

// $(document).ready(function(){
    // $(".Sort").click(function(){
        // if ($('.Sort-eject').hasClass('grade-w-roll')) {
            // $('.Sort-eject').removeClass('grade-w-roll');
			// $(this).removeClass('current');
			// $('.screening').attr('style',' ');
        // } else {
            // $('.Sort-eject').addClass('grade-w-roll');
			// $(this).addClass('current');
			// $(".meishi").removeClass('current');
			// $(".Regional").removeClass('current');
			// $(".Brand").removeClass('current');
			// $('.screening').attr('style','position: fixed;top:0;');
        // }
    // });
// });


//判断页面是否有弹出
// $(document).ready(function(){
    // $(".meishi").click(function(){
        // if ($('.Category-eject').hasClass('grade-w-roll')){
            // $('.Category-eject').removeClass('grade-w-roll');
        // };
    // });
// });
// $(document).ready(function(){
    // $(".meishi").click(function(){
        // if ($('.Sort-eject').hasClass('grade-w-roll')){
            // $('.Sort-eject').removeClass('grade-w-roll');
        // };
    // });
// });$(document).ready(function(){
    // $(".meishi").click(function(){
        // if ($('.grade-eject').hasClass('grade-w-roll')){
            // $('.grade-eject').removeClass('grade-w-roll');
        // };
    // });
// });






// $(document).ready(function(){
    // $(".Regional").click(function(){
        // if ($('.Category-eject').hasClass('grade-w-roll')){
            // $('.Category-eject').removeClass('grade-w-roll');
        // };
    // });
// });
// $(document).ready(function(){
    // $(".Regional").click(function(){
        // if ($('.Sort-eject').hasClass('grade-w-roll')){
            // $('.Sort-eject').removeClass('grade-w-roll');
        // };
    // });
// });
// $(document).ready(function(){
    // $(".Regional").click(function(){
        // if ($('.meishi22').hasClass('grade-w-roll')){
            // $('.meishi22').removeClass('grade-w-roll');
        // };

    // });
// });





// $(document).ready(function(){
    // $(".Brand").click(function(){
        // if ($('.Sort-eject').hasClass('grade-w-roll')){
            // $('.Sort-eject').removeClass('grade-w-roll');
        // };
    // });
// });
// $(document).ready(function(){
    // $(".Brand").click(function(){
        // if ($('.grade-eject').hasClass('grade-w-roll')){
            // $('.grade-eject').removeClass('grade-w-roll');
        // };
    // });
// });
// $(document).ready(function(){
    // $(".Brand").click(function(){
        // if ($('.meishi22').hasClass('grade-w-roll')){
            // $('.meishi22').removeClass('grade-w-roll');
        // };
    // });
// });





// $(document).ready(function(){
    // $(".Sort").click(function(){
        // if ($('.Category-eject').hasClass('grade-w-roll')){
            // $('.Category-eject').removeClass('grade-w-roll');
        // };
    // });
// });
// $(document).ready(function(){
    // $(".Sort").click(function(){
        // if ($('.grade-eject').hasClass('grade-w-roll')){
            // $('.grade-eject').removeClass('grade-w-roll');
        // };

    // });
// });
// $(document).ready(function(){
    // $(".Sort").click(function(){
        // if ($('.meishi22').hasClass('grade-w-roll')){
            // $('.meishi22').removeClass('grade-w-roll');
        // };

    // });
// });



//js点击事件监听开始

// function meishia(wbj){
    // var arr = document.getElementById("meishia").getElementsByTagName("li");
    // for (var i = 0; i < arr.length; i++){
        // var a = arr[i];
        // a.style.background = "";
    // };
    // wbj.style.background = "#eee"
// }

// function meishib(tbj){
    // var arr = document.getElementById("meishib").getElementsByTagName("li");
    // for (var i = 0; i < arr.length; i++){
        // var a = arr[i];
        // a.style.background = "";
    // };
// }

// function meishis(sbj){
    // var arr = document.getElementById("meishis").getElementsByTagName("li");
    // for (var i = 0; i < arr.length; i++){
        // var a = arr[i];
        // a.style.borderBottom = "";
    // };
    // sbj.style.borderBottom = "solid 1px #ff7c08"
// }




function grade1(wbj, id){
    var xx = document.getElementsByName("province");
    for( var i = 0; i < xx.length; i++) {
        var x = xx[i];
        x.style.background = "#fff";
    }

    var zz = document.getElementsByClassName("grade-t");
    for( var i = 0;  i < zz.length; i++) {
        zz[i].style.left="50%";
        zz[i].style.display="none";
    }

    var yy = document.getElementsByName("city");
    for( var i = 0; i < yy.length; i++) {
        var y = yy[i];
        y.style.display="none";
    }

    document.getElementById(id).style.display="block";
    document.getElementById(id).onclick=null;
    var arr = document.getElementById(id).getElementsByTagName("li");
    for (var i = 0; i < arr.length; i++){
        var a = arr[i];
        a.style.background = "#eee";
        var city_id = a.id;
        // document.getElementById(city_id).onclick=alert(city_id);
        a.style.display="block";
    };
    wbj.style.background = "#eee";
}

// function gradet(tbj){
    // var arr = document.getElementById("gradet").getElementsByTagName("li");
    // for (var i = 0; i < arr.length; i++){
        // var a = arr[i];
        // a.style.background = "";
    // };
// }

// function grades(sbj){
    // var arr = document.getElementById("grades").getElementsByTagName("li");
    // for (var i = 0; i < arr.length; i++){
        // var a = arr[i];
        // a.style.borderBottom = "";
    // };
    // sbj.style.borderBottom = "solid 1px #ff7c08"
// }

// function Categorytw(wbj){
    // var arr = document.getElementById("Categorytw").getElementsByTagName("li");
    // for (var i = 0; i < arr.length; i++){
        // var a = arr[i];
        // a.style.background = "";
    // };
	// wbj.style.background = "#eee"
// }

// function Categoryt(tbj){
    // var arr = document.getElementById("Categoryt").getElementsByTagName("li");
    // for (var i = 0; i < arr.length; i++){
        // var a = arr[i];
        // a.style.background = "";
    // };
// }

// function Categorys(sbj){
    // var arr = document.getElementById("Categorys").getElementsByTagName("li");
    // for (var i = 0; i < arr.length; i++){
        // var a = arr[i];
        // a.style.borderBottom = "";
    // };
    // sbj.style.borderBottom = "solid 1px #ff7c08"
// }

// function Sorts(sbj){
    // var arr = document.getElementById("Sort-Sort").getElementsByTagName("li");
    // for (var i = 0; i < arr.length; i++){
        // var a = arr[i];
        // a.style.background = "";
    // };
    // sbj.style.background = "#eee"
// }
