TPDirect.setupSDK(127041,'app_JKfppmuL4y08ycLnLaxKO8dnUP36wQffWPuUHCuMbgmen5FdNpKuAfBrVfDR', 'sandbox');
TPDirect.ccv.setupCardType(TPDirect.CardType.VISA);
TPDirect.ccv.setupCardType(TPDirect.CardType.JCB);
TPDirect.ccv.setupCardType(TPDirect.CardType.AMEX);
TPDirect.ccv.setupCardType(TPDirect.CardType.MASTERCARD);
TPDirect.ccv.setupCardType(TPDirect.CardType.UNIONPAY);
TPDirect.ccv.setupCardType(TPDirect.CardType.UNKNOWN);

const phone=document.querySelector("#phoneNumber");
const submitButton=document.querySelector(".pay-button");
const inputName=document.querySelector("input")
const phoneRegex=/^09+\d{8}$/
const emailRegex=/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/
const inputEmail=document.querySelector("input[type='email']")

//credit card info
TPDirect.card.setup({
    fields :{
        number: {
            element: '#card-number',
            placeholder: '**** ***** **** ****'
        },
        expirationDate: {
            element: '#card-expiration-date',
            placeholder: 'MM / YY'
        },
        ccv: {
            element: '#card-ccv',
            placeholder: 'CCV'
        }
    },
    styles: {
        'input': {
            'color': 'gray'
        },
        ':focus': {
            'color': 'gray'
        },
        '.valid': {
            'color': 'green'
        },
        '.invalid': {
            'color': 'orange'
        },
    },
    // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
    isMaskCreditCardNumber: true,
    maskCreditCardNumberRange: {
        beginIndex: 6,
        endIndex: 11
    }
})

TPDirect.card.onUpdate(function (update){
    if(update.canGetPrime && (phone.value).length===10){
        submitButton.removeAttribute('disabled')
    }else{
        submitButton.setAttribute('disabled', true)
    }
})

//listen for TapPay Field
phone.addEventListener("keyup", function(){
    const tappayStatus=TPDirect.card.getTappayFieldsStatus()
    if(tappayStatus.canGetPrime===true && (phone.value).length===10){
        submitButton.removeAttribute('disabled')
    }else{
        submitButton.setAttribute('disabled', true)
    }
})
inputEmail.addEventListener("keyup", function(){
    const tappayStatus=TPDirect.card.getTappayFieldsStatus()
    if(tappayStatus.canGetPrime===true && phoneRegex.test(phone.value) && emailRegex.test(inputEmail.value) && inputName.value){
        submitButton.removeAttribute('disabled')
    }else{
        submitButton.setAttribute('disabled', true)
    }
    if(emailRegex.test(inputEmail.value)){
        inputEmail.style.color="green"
    }else{
        inputEmail.style.color="orange"
    }
})
inputName.addEventListener("keyup", function(){
    const tapPayStatus=TPDirect.card.getTappayFieldsStatus()
    if(tapPayStatus.canGetPrime===true && phoneRegex.test(phone.value) && emailRegex.test(inputEmail.value) && inputName.value){
        submitButton.removeAttribute('disabled')
    }else{
        submitButton.setAttribute('disabled', true)
    }
})

submitButton.addEventListener('click', onSubmit);
function onSubmit(event){
    event.preventDefault()
    //取得tappay fields的status
    TPDirect.card.getPrime((result)=>{
        if(result.status!==0){
            console.log(result.msg);
            return
        }
        let cardUserInfo=document.querySelectorAll("label>input");
        let [name, email, phone_number]=cardUserInfo;
        let {price, ...trip}=order;
        let data={
            "prime": result.card.prime,
            "order":{
                "price": price, trip,
                "contact": {
                    "name": name.value,
                    "email": email.value,
                    "phone": phone_number.value
                }
            }
        }
        fetch("/api/orders", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }).then((res)=>res.json())
        .then((data)=>{
            let payData=data.data;
            let orderNum=payData.number;
            console.log(orderNum)
            if(data["data"]){
                location.href=`/thankyou?number=${orderNum}`;
            }else{
                console.log(result)
            }
        }).catch((error)=>{
            return error;
        })
    })
}