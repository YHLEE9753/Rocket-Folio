window.onload=function(){ 
  total_price = document.getElementById("gain_loss_amount");
  total_rate = document.getElementById("gain_loss_percentage");
  rate = document.getElementsByClassName("stock_gain_loss_rate");
  price = document.getElementsByClassName("stock_price");
  crypto_price = document.getElementsByClassName("crypto_price");
  crypto_rate = document.getElementsByClassName("crypto_gain_loss_rate");

  if (total_price.innerHTML.slice(0,1) == '+'){
      total_price.style.color = "#FF0000";
      total_rate.style.color = "#FF0000";
  }else{
      total_price.style.color = "#0000FF";
      total_rate.style.color = "#0000FF";
  }

  for(i=0;i<rate.length;i++){
    if(Number(rate[i].innerHTML.slice(0,-1))>0){
      rate[i].style.color = "#FF0000";
      price[i].style.color = "#FF0000";
    }else{
      rate[i].style.color = "#0000FF";
      price[i].style.color = "#0000FF";
    }
  }

  for(i=0;i<crypto_price.length;i++){
    if(Number(crypto_rate[i].innerHTML.slice(0,-1))>0){
      crypto_rate[i].style.color = "#FF0000";
      crypto_price[i].style.color = "#FF0000";
    }else{
      crypto_rate[i].style.color = "#0000FF";
      crypto_price[i].style.color = "#0000FF";
    }
    crypto_price[i].innerHTML = parseInt(crypto_price[i].innerHTML).toLocaleString('ko-KR')+"원";
  }
}
