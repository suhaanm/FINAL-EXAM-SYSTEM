function onBlur() {
  old = document.getElementById("focuscheck").value;
	document.getElementById('focuscheck').value = parseInt(old, 10) + 1;

	window.createNotification({
		closeOnClick: true,
		displayCloseButton: true,
		positionClass: 'nfc-top-right',
		showDuration: 20000,
		theme: "error"
	})({
		title: "Lost Focus",
		message: "Your exam just lost focus!"
	});
};
function onFocus(){
	document.body.className = 'focused';
};

if (/*@cc_on!@*/false) { // check for Internet Explorer
	document.onfocusin = onFocus;
	document.onfocusout = onBlur;
} else {
	window.onfocus = onFocus;
	window.onblur = onBlur;
}

function disableClick(){ 
  document.onclick=function(event){ 
  if (event.button == 2) { 
    alert('false'); 
    return false; 
  } 
} 
} 

window.addEventListener('online', () => document.getElementById("netstatus").innerHTML = "online");
window.addEventListener('offline', () => document.getElementById("netstatus").innerHTML = "offline");

window.addEventListener('online',function() {
  document.getElementById("netstatus").innerHTML = "online";
});

window.addEventListener('offline',function() {
  document.getElementById("netstatus").innerHTML = "offline";
});

window.addEventListener('offline', () => {
    //document.getElementById('submitbutton').style.visibility = 'hidden';
		window.createNotification({
			closeOnClick: true,
			displayCloseButton: true,
			positionClass: 'nfc-top-right',
			showDuration: 12000,
			theme: "warning"
		})({
			title: "Offline",
			message: "You've just become offline! The test might not submit successfully if you are offline at the time of submission."
		});
});

window.addEventListener('online', () => {
    //document.getElementById('submitbutton').style.visibility = 'visible';
		window.createNotification({
			closeOnClick: true,
			displayCloseButton: true,
			positionClass: 'nfc-top-right',
			showDuration: 10000,
			theme: "success"
		})({
			title: "Online",
			message: "You're back online! Everything will be functional!"
		});
});