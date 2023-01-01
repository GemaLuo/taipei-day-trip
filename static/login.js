//註冊、登入
//nav登入登出按鍵
const sign=document.querySelector("#sign");
const signOut=document.querySelector("#signOut");
signOut.style.display="none";

//verify user status
fetch("/api/user/auth",{
    method: "GET",
    credentials: "include",
    headers:{
        "Content-Type": "application/json"
    }
}).then(function(res){
    return res.json()
}).then(function(status){
    if(status.data){
        sign.style.display="none";
        signOut.style.display="block";
    }
})

//click logout button
signOut.addEventListener("click", function(e){
    fetch("/api/user/auth", {
        "method": "DELETE"
    }).then(function(res){
        return res.json();
    }).then(function(data){
        location.reload();//reloads the current URL
    })
})

//click sign up(button)
const btnSignUp=document.querySelector("#btnSignUp");
const signUpResMsg=document.querySelector("#signUp>.resMessage");
btnSignUp.addEventListener("click", function(e){
    let data={};
    signUpResMsg.style.display="none";
    signUpInput=document.querySelectorAll("#signUp>input");
    const regex=/^[\w-\.]+@([\w-]+\.)+[\w]{2,4}$/
    const InputEmail=signUpInput[1].value;
    for (let i=0; i<signUpInput.length; i++){
        let inputBarData=signUpInput[i].value;
        if (!inputBarData){
            data=null;
            break;
        }
        data[signUpInput[i].id]=signUpInput[i].value;
    }
    //verify input information
    if (!data || !regex.test(InputEmail)){
        signUpResMsg.textContent="輸入資料有誤，請重新輸入";
        signUpResMsg.style.display="block";
        return
    }
    //send data to backend
    fetch("/api/user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then(function(res){
        return res.json();
    }).then(function(data){
        if(data.error){
            signUpResMsg.style.display="block";
            signUpResMsg.textContent=data.message;
            return
        }
        signUpResMsg.style.display="block";
        signUpResMsg.style.color="black";
        signUpResMsg.textContent="已註冊成功，請重新登入";
    })
})

//CLICK LOGIN BUTTON
const btnSignIn=document.querySelector("#btnSignIn");
const signInResMsg=document.querySelector("#signIn>.resMessage");
btnSignIn.addEventListener("click", function(){
    signInResMsg.style.display="none";
    const signInInput=document.querySelectorAll("#signIn>input");
    let data={
        email: signInInput[0].value,
        password: signInInput[1].value
    }
    fetch("/api/user/auth", {
        method: "PUT",
        headers:{
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then(function(res){
        return res.json()
    }).then(function(status){
        if (status.error){
            signInResMsg.style.display="block";
            signInResMsg.textContent="帳號或密碼錯誤";
            return
        }
        location.reload()
    })
})

const dialogMask=document.querySelector(".dialog-mask");
const signIn=document.querySelector("#signIn");
const signUp=document.querySelector("#signUp");
const tapToSignUp=document.querySelector("#tapToSignUp");
tapToSignUp.addEventListener("click", function(){
    signIn.style.display="none";
    signUp.style.display="flex";
    signUpResMsg.style.display="none";
})

const tapToSignIn=document.querySelector("#tapToSignIn");
tapToSignIn.addEventListener("click", function(){
    signIn.style.display="flex";
    signUp.style.display="none";
    signInResMsg.style.display="none";
})

const login=document.querySelectorAll(".login");
login.forEach(closeLogin=>{
    closeLogin.addEventListener("click", function(e){
        if (e.target.className=="close"){
            this.style.display="none";
            dialogMask.style.display="none";
        }
    })
})
sign.addEventListener("click",function(){
    signIn.style.display="flex";
    dialogMask.style.display="block";
})
//nav booking button
document.querySelector("#nav-booking").addEventListener("click", function(){
    if(document.cookie){
        location.href="/booking";
    }else{
        signIn.style.display="flex";
        dialogMask.style.display="block";
    }
})
