document.querySelectorAll("iframe").forEach(iframe=>{
    // iframe.addEventListener("load",e=>{
    //     console.log("load")
    //     console.log(iframe.contentDocument.documentElement.querySelector("img"))
    //     try {
    //         iframe.contentDocument.documentElement.querySelector("img").style.height="95%"
    //     } catch (error) {
    //         console.log("verga")
    //     }
    // })
    // console.log(iframe.contentDocument)
    // console.log(iframe.contentDocument.querySelector("head"))
    iframe.contentDocument.querySelector("head").addEventListener("load",e=>{
        console.error("iframe")
        console.log(iframe.contentDocument.querySelector("head").innerHTML)
        iframe.contentDocument.querySelector("head").innerHTML+='<link rel="stylesheet" href="../static/styles/iframe.css">'
    })
})