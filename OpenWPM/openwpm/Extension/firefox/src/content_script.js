console.log('content script loaded')
document.body.style.border = "5px solid red";

window.addEventListener("message", function (event) {
    console.log(`content script works! It received ${event} and ${event.data}`)
    if (event.data &&
        (event.data.message == 'triggered_func' ||
            event.data.message == 'about-to-button-click' ||
            event.data.message == 'finish-button-click' ||
            event.data.message == 'clear_triggered_func_data' ||
            event.data.message == "send_triggered_func_data" ||
            event.data.message == 'send_used_string')) {
        browser.runtime.sendMessage(event.data)
    }
});