window.onload=function(){
  total_price = document.getElementById("gain_loss_amount");
  total_rate = document.getElementById("gain_loss_percentage");
  rate = document.getElementsByClassName("stock_gain_loss_rate");
  price = document.getElementsByClassName("stock_price");
  price_value1= document.getElementsByClassName("price_value1");
  price_value2= document.getElementsByClassName("price_value2");
  price_value3= document.getElementsByClassName("price_value3");

  if (total_price.innerHTML.slice(0,1) == '-'){
      total_price.style.color = "#0000FF";
      total_rate.style.color = "#0000FF";
  }else{
    total_price.style.color = "#FF0000";
      total_rate.style.color = "#FF0000";
  }

  for(i=0;i<rate.length;i++){
    console.log(1);
    if(Number(rate[i].innerHTML.slice(0,-1))>0){
      rate[i].style.color = "#FF0000";
      price[i].style.color = "#FF0000";
    }else{
      rate[i].style.color = "#0000FF";
      price[i].style.color = "#0000FF";
    }
  }
  document.getElementById("asset_amount").innerHTML = parseInt(document.getElementById("asset_amount").innerHTML).toLocaleString('ko-KR')+"원";
  document.getElementById("buying_amount").innerHTML = parseInt(document.getElementById("buying_amount").innerHTML).toLocaleString('ko-KR')+"원";
  document.getElementById("gain_loss_amount").innerHTML = parseInt(document.getElementById("gain_loss_amount").innerHTML).toLocaleString('ko-KR')+"원";
  for(i=0;i<price.length;i++){
    price[i].innerHTML = parseInt(price[i].innerHTML).toLocaleString('ko-KR')+"원";
    price_value1[i].innerHTML = parseInt(price_value1[i].innerHTML).toLocaleString('ko-KR');
    price_value2[i].innerHTML = parseInt(price_value2[i].innerHTML).toLocaleString('ko-KR');
    price_value3[i].innerHTML = parseInt(price_value3[i].innerHTML).toLocaleString('ko-KR');
  }
}
