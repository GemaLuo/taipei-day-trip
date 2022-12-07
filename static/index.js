//設定全域變數isLoading追蹤、記錄頁面是否正載入API
let isLoading=false;
const category_list=document.querySelector(".category-list");
const input=document.querySelector("input");
const body=document.querySelector("body");
const main_content=document.querySelector(".main-content");
//categories選項
fetch("http://44.229.57.144:3000/api/categories").then(function(res){
    return res.json();
}).then(function(data){
    const categories=data.data
    category_list.addEventListener("click", touchCat)
    for(let i=0; i<categories.length; i++){
        ///api/categories有replace()移除空白
        if (categories[i]=="其他"){
            categories[i]="其　　他"
        }
        let category_items=document.createElement("div")
        category_items.className="category-items"
        category_items.textContent=categories[i]
        category_list.appendChild(category_items)
    }
});
//點searchBar
function touchCat(e){
    input.value=e.target.textContent
    input.style.color="black"
}

input.addEventListener("click", touchInput)
function touchInput(e){
    //阻止事件冒泡
    e.stopPropagation()
    let category_list=document.querySelector(".category-list")
    category_list.style.display="grid"
}

//點searchBar以外body區域以隱藏分類清單
body.addEventListener("click", touchBlank)
function touchBlank(e){
    let category_list=document.querySelector(".category-list")
    category_list.style.display="none"
}

//搜尋keyword
let page=0 //因無限載入後page不為0
search=function(){
    //停止對loadingObserver的監聽
    observer.unobserve(loadingObserver)
    let inputBar=document.querySelector("#inputBar").value;
    //清除原本景點內容，在nextPage()即可新增資料在景點區域
    main_content.innerHTML="";
    let data=[]
    page=0 
    fetch("http://44.229.57.144:3000/api/attractions?page="+page+"&keyword="+inputBar).then(function(response){
        return response.json();
    }).then(function(allData){
        data=allData.data;
        if(data && data.length){
            page=0
            observer.observe(loadingObserver);
        }else{
            let nothing=document.createElement("div");
            nothing.textContent="查無此結果，請輸入分類名稱。"
            nothing.className="nothing"
            main_content.appendChild(nothing);
        }
    })    
}
//設定觀察目標:footer
const loadingObserver=document.querySelector(".footer");

//主內容
const getData=function(){
    let inputBar=document.querySelector("#inputBar").value;
    fetch("http://44.229.57.144:3000/api/attractions?page="+page+"&keyword="+inputBar).then(function(response){
        return response.json();
    }).then(function(allData){
        let data=allData.data;
        for (let i=0; i<data.length; i++){
            item=data[i].images
            let main_item=document.createElement("a");
            let img_name=document.createElement("div");
            let img_nametxt=document.createElement("div");
            main_item.className="main-item";
            main_item.href="/attraction/"+parseInt(data[i].id)
            main_item.id="pic"+((page)*12+i);
            main_content.appendChild(main_item);
            let main_item_id=document.querySelector("#pic"+((page)*12+i));
            let img=document.createElement('img');
            img.src=item[0];
            main_item_id.appendChild(img);
            img_nametxt.textContent=data[i].name
            img_name.className="img-name";
            img_nametxt.className="img-nametxt";
            main_item_id.appendChild(img_name)
            img_name.appendChild(img_nametxt)
            //資訊欄
            let main_info=document.createElement("div");
            main_info.className="main-info";
            main_info.id="main-info"+((page)*12+i);
            main_item_id.appendChild(main_info);

            let main_info_txt=document.querySelector("#main-info"+((page)*12+i));
            let txt1=document.createElement("div");
            let txt2=document.createElement("div");
            txt1.className="main-infotxt";
            txt2.className="main-infotxt";
            txt1.textContent=data[i].mrt;
            txt2.textContent=data[i].category;
            main_info_txt.appendChild(txt1);
            main_info_txt.appendChild(txt2);
        }
        isLoading=false;
        page=allData.nextPage;
    })
};
//scroll event
//rootMargin:移到目標的相對位置，距離目標還有150px時才會觸發事件
//threshold:設定目標進入可見範圍多少百分比後會觸發事件
const option={
    rootMargin: '0px 0px 150px 0px',
    threshold: 0.5
}
//目標target進入/離開觀察器root的可見範圍會做的事
//執行callback
const callback=([entry])=>{
    if(entry && entry.isIntersecting && page!=null && !isLoading){
        isLoading=true
        getData()
    }
}
//建立觀察器，設定偵測捲動目標是否進入可見範圍的容器(觀察器)
let observer=new IntersectionObserver(callback, option)
//告訴observer要觀察哪個目標元素
observer.observe(loadingObserver);

