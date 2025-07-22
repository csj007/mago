let index = 1;

// 添加材料行
function addRow() {
    const row = document.getElementById('material-row').cloneNode(true);
    row.id = `material-row-${index}`;
    index += 1;
    const inputs = row.querySelectorAll('input');
    inputs.forEach(input => {
        input.value = '';
    });
    document.getElementById('material-form').appendChild(row);
}

// 提交记录生成表格并显示按钮
function submitRecord() {
    console.log('submitRecord 函数开始执行');

    const rows = document.querySelectorAll('#material-form .row');
    const table = document.getElementById('materials-table');
    table.innerHTML = '';
    const data = [];

    rows.forEach(row => {
        const name = row.querySelector('input[name="medicine[]"]').value.trim();
        const amount = parseFloat(row.querySelector('input[name="amount[]"]').value) || 0;
        if (name && amount > 0) {
            data.push({ name: name, amount: amount });
        }
    });

    console.log('收集到的数据:', data);

    if (data.length === 0) {
        alert('请至少输入一个材料和克数！');
        return;
    }

    // 表头行
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = `<th>药品名称</th>`.repeat(data.length + 1);
    table.appendChild(headerRow);

    // 名称行
    const namesRow = document.createElement('tr');
    data.forEach(item => {
        const td = document.createElement('td');
        td.innerText = item.name;
        namesRow.appendChild(td);
    });
    const totalNameTd = document.createElement('td');
    totalNameTd.innerText = '总计';
    namesRow.appendChild(totalNameTd);
    table.appendChild(namesRow);

    // 克数行
    const valuesRow = document.createElement('tr');
    data.forEach(item => {
        const td = document.createElement('td');
        td.innerText = item.amount;
        valuesRow.appendChild(td);
    });
    const totalTd = document.createElement('td');
    totalTd.innerText = data.reduce((sum, item) => sum + item.amount, 0);
    valuesRow.appendChild(totalTd);
    table.appendChild(valuesRow);

    console.log('表格生成完成');

    // 显示按钮
    const actionButtons = document.getElementById('action-buttons');
    if (actionButtons) {
        actionButtons.style.display = 'block';
        actionButtons.classList.remove('d-none');
        console.log('action-buttons 元素:', actionButtons);
        console.log('action-buttons 已显示');
    } else {
        console.error('未找到 action-buttons 元素，请检查 ID');
    }
}

// 复制表格为 Excel 可识别格式
function copyTable() {
    const table = document.getElementById('materials-table');
    let text = '';
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cells = row.querySelectorAll('td, th');
        const rowText = Array.from(cells).map(cell => cell.innerText).join('\t');
        text += rowText + '\n';
    });

    navigator.clipboard.writeText(text)
        .then(() => alert('表格已复制！可以直接粘贴到 Excel 中。'))
        .catch(err => console.error('复制失败:', err));
}

// 复制表格为图片到剪贴板
function copyTableAsImage() {
    domtoimage.toPng(document.getElementById('materials-table'))
        .then(dataUrl => {
            navigator.clipboard.write([
                new ClipboardItem({
                    'image/png': fetch(dataUrl).then(response => response.blob())
                })
            ]).then(() => {
                alert('表格图片已复制到剪贴板！');
            }).catch(err => {
                console.error('复制图片失败:', err);
            });
        })
        .catch(err => {
            console.error('生成图片失败:', err);
        });
}

// 下载表格为图片
function downloadTableAsImage() {
    domtoimage.toBlob(document.getElementById('materials-table'))
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'material-record.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        })
        .catch(err => {
            console.error('生成图片失败:', err);
        });
}

// 清空所有数据并隐藏按钮（可选）
function resetForm() {
    document.getElementById('material-form').innerHTML = `
        <div class="row mb-2" id="material-row">
            <div class="col-md-4">
                <input type="text" class="form-control" placeholder="药品名称" name="medicine[]">
            </div>
            <div class="col-md-4">
                <input type="number" class="form-control" placeholder="克数" name="amount[]">
            </div>
            <div class="col-md-2">
                <button class="btn btn-success" onclick="addRow()">添加材料</button>
            </div>
        </div>
    `;
    document.getElementById('materials-table').innerHTML = '';
    document.getElementById('action-buttons').style.display = 'none';
}
