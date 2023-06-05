function sendData() {
    var input = document.getElementById('inputField').value;

    // Отправка данных на сервер
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/orders', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            // Обновление таблицы с результатами
            updateTable(response.result);
        }
    };
    xhr.send(JSON.stringify({data: input}));
}

function updateTable(result) {
    var tableBody = document.getElementById('tableBody');
    var newRow = tableBody.insertRow();
    var cell = newRow.insertCell();
    cell.innerHTML = result;
}
