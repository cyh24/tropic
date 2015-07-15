
//失去焦点，验证个数据是够正确

$(function (){
//	$('#bao_email').blur(function() {
//		var bao_email = $('#bao_email').val();
//		var temp=/^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/.test(bao_email);
//		if(temp==false){
//		alert('请输入正确的邮箱地址！');
//		}else{
//			return ;
//		}
//	}) ;
	/*$('#phonenum').blur(function() {
		var phonenum = $('#phonenum').val();
		var temp=/1[3|5|7|8|][0-9]{9}/.test(phonenum);
		if(temp==false){
			alert('请输入正确的邮箱地址！');
		}else{
			return ;
		}
	}) ;*/
	
});

//提交用户报名信息
function applyInfo(){
	$("#userInfo_first").css("display", "none");
	$("#userInfo_second").css("display", "block");
//	alert($("#applyInfoform").serialize());
	$.ajax({
        type: "post",
        url: post_url,
        data:$('#applyInfoform').serialize(),// 你的formid
       // async: false,
        success: function(data) {
        	//alert(data.msg);
        	location.href = re_url;
            
        },
        error: function(request) {
           // alert("Connection error");
        }
    });
	return false;
}

//上一步下一步，样式设定
function gobackfirst(){
	$('.progress-bar').css({'width':'0%'})
	$("#userInfo_first").css("display", "block");
	$("#userInfo_second").css("display", "none");
	
}
function applynextstep(){
	/*var true_name = $('#true_name').val();
	var collage = $('#collage').val();
	var professional = $('#professional').val();
	var hobby = $('#hobby').val();
	var phonenum = $('#phonenum').val();
	var qq = $('#qq').val();
	if(true_name=="" || collage=="" || true_name=="" || professional=="" || hobby=="" || phonenum=="" || qq==""){
		$("#alert-id").css("display", "block");
		return false;
	}*/
	
	
	$('.progress-bar').css({'width':'45%'})
	
	$("#userInfo_first").css("display", "none");
	$("#userInfo_second").css("display", "block");
	
}

//解析url参数
function getQueryString(name) {
	var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
	var r = window.location.search.substr(1).match(reg);
	if (r != null)
		return unescape(r[2]);

	return null;
}

$('div#myCarousel ol.carousel-indicators li').bind({
    'mouseenter' : function(){
        //获取当前元素的索引值
        int = $(this).index();

        //执行函数,这里会显示右侧的第一个div元素
        $('.carousel').carousel(int);
        $('.carousel').carousel('pause');
    },
    'mouseleave' : function(){
        //鼠标划开时的操作
        //int = 0;
        $('.carousel').carousel('cycle');
    }
});


// 图片轮播的左右两个箭头默认是不显示的, 鼠标到了大图上才显示
$('.carousel-control .icon-prev').hide();
$('.carousel-control .icon-next').hide();

// 图片轮播的左右背景图片默认是不显示的, 鼠标到了大图上才显示
$('.carousel-control.left').css('background-image', 'none');
$('.carousel-control.right').css('background-image', 'none');
$('.carousel').bind({
    'mouseover' : function(){
        $('.carousel-control .icon-prev').show();
        $('.carousel-control .icon-next').show();
        $('.carousel-control.left').css('background-image', 'linear-gradient(to right,rgba(0,0,0,.5) 0,rgba(0,0,0,.0001) 100%)');
        $('.carousel-control.right').css('background-image', 'linear-gradient(to right,rgba(0,0,0,.0001) 0,rgba(0,0,0,.5) 100%)');
    },
    'mouseleave' : function() {

        //鼠标划开时的操作
        $('.carousel-control .icon-prev').hide();
        $('.carousel-control .icon-next').hide();
        $('.carousel-control.left').css('background-image', 'none');
        $('.carousel-control.right').css('background-image', 'none');
    }
});

