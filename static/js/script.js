<!-- 初始化 Toast 提示框自动消失和关闭 -->
document.addEventListener("DOMContentLoaded", function () {
    let toasts = document.querySelectorAll(".self-toast");
    toasts.forEach(function (toast) {
        setTimeout(function () {
            toast.classList.add("fade-out");
            setTimeout(function () {
                toast.style.display = "none";
            }, 500);
        }, 5000);
        let closeBtn = toast.querySelector(".self-close-btn");
        closeBtn.addEventListener("click", function () {
            toast.classList.add("fade-out");
            setTimeout(function () {
                toast.style.display = "none";
            }, 500); // 持续 5秒
        });
    });
});


// 密码可视 切换指定 input[type=password] 的可见性
function togglePasswordVisibility(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);

    // 如果当前是密码则改为明文，并把图标改为fa-eye-slash
    if (input.type === "password") {
          input.type = "text";
          icon.classList.remove("fa-eye");
          icon.classList.add("fa-eye-slash");
    } else {
      // 否则改为密码，并把图标改回fa-eye
      input.type = "password";
      icon.classList.remove("fa-eye-slash");
      icon.classList.add("fa-eye");
    }
}





// 打开编辑资料的 Modal 弹窗
function openProfileModal() {
    // 获取 Modal 元素并初始化 bootstrap Modal 实例
    const profileModal = new bootstrap.Modal(document.getElementById("profileModal"));
    // 显示弹窗
    profileModal.show();
}

/**
 * 通用校验函数：验证输入框内容并显示错误提示
 * @param {HTMLElement} field - 需要校验的输入框元素
 * @param {RegExp} regex - 用于验证的正则表达式
 * @param {String} errorMsg - 校验失败时显示的错误信息
 * @returns {Boolean} - 校验通过返回 true，否则返回 false
 */
function validateField(field, regex, errorMsg) {
    // 如果输入框的值不匹配正则表达式
    if (!regex.test(field.value)) {
        // 移除可能存在的成功样式，添加错误样式
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        // 获取该输入框下方的错误提示元素
        let errorElement = field.nextElementSibling;
        // 如果没有找到错误提示元素，则创建一个新的错误提示元素
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback'; // 设置错误提示的样式
            // 将错误提示插入到输入框的下方
            field.parentNode.insertBefore(errorElement, field.nextSibling);
        }
        // 设置错误提示内容
        errorElement.textContent = errorMsg;
        return false;  // 返回 false，表示校验未通过
    } else {
        // 如果输入框的值符合正则表达式，清除错误样式和提示，不再添加成功样式
        field.classList.remove('is-invalid');
        let errorElement = field.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.textContent = ''; // 清空错误提示
        }
        return true;  // 返回 true，表示校验通过
    }
}

// 为手机、身份证、姓名输入框绑定 blur 事件进行即时校验
// 手机号码校验：必须为 11 位数字
["employee_phone", "employee_phone_edit"].forEach(function(id) {
    const phoneElement = document.getElementById(id);
    if (phoneElement) {  // 防止 id 不存在时出错
        phoneElement.addEventListener('blur', function() {
            validateField(this, /^[0-9]{11}$/, '请输入有效的手机号码');
        });
    }
});

// 身份证号校验：15位、18位或17位+X/x
["employee_IDcard", "employee_IDcard_edit", "customer_IDcard"].forEach(function(id) {
    const idcardElement = document.getElementById(id);
    if (idcardElement) {  // 防止 id 不存在时出错
        idcardElement.addEventListener('blur', function() {
            validateField(this, /^(?:\d{15}|\d{18}|\d{17}[Xx])$/, '请输入有效的身份证号码');
        });
    }
});

// 校验：不允许为空
["employee_name_edit", "employee_name","employee_id_edit"].forEach(function(id) {
    const element = document.getElementById(id);
    if (element) {  // 防止 id 不存在时出错
        element.addEventListener('blur', function() {
            // 校验是否为空
            if (element.value.trim() === '') {
                element.classList.remove('is-valid'); // 移除可能存在的成功样式
                element.classList.add('is-invalid');  // 添加错误样式

                // 获取该输入框下方的错误提示元素
                let errorElement = element.nextElementSibling;

                // 如果没有找到错误提示元素，创建一个新的错误提示元素
                if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
                    errorElement = document.createElement('div');
                    errorElement.className = 'invalid-feedback'; // 设置错误提示样式
                    // 将错误提示元素插入到输入框下方
                    element.parentNode.insertBefore(errorElement, element.nextSibling);
                }

                // 设置错误提示文本
                errorElement.textContent = '输入不能为空';
            } else {
                // 清除错误样式和提示文本
                element.classList.remove('is-invalid');
                let errorElement = element.nextElementSibling;
                if (errorElement && errorElement.classList.contains('invalid-feedback')) {
                    errorElement.textContent = ''; // 清空错误提示文本
                }
            }
        });
    }
});


/**
 * 在表单提交前统一校验所有输入项
 * @returns {Boolean} - 如果所有字段校验通过则返回 true，否则返回 false
 */
function validateProfileForm() {
    const phoneValid = validateField(
        document.getElementById("employee_phone"),
        /^[0-9]{11}$/,
        '请输入有效的手机号码'
    );
    const idCardValid = validateField(
        document.getElementById("employee_IDcard"),
        /^(?:\d{15}|\d{18}|\d{17}[Xx])$/,
        '请输入有效的身份证号码'
    );
    const nameValid = document.getElementById("employee_name").value.trim() !== '';
    if (!nameValid) {
        document.getElementById("employee_name").classList.remove('is-valid');
        document.getElementById("employee_name").classList.add('is-invalid');
        let errorElement = document.getElementById("employee_name").nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            document.getElementById("employee_name").parentNode.insertBefore(errorElement, document.getElementById("employee_name").nextSibling);
        }
        errorElement.textContent = '姓名不能为空';
    }
    return phoneValid && idCardValid && nameValid;
}

/**
 * 保存用户资料
 * 如果校验通过，则提交表单，采用 Django 后端传统处理方式（页面刷新或重定向）
 */
function submitProfile() {
    if (!validateProfileForm()) {
        alert("请检查输入是否正确！");
        return;
    }
    document.getElementById("profileForm").submit();
}

// 修改密码弹窗
function openPasswordModal() {
    const passwordModal = new bootstrap.Modal(document.getElementById("passwordModal"));
    passwordModal.show();
}

// 旧密码校验：不能为空
document.getElementById("old_password").addEventListener('blur', function(){
    if (this.value.trim() === '') {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        let errorElement = this.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            this.parentNode.insertBefore(errorElement, this.nextSibling);
        }
        errorElement.textContent = '旧密码不能为空';
    } else {
        this.classList.remove('is-invalid');
        let errorElement = this.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.textContent = '';
        }
    }
});

// 新密码校验：不能为空且格式需要符合要求
document.getElementById("new_password").addEventListener('blur', function(){
    if (this.value.trim() === '') {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        let errorElement = this.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            this.parentNode.insertBefore(errorElement, this.nextSibling);
        }
        errorElement.textContent = '新密码不能为空';
    } else {
        this.classList.remove('is-invalid');
        let errorElement = this.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.textContent = '';
        }

        // 进行正则校验：密码至少8位，且需包含大小写字母和数字
        validateField(
            this,
            /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$/,
            '密码至少8位，且需包含大小写字母和数字'
        );
    }
});

// 确认密码校验：不能为空且必须与新密码一致
document.getElementById("confirm_password").addEventListener('blur', function(){
    if (this.value.trim() === '') {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        let errorElement = this.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            this.parentNode.insertBefore(errorElement, this.nextSibling);
        }
        errorElement.textContent = '确认密码不能为空';
    } else {
        this.classList.remove('is-invalid');
        let errorElement = this.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.textContent = '';
        }

        // 校验两次输入的新密码是否一致
        const newPassword = document.getElementById("new_password").value;
        if (this.value !== newPassword) {
            this.classList.remove('is-valid');
            this.classList.add('is-invalid');
            if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
                errorElement = document.createElement('div');
                errorElement.className = 'invalid-feedback';
                this.parentNode.insertBefore(errorElement, this.nextSibling);
            }
            errorElement.textContent = '两次输入的密码不一致';
        }

        // 正则校验密码格式
        validateField(
            this,
            /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$/,
            '密码至少8位，且需包含大小写字母和数字'
        );
    }
});

// 密码提交
function submitPasswordEdit() {
    if (!validatePasswordForm()) {
        alert("请检查输入是否正确！");
        return;
    }
    document.getElementById("passwordForm").submit();
}

/**
 * 在表单提交前统一校验所有输入项
 * @returns {Boolean} - 如果所有字段校验通过则返回 true，否则返回 false
 */
function validatePasswordForm() {
    const old_passwordValid = validateField(
        document.getElementById("old_password"),
        /^(?!\s*$).+/,  // 这个正则表达式表示输入框不能为空
        '旧密码不能为空'
    );

    const new_passwordValid = validateField(
        document.getElementById("new_password"),
        /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$/,
        '密码至少8位，且需包含大小写字母和数字'
    );
    const confirm_passwordValid = validateField(
        document.getElementById("confirm_password"),
        /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$/,
        '密码至少8位，且需包含大小写字母和数字'
    );

    const equal = document.getElementById("new_password").value === document.getElementById("confirm_password").value;

    // 如果两次密码不一致，则给确认密码框添加错误提示
    if (!equal) {
        const confirmPasswordElement = document.getElementById("confirm_password");
        confirmPasswordElement.classList.remove('is-valid');
        confirmPasswordElement.classList.add('is-invalid');
        let errorElement = confirmPasswordElement.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            confirmPasswordElement.parentNode.insertBefore(errorElement, confirmPasswordElement.nextSibling);
        }
        errorElement.textContent = '两次输入的密码不一致';
    }

    return old_passwordValid && new_passwordValid && confirm_passwordValid && equal;
}


// 在文档加载完成后，给 Modal 绑定事件监听
document.addEventListener('DOMContentLoaded', function () {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('hidden.bs.modal', function () {
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
                const inputs = form.querySelectorAll('input');
                inputs.forEach(function(input) {
                    // 重置时移除所有校验相关的样式
                    input.classList.remove('is-valid', 'is-invalid');
                    const errorElement = input.nextElementSibling;
                    if (errorElement && errorElement.classList.contains('invalid-feedback')) {
                        errorElement.textContent = '';
                    }
                });
            }
        });
    });
});





