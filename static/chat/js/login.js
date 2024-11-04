document
  .getElementById("loginForm")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // 폼 제출 방지

    const email = document.getElementById("floatingEmail").value;
    const password = document.getElementById("floatingPassword").value;
    const errorMessage = document.getElementById("errorMessage");

    fetch("/auth/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.access_token) {
          // 토큰을 localStorage에 저장
          console.log("Login successful", data);
          localStorage.setItem("access_token", data.access_token);
          window.location.href = "/test"; // 로그인 성공 시 리디렉션
        } else {
          errorMessage.classList.remove("d-none");
          errorMessage.textContent =
            "로그인에 실패했습니다. 이메일 또는 비밀번호를 확인해주세요.";
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        errorMessage.classList.remove("d-none");
        errorMessage.textContent = "서버와의 연결에 문제가 발생했습니다.";
      });
  });
