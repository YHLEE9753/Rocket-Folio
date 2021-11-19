window.onload=function(){ 
    total_price = document.getElementById("gain_loss_amount");
    total_rate = document.getElementById("gain_loss_percentage");
    rate = document.getElementsByClassName("stock_gain_loss_rate");

    if (Number(total_price.innerHTML.slice(0,-1))>0){
        total_price.style.color = "#FF0000";
        total_rate.style.color = "#FF0000";
    }else{
        total_price.style.color = "#0000FF";
        total_rate.style.color = "#0000FF";
    }

    for(i=0;i<rate.length;i++){
        if(Number(rate[i].innerHTML.slice(0,-1))>0){
          rate[i].style.color = "#FF0000";
        }else{
          rate[i].style.color = "#0000FF";
        } 
    }
}
