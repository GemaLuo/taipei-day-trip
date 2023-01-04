const signOut=document.querySelector("#signOut");

fetch("/api/user/auth",{
    method: "GET",
    credentials: "include",
}).then(res=>res.json())
    .then(function(status){
    if(status.data){
       let {name,email, id}=status.data;
       document.querySelectorAll("#name").forEach(function(element, index){
        if (index===0){
            element.textContent=name;
        }
        else{
            element.value=name;
        }
       })
       inputEmail.value=email;
    }else{
        location.href="/";
    }
    return fetch("/api/booking",{
        credentials:"include",
        headers: {
            "Content-Type": "application/json"
        }
    })
})
    .then(res=>res.json())
    .then(function(result){
        order=result.data
        if(result.data){
            let {date, time, price, attraction}=result.data;
            let {name, address, image}=attraction;
            if(time==="morning"){
                time="早上 9 點到下午 4 點";
            }else{
                time="下午 2 點到晚上 9 點";
            };
            price="新台幣 "+price+" 元";
            let data=[name, date, time, price, address]
            document.querySelector(".image>img").src=image;
            spans=document.querySelectorAll(".booking-txt span");
            spans.forEach(function(span, index){
                span.textContent=data[index]
            });
            document.querySelector(".order-fee>span").textContent=price;
            document.querySelectorAll(".booking-section").forEach(element=>{element.style.display="flex"});
            document.querySelector(".order-total").style.display="flex";
            document.querySelector(".noSchedule").style.display="none";
            document.querySelector(".footer-nobooking").style.display="none";
            document.querySelector(".footer").style.display="flex";
        }
    })

document.querySelectorAll(".booking-section").forEach(element=>{
    element.style.display="none"
});
document.querySelector(".order-total").style.display="none";
document.querySelector(".noSchedule").textContent="目前沒有任何待預訂的行程";
document.querySelector(".footer-nobooking").style.display="flex";
document.querySelector(".footer").style.display="none";

//刪除預定行程
document.querySelector(".booking-section>img").addEventListener("click", function(){
    fetch("/api/booking",{
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
    }).then(function(res){
        return res.json();
    }).then(function(res){
        if(res.ok){
            location.reload()
        }
    })
})

//click logout button
signOut.addEventListener("click", function(e){
    fetch("/api/user/auth", {
        "method": "DELETE"
    }).then(function(res){ 
        return res.json();
    }).then(function(data){
        location.reload();
    })
})
const navBooking=document.querySelector('#nav-booking');
navBooking.addEventListener("click", function(){
    location.reload()
})