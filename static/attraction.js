let path=window.location.pathname;
let attractionId=path.split('/')[2];
let data=document.getElementById("main-img");

function loader(){
    document.getElementById("loading").style.display="none";
}

function connectAttraction(url){
    url="/api/attraction/"+attractionId;
    fetch(url, {
        method:'GET',
    })
    .then((Res)=>Res.json())
    .then((Res)=>{
        loader();
        getData(Res);
        showImg(indexValue);
    })
   
}
connectAttraction();

function getData(Res){
    let myResult=Res.data;
    let imgData=myResult["images"];
    let titleData=myResult["name"];
    let categoryData=myResult["category"];
    let mrtData=myResult["mrt"];
    let descriptionData=myResult["description"];
    let addressData=myResult["address"];
    let transportData=myResult["transport"];

    let name=document.getElementById("main-name");
    name.textContent=titleData;
    let category=document.getElementById("category");
    category.textContent=categoryData+" at "+mrtData;
    let description=document.getElementById("description");
    description.textContent=descriptionData;
    let address=document.getElementById("address");
    address.textContent=addressData;
    let transport=document.getElementById("transportation");
    transport.textContent=transportData;

    for (let i=0; i<imgData.length; i++){
        let imgLink=imgData[i];
        let listContainer=document.getElementById("images");
        let imgContainer=document.createElement("li");
        let img=document.createElement("img");
        img.src=imgLink;
        let dots=document.createElement("p");
        let dotsList=document.getElementById("dots");
        dots.className="dots";
        let j=i+1;
        let target='slider('+j+')';
        dots.setAttribute("onclick", target);

        imgContainer.appendChild(img);
        listContainer.appendChild(imgContainer);
        data.appendChild(listContainer);
        dotsList.appendChild(dots);
    }
}

//image slider
let indexValue=1;
function slider(e){
    showImg((indexValue=e));
}
function img_slide(e){
    showImg((indexValue+=e));
}
function showImg(e){
    let i;
    let img=document.querySelectorAll("img");
    let dots=document.querySelectorAll(".dots");
    if(e>img.length){
        indexValue=1;
    }
    if(e<1){
        indexValue=img.length;
    }
    for(i=0; i<img.length; i++){
        img[i].style.display="none";
    }
    img[indexValue-1].style.display="block";
    for(i=0;i<dots.length; i++){
        dots[i].style="background:white; width: 12px; height: 12px;";
    }
    dots[indexValue-1].style="background: black; border: 1px solid #FFFFFF; width: 12px; height: 12px;";
}

//日期不得為明日之前
let today=new Date().toISOString().split("T")[0];
document.getElementsByName("date")[0].setAttribute("min",today);

//價目表選項按鍵
function changePrice(){
    let evening=document.getElementById("evening");
    let context=document.getElementById("price_ntd");
    if (evening.checked==true){
        context.innerHTML="新台幣 2500 元";
    }else{
        context.innerHTML="新台幣 2000 元";
    }
}
