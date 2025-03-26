// 为手机、身份证、姓名输入框绑定 blur 事件进行即时校验
// 手机号码校验：必须为 11 位数字
document.addEventListener("DOMContentLoaded", function() {
    ["customer_phone"].forEach(function(id) {
        const phoneElement = document.getElementById(id);
        console.log('检测到:', id, phoneElement);
        if (phoneElement) {
            phoneElement.addEventListener('blur', function() {
                validateField(this, /^[0-9]{11}$/, '请输入有效的手机号码');
            });
        }
    });
});

// 身份证号校验：15位、18位或17位+X/x
document.addEventListener("DOMContentLoaded", function() {
    ["customer_IDcard"].forEach(function(id) {
        const idcardElement = document.getElementById(id);
        if (idcardElement) {  // 防止 id 不存在时出错
            idcardElement.addEventListener('blur', function() {
                validateField(this, /^(?:\d{15}|\d{18}|\d{17}[Xx])$/, '请输入有效的身份证号码');
            });
        }
    });
});

// 订单人姓名实时校验（blur 事件）
document.addEventListener("DOMContentLoaded", function() {
    const nameElement = document.getElementById("customer_name");

    if (nameElement) {
        nameElement.addEventListener('blur', function() {
            const value = this.value.trim();
            if (value === '') {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
                let errorElement = this.nextElementSibling;
                if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
                    errorElement = document.createElement('div');
                    errorElement.className = 'invalid-feedback';
                    this.parentNode.insertBefore(errorElement, this.nextSibling);
                }
                errorElement.textContent = '姓名不能为空';
            } else {
                this.classList.remove('is-invalid');
                let errorElement = this.nextElementSibling;
                if (errorElement && errorElement.classList.contains('invalid-feedback')) {
                    errorElement.textContent = '';
                }
            }
        });
    }
});



/**
 * 在表单提交前统一校验所有输入项
 * @returns {Boolean} - 如果所有字段校验通过则返回 true，否则返回 false
 */
function validateBookForm() {
    const phoneValid = validateField(
        document.getElementById("customer_phone"),
        /^[0-9]{11}$/,
        '请输入有效的手机号码'
    );
    const idCardValid = validateField(
        document.getElementById("customer_IDcard"),
        /^(?:\d{15}|\d{18}|\d{17}[Xx])$/,
        '请输入有效的身份证号码'
    );
    const nameValid = document.getElementById("customer_name").value.trim() !== '';
    if (!nameValid) {
        document.getElementById("customer_name").classList.remove('is-valid');
        document.getElementById("customer_name").classList.add('is-invalid');
        let errorElement = document.getElementById("customer_name").nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            document.getElementById("customer_name").parentNode.insertBefore(errorElement, document.getElementById("customer_name").nextSibling);
        }
        errorElement.textContent = '姓名不能为空';
    }
    return phoneValid && idCardValid && nameValid;
}




// 预订表单提交
function submitBookEdit() {
    const form = document.getElementById("bookForm");

    // 先运行浏览器原生HTML5校验
    if (!form.checkValidity()) {
        form.reportValidity();  // 弹出浏览器的校验提示（如：请选择支付渠道）
        return;
    }

    // 再运行自定义的校验逻辑（如手机号正则、身份证等）
    if (!validateBookForm()) {
        alert("请检查输入是否正确！");
        return;
    }

    // 如果都通过，提交
    form.submit();
}




// 入住者身份证校验
document.addEventListener("DOMContentLoaded", function() {
    // 监听所有入住人身份证框 blur 事件（动态绑定）
    document.getElementById("occupant-info").addEventListener('blur', function (e) {
        if (e.target && e.target.name === "occupant_id_card[]") {
            validateField(e.target, /^(?:\d{15}|\d{18}|\d{17}[Xx])$/, '请输入有效的身份证号码');
        }
    }, true);  // 捕获阶段，保证动态加的也能触发
});


// 入住表单提交
function submitCheckInEdit() {
    const form = document.getElementById("bookForm");
    if (!form.checkValidity()) {
        form.reportValidity();  // 弹出浏览器的校验提示（如：请选择支付渠道）
        return;
    }
    if (!validateCheckInForm()) {
        return;
    }
    form.submit();
}


// 入住表单校验
function validateCheckInForm() {
    let valid = true;
    let occupants = document.querySelectorAll(".occupant-entry");

    // 第一层：入住人数量检测
    if (occupants.length === 0) {
        alert("请至少添加一位入住人！");
        return false;
    }

    // 第二层：循环校验
    occupants.forEach(function (entry) {
        const nameInput = entry.querySelector('input[name="occupant_name[]"]');
        const idInput = entry.querySelector('input[name="occupant_id_card[]"]');

        // 姓名校验
        if (!nameInput.value.trim()) {
            nameInput.classList.add('is-invalid');
            let nameError = nameInput.nextElementSibling;
            if (!nameError || !nameError.classList.contains('invalid-feedback')) {
                nameError = document.createElement('div');
                nameError.className = 'invalid-feedback';
                nameInput.parentNode.insertBefore(nameError, nameInput.nextSibling);
            }
            nameError.textContent = '姓名不能为空';
            valid = false;
        } else {
            nameInput.classList.remove('is-invalid');
            let nameError = nameInput.nextElementSibling;
            if (nameError && nameError.classList.contains('invalid-feedback')) {
                nameError.textContent = '';
            }
        }

        // 身份证校验
        const idReg = /^(?:\d{15}|\d{18}|\d{17}[Xx])$/;
        if (!idReg.test(idInput.value.trim())) {
            idInput.classList.add('is-invalid');
            let idError = idInput.nextElementSibling;
            if (!idError || !idError.classList.contains('invalid-feedback')) {
                idError = document.createElement('div');
                idError.className = 'invalid-feedback';
                idInput.parentNode.insertBefore(idError, idInput.nextSibling);
            }
            idError.textContent = '身份证格式不正确';
            valid = false;
        } else {
            idInput.classList.remove('is-invalid');
            let idError = idInput.nextElementSibling;
            if (idError && idError.classList.contains('invalid-feedback')) {
                idError.textContent = '';
            }
        }
    });

    // 只在全部校验完后，统一弹出一次
    if (!valid) {
        alert("请检查入住人信息，姓名不能为空且身份证格式正确！");
    }

    return valid;
}



// 动态入住人姓名校验（事件委托）
// 实时校验入住人姓名
document.addEventListener("DOMContentLoaded", function() {
    const occupantArea = document.getElementById("occupant-info");
    console.log('入住人区域绑定:', occupantArea);
    if (occupantArea) {
        occupantArea.addEventListener('blur', function (e) {
            console.log('监听到入住人blur', e.target);
            if (e.target && e.target.name === "occupant_name[]") {
                const value = e.target.value.trim();
                if (value === '') {
                    e.target.classList.add('is-invalid');
                    let nameError = e.target.nextElementSibling;
                    if (!nameError || !nameError.classList.contains('invalid-feedback')) {
                        nameError = document.createElement('div');
                        nameError.className = 'invalid-feedback';
                        e.target.parentNode.insertBefore(nameError, e.target.nextSibling);
                    }
                    nameError.textContent = '姓名不能为空';
                } else {
                    e.target.classList.remove('is-invalid');
                    let nameError = e.target.nextElementSibling;
                    if (nameError && nameError.classList.contains('invalid-feedback')) {
                        nameError.textContent = '';
                    }
                }
            }
        }, true);  // 必须加true
    }
});
