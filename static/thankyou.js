const signOut=document.querySelector("#signOut");

fetch("/api/user/auth",{
    method: "GET",
    credentials: "include",
    headers: {
        "Content-Type": "application/json"
    }
}).then(function(res){
    return res.json()
}).then(function(result){
    if(!result.data){
        return location.href="/"
    }
    return showOrderNumber
})
function showOrderNumber(){
    const orderNumber=(location.search).replace("?number=", "")
    document.querySelector(".order-number>span").textContent=orderNumber
}
showOrderNumber()
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
const book=document.querySelector('#nav-booking');
book.addEventListener("click", function(e){
    alert("請至首頁訂購行程！")
})