// 첫 화면 로딩시 실행되는 함수. 상위 10개의 종목만 보여준다.
window.onload=function(){ 
    item = document.getElementsByClassName("stock_item");
    for(i=0;i<item.length;i++){
      if(0<i && i<11){
        item[i].style.display = "flex";
      }else{
        item[i].style.display = "none";
      } 
    }
  }
function filter() {
  var value, name, item, i, stockList;
  value = document.getElementById("value").value;
  item = document.getElementsByClassName("stock_item");

  stockList = []

  for (i = 0; i < item.length; i++) {
    item[i].style.display = "none";
    name = item[i].getElementsByClassName("stock_btn");
    
    if (name[0].innerHTML.indexOf(value) > -1) {  
      stockList.push(item[i]);
    } else {
      item[i].style.display = "none";
    }
  }
  
  for (i = 0; i < 10; i++){
    stockList[i].style.display = "flex";
  }
}

function changeinput(code) {
  item = document.getElementsByClassName("stock_item");
  for (i = 0; i < item.length; i++) {
    if (item[i].childNodes[1].childNodes[1].childNodes[3].innerHTML == code){
      console.log(item[i].childNodes[1].childNodes[1].childNodes[3].innerHTML)
      var stockName = item[i].childNodes[1].childNodes[1].childNodes[1].innerHTML;
      break
    }
  }
  console.log(stockName);
  console.log(code)
  const element = document.getElementsByClassName("searh_bar");
  console.log(element);
  element.value = stockName;
}

function onDisplay(){
  $('.number_and_price_container').show();
  $('.stock_item').hide();
}

function onHide(){
  $('.number_and_price_container').hide();
  $('.stock_item').show();
}