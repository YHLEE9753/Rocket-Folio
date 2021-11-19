window.onload=function(){ 
    var cor = document.getElementsByClassName("cor_values");
    var rate = document.getElementsByClassName("price_value");
    var gain_loss_rate = document.getElementsByClassName("stock_gain_loss_rate");
    var stock_price = document.getElementsByClassName("stock_price");


    for(i=0;i<cor.length;i++){
        console.log(cor[i])
        if (cor[i].innerHTML > 0.5){
            cor[i].style.color = "#FF69A3";
            cor[i].style.border = "1px solid #FF69A3";
        }else if(-0.5<=cor[i].innerHTML && cor[i].innerHTML<= 0.5 ){
            cor[i].style.color = "#0DB99E";
            cor[i].style.border = "1px solid #0DB99E";
        }else if(cor[i].innerHTML < -0.5){
            cor[i].style.color = "#000000";
            cor[i].style.border = "1px solid #000000";
        }else{
            cor[i].style.color = "#000000";
            cor[i].style.border = "0px";
            cor[i].style.fontSize = "18px";
            cor[i].style.fontFamily = "Apple SD Gothic Neo";
            cor[i].style.fontWeight = "550";
        }
    }

    for(i=0;i<rate.length;i++){
        if (rate[i].innerHTML.slice(0, 1) == "+"){
            rate[i].style.color = "#FF0000";
        }else if(rate[i].innerHTML.slice(0, 1) == "-"){
            rate[i].style.color = "#0000FF";
        }else{
            rate[i].style.color = "#000000";
        }
    }

    for(i=0;i<gain_loss_rate.length;i++){
        if(gain_loss_rate[i].innerHTML.slice(0, 1) == "-"){
            gain_loss_rate[i].style.color = "#0000FF";
            stock_price[i].style.color = "#0000FF";
        }else{
            gain_loss_rate[i].style.color = "#FF0000";
            stock_price[i].style.color = "#FF0000";
        }
    }
}