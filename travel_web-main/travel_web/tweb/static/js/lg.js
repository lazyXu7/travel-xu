// 登录函数
document.getElementById('login').onclick = function() {
  var username = document.getElementById('input_username').value;
  var pwd = document.getElementById('input_password').value;

  if (username == '' || pwd == '') {
    alert("请输入完整的登录信息");
    return;
  }

  if (pwd.length < 6 || pwd.length > 16) {
    alert('密码需要在6-16位之间');
    return;
  }

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/login/', true);
  xhr.setRequestHeader('Content-Type', 'application/json');

  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      if (xhr.status == 200) {
        try {
          var data = JSON.parse(xhr.responseText);
          if (data.message == '1') {
            window.location.href = '/';
          } else if (data.message == '3') {
            alert('密码错误');
          } else {
            alert('登录失败');
          }
        } catch (e) {
          alert('响应解析错误');
        }
      } else {
        alert('请求失败: ' + xhr.status);
      }
    }
  };

  xhr.send(JSON.stringify({ username: username, password: pwd }));
};
