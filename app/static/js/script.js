//the header
let menu = document.querySelector('#menu');
let nav =document.querySelector('.nav');
menu.onclick=()=>{
    menu.classList.toggle('fa-times');
    nav.classList.toggle('active');
}
//window scrolling
window.onscroll = () =>{
    menu.classList.remove('fa-times');
    nav.classList.remove('active');
    if(window.scrollY>0){
        document.querySelector('.theheader').classList.add('active');
    }
    else{
        document.querySelector('.theheader').classList.remove('active');
    }
    window.onload=()=>{
        if(window.scrollY>0){
            document.querySelector('.theheader').classList.add('active');
        }
        else{
            document.querySelector('.theheader').classList.remove('active');
        }
    }
}
//home section
var swiper = new Swiper(".silder", {
    spaceBetween: 20,
    effect: "fade",
    grabCursor:true,
    loop:true,
    centeredSliders:true,
    autoplay: {
        delay: 2500,
        disableOnInteraction: false,
      },
  });
  //feature
  var swiper = new Swiper(".featureslider", {
    spaceBetween: 20,
    grabCursor:true,
    loop:true,
    centeredSlides:true,
    autoplay: {
        delay: 9500,
        disableOnInteraction: false,
      },
      breakpoints:{
        0:{
            slidesPerView:1,
        },
        768:{
            slidesPerView:2,
        },
        991:{
            slidesPerView:3,
        },
      },
  });