window.addEventListener('load', (_) => {
    const tabs = document.querySelectorAll('.tabs__tab');
    const menu = document.querySelectorAll('.menu')
    
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', (_) => {
            tabs.forEach(tab => {
                tab.classList.remove('tabs__tab--active')
            })

            tab.classList.add('tabs__tab--active')
            menu.forEach(menu => {
                menu.style.display = 'none'
            })

            menu[index].style.display = ''
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
            if (anyInputFilled)
            {
                submitButton.classList.remove('button--disabled')
                submitButton.classList.add('button--filled')
            }
            else
            {
                submitButton.classList.remove('button--filled')
                submitButton.classList.add('button--disabled')
            }
        })
    })
})
