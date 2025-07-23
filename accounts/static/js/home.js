let index = 1;

// 添加材料行
function addRow() {
    const row = document.getElementById('material-row').cloneNode(true);
    row.id = `material-row-${index}`;
    index += 1;

    // 清空输入的值
    const inputs = row.querySelectorAll('input');
    inputs.forEach(input => {
        input.value = '';
    });

    document.getElementById('material-form').appendChild(row);
}


function deleteRow(button) {
    const row = button.closest('.row');
    if (row && row.id.startsWith('material-row-')) {
        row.remove(); // 删除该行
    } else if (row && row.id === 'material-row') {
        alert('不能删除初始行！');
    }
}

// 提交记录生成表格并显示按钮
function submitRecord() {
    const rows = document.querySelectorAll('#material-form .row');
    const data = [];
    rows.forEach(row => {
        const name = row.querySelector('input[name="medicine[]"]').value.trim();
        const amount = parseFloat(row.querySelector('input[name="amount[]"]').value) || 0;
        if (name && amount > 0) {
            data.push({ name: name, amount: amount });
        }
    });
    if (data.length === 0) {
        alert('请至少输入一个材料和克数！');
        return;
    }

    // 生成两个表格
    for (let i = 0; i < 2; i++) {
        let tableId = `materials-table-${i}`;
        let buttonsId = `action-buttons-${i}`;

        // 创建表格
        const table = document.createElement('table');
        table.className = 'table table-bordered';
        table.id = tableId;

        // 创建按钮组
        const buttons = document.createElement('div');
        buttons.id = buttonsId;
        buttons.className = 'd-none mt-3';
        buttons.innerHTML = `
            <button class="btn btn-success" onclick="copyTable(${i})">复制表格</button>
            <button class="btn btn-info" onclick="copyTableAsImage(${i})">复制图片</button>
            <button class="btn btn-primary" onclick="downloadTableAsImage(${i})">下载图片</button>
        `;

        // 插入标题
        const title = document.createElement('h3');
        title.className = 'mb-3';

        // 插入 DOM
        const container = document.createElement('div');
        container.innerHTML = '';
        container.appendChild(title);
        container.appendChild(table);
        container.appendChild(buttons);

        // 插入页面
        document.querySelector('#materials-table').parentNode.appendChild(container);

        // 发起请求获取药品编码
        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.cookie.split('=')[1].split(';')[0]
            },
            body: JSON.stringify({ materials: data })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('网络请求失败');
            }
            return response.json();
        })
        .then(result => {
            const table = document.getElementById(tableId);
            table.innerHTML = '';
            const namesRow = document.createElement('tr');
            result.forEach(item => {
                const td = document.createElement('td');
                td.innerText = i === 1 ? item.name : item.code;
                namesRow.appendChild(td);
            });
            const totalNameTd = document.createElement('td');
            totalNameTd.innerText = '总计';
            namesRow.appendChild(totalNameTd);
            table.appendChild(namesRow);

            const valuesRow = document.createElement('tr');
            data.forEach(item => {
                const td = document.createElement('td');
                td.innerText = item.amount;
                valuesRow.appendChild(td);
            });
            const totalTd = document.createElement('td');
            const totalAmount = data.reduce((sum, item) => sum + item.amount, 0);
            totalTd.innerText = totalAmount.toFixed(4); // 保留小数点后 6 位
            valuesRow.appendChild(totalTd);
            table.appendChild(valuesRow);

            // 显示按钮
            const actionButtons = document.getElementById(buttonsId);
            if (actionButtons) {
                actionButtons.style.display = 'block';
                actionButtons.classList.remove('d-none');
            } else {
                console.error('未找到 action-buttons 元素，请检查 ID');
            }
        })
        .catch(err => {
            console.error('请求失败:', err);
            alert('无法获取药品编号，请检查后端服务');
        });
    }
}

function copyTable(tableIndex = 0) {
    const table = document.getElementById(`materials-table-${tableIndex}`);
    const rows = table.querySelectorAll("tr");
    let tsvContent = "";
    rows.forEach((row) => {
        const cells = row.querySelectorAll("td");
        const rowValues = Array.from(cells).map(cell => {
            const text = cell.textContent.trim();
            if (text.endsWith("克")) {
                return parseFloat(text.replace(/克/g, ""));
            }
            return text;
        });
        tsvContent += rowValues.join("\t") + "\n";
    });
    const temp = document.createElement("textarea");
    temp.value = tsvContent;
    document.body.appendChild(temp);
    temp.select();
    document.execCommand("copy");
    document.body.removeChild(temp);
    alert("表格已复制为可粘贴到 Excel 的格式");
}

function copyTableAsImage(tableIndex = 0) {
    const element = document.getElementById(`materials-table-${tableIndex}`);
    html2canvas(element).then(canvas => {
        canvas.toBlob(blob => {
            if (!blob) return;
            const clipboardItem = new ClipboardItem({ 'image/png': blob });
            navigator.clipboard.write([clipboardItem])
                .then(() => {
                    alert('表格图片已复制到剪贴板！');
                })
                .catch(err => {
                    console.error('复制图片失败:', err);
                });
        }, 'image/png');
    }).catch(err => {
        console.error('生成图片失败:', err);
    });
}

function downloadTableAsImage(tableIndex = 0) {
    const element = document.getElementById(`materials-table-${tableIndex}`);
    html2canvas(element).then(canvas => {
        const image = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = image;
        link.download = `material-record-${tableIndex}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }).catch(err => {
        console.error('生成图片失败:', err);
    });
}
