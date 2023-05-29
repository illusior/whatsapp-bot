window.addEventListener('load', (_) => {
    const tabs = document.querySelectorAll('.tabs__tab');
    const formContent = document.querySelectorAll('.form--content')

    tabs.forEach((tab, index) => {
        tab.addEventListener('click', (_) => {
            tabs.forEach(tab => {
                tab.classList.remove('tabs__tab--active')
            })

            tab.classList.add('tabs__tab--active')
            formContent.forEach(menu => {
                menu.style.display = 'none'
            })

            formContent[index].style.display = ''
        })
    });
})

window.addEventListener('load', (_) => {
    const inputs = document.querySelectorAll('.input')
    const submitButton = document.getElementById('submit-btn')

    let anyInputFilled = false
    inputs.forEach((input, _) => {
        input.addEventListener('input', (e) => {
            anyInputFilled = input.value !== ''

            submitButton.disabled = !anyInputFilled
            if (anyInputFilled) {
                submitButton.classList.remove('button--disabled')
                submitButton.classList.add('button--filled')
            }
            else {
                submitButton.classList.remove('button--filled')
                submitButton.classList.add('button--disabled')
            }
        })
    })
})


window.addEventListener('load', (_) => {
    const modalCloseBtn = document.querySelector('.modal__close a')

    modalCloseBtn?.addEventListener('click', () => {
        const modal = document.querySelector('.modal')
        modal.remove()
    })
})

window.addEventListener('load', (_) => {
    $('#reset-settings').mousedown((e) => {
        e.preventDefault()
        $.ajax({
            url: "reset-settings/",
            success: (response) => {
                document.getElementById("reset-settings").style = "display: none"
                document.getElementById("send-msg-btn").innerText = "Дать доступ к Google-таблице"
            },
            error: (response) => {
                alert(response.responseJSON?.errors)
            }
        });

        return false;
    });
})
