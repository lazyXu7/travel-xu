// 城市页面登录状态检查
(function() {
  const username = localStorage.getItem('username');
  const pwd = localStorage.getItem('pwd');
  
  if (!username || !pwd) {
    alert("请先登录");
    window.location.href = '/login/';
    return;
  }
  
  // 可选：验证登录状态
  fetch('/index/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username: username, password: pwd })
  }).then(response => response.text())
    .then(data => {
      try {
        const jsonData = JSON.parse(data);
        if (jsonData.message != 1) {
          alert("登录已过期，请重新登录");
          localStorage.removeItem("username");
          localStorage.removeItem("pwd");
          window.location.href = '/login/';
        }
      } catch (e) {
        // 忽略解析错误
      }
    })
    .catch(error => {
      // 忽略网络错误
    });
})();
