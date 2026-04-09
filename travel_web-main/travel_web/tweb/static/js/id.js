var imageArray = [
  "https://youimg1.c-ctrip.com/target/0106m120004eks4oyF624_C_1180_462.jpg",
  "https://youimg1.c-ctrip.com/target/0103l1200080zklhd01B9_C_1180_462.jpg"
];

// 登出函数
function logout() {
  localStorage.removeItem("username");
  localStorage.removeItem("pwd");
  window.location.href = "/login/";
}

// 搜索函数
function search() {
  var input = document.getElementById('input_city').value;
  if (input == '') {
    alert('请输入需要查找的城市');
    return;
  }
  window.location.href = '/city/?city=' + encodeURIComponent(input);
}

// 图片预加载
function preloadImages() {
  for (var i = 0; i < imageArray.length; i++) {
    var img = new Image();
    img.src = imageArray[i];
  }
}
preloadImages();

// 绑定事件
document.addEventListener('DOMContentLoaded', function() {
  var logoutBtn = document.getElementById('logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
  
  var searchBtn = document.getElementById('search');
  if (searchBtn) {
    searchBtn.addEventListener('click', search);
  }
  
  // 背景轮播
  var background = document.getElementById("background");
  if (background) {
    background.style.backgroundImage = "url(" + imageArray[0] + ")";
    
    var index = 0;
    setInterval(function () {
      index = (index + 1) % imageArray.length;
      var imageUrl = "url(" + imageArray[index] + ")";
      fadeToImage(imageUrl, background);
    }, 8000);
  }
});

function fadeToImage(imageUrl, background) {
  var tempBackground = document.createElement("div");
  tempBackground.style.backgroundImage = imageUrl;
  tempBackground.style.opacity = 0;
  tempBackground.className = "temp-background";
  background.appendChild(tempBackground);

  setTimeout(function () {
    tempBackground.style.opacity = 1;
    background.style.backgroundImage = imageUrl;
  }, 1000);

  setTimeout(function () {
    var oldBackground = document.getElementsByClassName("temp-background")[0];
    if (oldBackground && oldBackground.parentNode) {
      background.removeChild(oldBackground);
    }
  }, 1000);
}
