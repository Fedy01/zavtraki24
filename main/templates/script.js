// Корзина
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let cartTotal = parseFloat(localStorage.getItem('cartTotal')) || 0;

// Обновление отображения корзины
function updateCartDisplay() {
    const cartTotalElements = document.querySelectorAll('.cart-total');
    cartTotalElements.forEach(element => {
        element.textContent = cartTotal.toFixed(2);
    });

    // Обновляем счетчик товаров
    const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        element.textContent = cartCount;
    });

    // Обновляем страницу корзины, если мы на ней
    if (document.querySelector('.cart-items')) {
        renderCartItems();
    }
}

// Добавление товара в корзину
function addToCart(name, price, quantity = 1) {
    // Проверяем, есть ли уже такой товар в корзине
    const existingItem = cart.find(item => item.name === name);

    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            name: name,
            price: price,
            quantity: quantity
        });
    }

    // Обновляем общую сумму
    cartTotal += price * quantity;

    // Сохраняем в localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    localStorage.setItem('cartTotal', cartTotal.toString());

    // Обновляем отображение
    updateCartDisplay();

    return true;
}

// Удаление товара из корзины
function removeFromCart(index) {
    if (index >= 0 && index < cart.length) {
        const item = cart[index];
        cartTotal -= item.price * item.quantity;

        cart.splice(index, 1);

        // Сохраняем в localStorage
        localStorage.setItem('cart', JSON.stringify(cart));
        localStorage.setItem('cartTotal', cartTotal.toString());

        // Обновляем отображение
        updateCartDisplay();

        return true;
    }
    return false;
}

// Отображение товаров в корзине
function renderCartItems() {
    const cartItemsContainer = document.querySelector('.cart-items');
    const cartTotalElement = document.querySelector('.cart-total-amount');
    const orderTotalElement = document.querySelector('.order-total');

    if (!cartItemsContainer) return;

    // Очищаем контейнер
    cartItemsContainer.innerHTML = '';

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p class="empty-cart" style="text-align: center; padding: 40px; color: #666;">Корзина пуста</p>';
        if (cartTotalElement) {
            cartTotalElement.textContent = '0.00';
        }
        if (orderTotalElement) {
            orderTotalElement.textContent = '0.00';
        }
        return;
    }

    // Добавляем каждый товар
    cart.forEach((item, index) => {
        const itemElement = document.createElement('div');
        itemElement.className = 'cart-item';
        itemElement.innerHTML = `
            <div class="cart-item-info">
                <h3>${item.name}</h3>
                <p>${item.quantity} шт. × ${item.price.toFixed(2)} руб.</p>
            </div>
            <div class="cart-item-price">${(item.price * item.quantity).toFixed(2)} руб.</div>
        `;
        cartItemsContainer.appendChild(itemElement);
    });

    // Обновляем общую сумму
    if (cartTotalElement) {
        cartTotalElement.textContent = cartTotal.toFixed(2);
    }
    if (orderTotalElement) {
        orderTotalElement.textContent = `${cartTotal.toFixed(2)} руб.`;
    }
}

// Инициализация страницы оформления заказа
function initializeCheckout() {
    const orderTotalElement = document.querySelector('.order-total');
    if (orderTotalElement) {
        orderTotalElement.textContent = `${cartTotal.toFixed(2)} руб.`;
    }

    // Выбор способа оплаты
    const paymentMethods = document.querySelectorAll('.payment-method');
    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            paymentMethods.forEach(m => m.classList.remove('active'));
            this.classList.add('active');

            // Отмечаем соответствующий radio input
            const radioInput = this.querySelector('input[type="radio"]');
            if (radioInput) {
                radioInput.checked = true;
            }
        });
    });

    // Оформление заказа
    const checkoutForm = document.querySelector('.checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Проверяем, заполнены ли обязательные поля
            const nameInput = document.getElementById('name');
            const phoneInput = document.getElementById('phone');

            if (!nameInput.value.trim()) {
                alert('Пожалуйста, введите ваше имя');
                nameInput.focus();
                return;
            }

            if (!phoneInput.value.trim()) {
                alert('Пожалуйста, введите номер телефона');
                phoneInput.focus();
                return;
            }

            // Проверяем, выбран ли способ оплаты
            const selectedPayment = document.querySelector('.payment-method.active');
            if (!selectedPayment) {
                alert('Пожалуйста, выберите способ оплаты');
                return;
            }

            // Проверяем, есть ли товары в корзине
            if (cart.length === 0) {
                alert('Корзина пуста. Добавьте товары перед оформлением заказа.');
                return;
            }

            // Собираем данные заказа
            const orderData = {
                customer: {
                    name: nameInput.value,
                    phone: phoneInput.value,
                    pickupTime: document.getElementById('time').value
                },
                paymentMethod: selectedPayment.querySelector('input').id,
                items: cart,
                total: cartTotal,
                orderDate: new Date().toISOString()
            };

            // Здесь обычно отправка данных на сервер
            console.log('Данные заказа:', orderData);

            // Показываем сообщение об успехе
            alert(`Заказ оформлен! Номер вашего заказа: #${Math.floor(Math.random() * 10000)}. Спасибо за покупку!`);

            // Очищаем корзину
            cart = [];
            cartTotal = 0;
            localStorage.removeItem('cart');
            localStorage.removeItem('cartTotal');

            // Перенаправляем на главную
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        });
    }
}

// Основная инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация корзины
    updateCartDisplay();

    // Обработчики для кнопок "В корзину" на главной
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const name = this.getAttribute('data-name');
            const price = parseFloat(this.getAttribute('data-price'));
            const quantity = parseInt(this.getAttribute('data-quantity')) || 1;

            // Добавляем товар в корзину
            addToCart(name, price, quantity);

            // Анимация кнопки
            const originalText = this.textContent;
            this.textContent = 'Добавлено!';
            this.style.backgroundColor = '#34c759';

            setTimeout(() => {
                this.textContent = originalText;
                this.style.backgroundColor = '';
            }, 1500);
        });
    });

    // Обработчики для изменения количества в меню
    const quantityButtons = document.querySelectorAll('.quantity-btn');
    quantityButtons.forEach(button => {
        button.addEventListener('click', function() {
            const container = this.closest('.quantity-selector');
            const quantityElement = container.querySelector('.quantity');
            const addButton = container.closest('.menu-item').querySelector('.add-to-cart');

            let quantity = parseInt(quantityElement.textContent);

            if (this.classList.contains('plus')) {
                quantity += 1;
            } else if (this.classList.contains('minus') && quantity > 0) {
                quantity -= 1;
            }

            quantityElement.textContent = quantity;

            // Обновляем атрибуты кнопки
            if (quantity > 0) {
                addButton.setAttribute('data-quantity', quantity);
                addButton.textContent = `В корзину (${quantity})`;
            } else {
                addButton.removeAttribute('data-quantity');
                addButton.textContent = 'В корзину';
            }
        });
    });

    // Инициализация страницы оформления заказа
    if (document.querySelector('.checkout-page')) {
        initializeCheckout();
    }

    // Активное состояние в навигации
    const currentPage = window.location.pathname;
    const navLinks = document.querySelectorAll('.main-nav a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPage.split('/').pop()) {
            link.classList.add('active');
        }
    });

    // Обновляем отображение корзины при загрузке страницы корзины
    if (document.querySelector('.cart-page')) {
        renderCartItems();
    }

    // Добавляем счетчик товаров в корзину
    const cartElements = document.querySelectorAll('.cart');
    const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

    if (cartCount > 0) {
        cartElements.forEach(cartElement => {
            // Добавляем счетчик, если его еще нет
            if (!cartElement.querySelector('.cart-count')) {
                const cartText = cartElement.querySelector('.cart-total') ?
                    cartElement.innerHTML :
                    cartElement.textContent;

                cartElement.innerHTML = `
                    <i class="fas fa-shopping-cart"></i>
                    Корзина
                    <span class="cart-count" style="background-color: #fff; color: #ff3b30; padding: 2px 6px; border-radius: 50%; font-size: 12px; margin-right: 5px;">${cartCount}</span>
                    <span class="cart-total">${cartTotal.toFixed(2)}</span> руб.
                `;
            }
        });
    }
});

// Функция для очистки корзины (можно вызвать из консоли или добавить кнопку)
function clearCart() {
    cart = [];
    cartTotal = 0;
    localStorage.removeItem('cart');
    localStorage.removeItem('cartTotal');
    updateCartDisplay();
    alert('Корзина очищена');
}

// Экспортируем функции для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        addToCart,
        removeFromCart,
        updateCartDisplay,
        clearCart,
        cart,
        cartTotal
    };
}