document.querySelectorAll('meta[class="metaError"]').forEach(error=>{
    alert(error.getAttribute("content"))
})