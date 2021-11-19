window.onload=function(){ 
    cor = document.getElementsByClassName("cor_values");
    rate = document.getElementsByClassName("price_value");

    for(i=0;i<cor.length;i++){
        if (cor[i].innerHTML > 0.85){
            cor[i].style.color = "#FF69A3";
            cor[i].style.border = "1px solid #FF69A3";
        }else if(cor[i].innerHTML > 0.6){
            cor[i].style.color = "#0DB99E";
            cor[i].style.border = "1px solid #0DB99E";
        }else if(cor[i].innerHTML <= 0.6){
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
}
