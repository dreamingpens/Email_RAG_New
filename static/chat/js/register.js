document.getElementById("loginForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const email = document.getElementById("floatingEmail").value;
  const password = document.getElementById("floatingPassword").value;
  const name = document.getElementById("floatingName").value;
  const errorMessage = document.getElementById("errorMessage");
  // 이메일 도메인 검증
  if (!email.endsWith("@kaist.ac.kr")) {
    errorMessage.textContent = "Only @kaist.ac.kr email addresses are allowed.";
    errorMessage.classList.remove("d-none");
    return;
  }

  // POST 요청 보내기
  fetch("/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, name, password }),
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((errorData) => {
          if (
            response.status === 400 &&
            errorData.detail === "Email already registered"
          ) {
            throw new Error("This email is already registered.");
          } else {
            throw new Error("Registration failed");
          }
        });
      }
      return response.json();
    })
    .then((data) => {
      // 로그인 성공 처리
      console.log("Login successful", data);
      window.location.href = "/";
      // 여기에 로그인 성공 후 처리 로직 추가 (예: 리다이렉트)
    })
    .catch((error) => {
      console.error("Error:", error);
      if (error.message === "This email is already registered.") {
        errorMessage.textContent = "This email is already registered.";
      } else {
        errorMessage.textContent = "Registration failed. Please try again.";
      }
      errorMessage.classList.remove("d-none");
    });
});
