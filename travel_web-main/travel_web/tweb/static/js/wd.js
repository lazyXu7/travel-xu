function formsubmit() {
  const username = document.getElementById('input_username').value;
  const pwd = document.getElementById('input_password').value;
  const pwd2 = document.getElementById('input_password2').value;
  if (username == '' || pwd == '' || pwd2 == '') {
    alert('请输入完整的信息');
    return;
  }
  if (pwd != pwd2) {
    alert('两次密码不一致，请重新输入');
    return;
  }
  if (pwd.length < 6 || pwd.length > 16) {
    alert('密码需要在6-16位之间');
    return;
  }
  if (username.length < 2 || username.length > 20) {
    alert('用户名需要在2-20位之间');
    return;
  }
  fetch('/signup/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username: username, password: pwd })
  }).then(response => response.json())
    .then(data => {
      if (data.message == 1) {
        alert('注册成功');
        window.location.href = "/login/";
      }
      if (data.message == 2) {
        alert('服务器异常，请刷新页面后重试');
      }
      if (data.message == 3) {
        alert('注册失败');
      }
      if (data.message == 4) {
        alert('用户名已存在')
      }
    })
}

$("#formsubmit").click(function (e) {
  console.log("sub");
  formsubmit();
})
