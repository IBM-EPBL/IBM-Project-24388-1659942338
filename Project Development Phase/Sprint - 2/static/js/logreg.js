var hamburger = document.querySelector(".hamburger");

hamburger.addEventListener("click", function(){
  	document.querySelector("body").classList.toggle("active");
})

document.getElementById('Update').onclick = function() {
    document.getElementById('description').removeAttribute('readonly');
    document.getElementById('name').removeAttribute('readonly');
    document.getElementById('uname').removeAttribute('readonly');
    document.getElementById('email').removeAttribute('readonly');
    document.getElementById('dob').removeAttribute('readonly');
    document.getElementById('age').removeAttribute('readonly');
    document.getElementById('phone').removeAttribute('readonly');
    document.getElementById('city').removeAttribute('readonly');
    document.getElementById('state').removeAttribute('readonly');
    document.getElementById('country').removeAttribute('readonly');
    document.getElementById('bloodtype').removeAttribute("disabled");
    document.getElementById('avail').removeAttribute("disabled");
};