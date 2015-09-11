	var trade_state = "NOTPAY";
	var Timer;
	function paycheck()
	{
		$.getJSON('/ajax_check/',function(result){
			trade_state = result['trade_state']
			if( trade_state == "SUCCESS")
			{
				clearInterval(Timer);
				location.href = "/pay_result/";
			}
			else if (result['return_code'] == "FAIL") 
			{
				clearInterval(Timer);
				alert(result['return_msg']);
			}
			else if (result['result_code'] == "FAIL") 
			{
				clearInterval(Timer);
				alert(result['err_code']);
			}
          });
	}
	          
    $(document).ready(function(){
      Timer = setInterval(paycheck, 5000);  
    });