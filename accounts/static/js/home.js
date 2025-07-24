let index = 1;

// 添加材料行
function addRow() {
    const row = document.getElementById('material-row').cloneNode(true);
    row.id = `material-row-${index}`;
    index += 1;

    // 清空输入框
    const inputs = row.querySelectorAll('input');
    inputs.forEach(input => {
        input.value = '';
    });

    // 为新行的药品搜索框绑定事件（克隆后需要重新绑定）
    const medicineInput = row.querySelector('input[type="text"]');
    setupMedicineInput(medicineInput);

    document.getElementById('material-form').appendChild(row);
}

function setupMedicineInput(input) {
    // 点击输入框时展开药品下拉框
    input.addEventListener('focus', function () {
        if (this.value.trim() === '') {
            fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.cookie.split('=')[1].split(';')[0]
                },
                body: JSON.stringify({ search: '' })
            })
            .then(response => response.json())
            .then(data => {
                showMedicineList(this, data);
            })
            .catch(err => {
                console.error('搜索药品失败:', err);
                alert('搜索药品失败，请检查后端服务');
            });
        }
    });

    // 输入变化时触发搜索
    input.addEventListener('input', function () {
        const value = this.value.trim();
        if (value === '') {
            document.getElementById('custom-medicine-list').classList.add('d-none');
            return;
        }

        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.cookie.split('=')[1].split(';')[0]
            },
            body: JSON.stringify({ search: value })
        })
        .then(response => response.json())
        .then(data => {
            showMedicineList(this, data);
        })
        .catch(err => {
            console.error('搜索药品失败:', err);
            alert('搜索药品失败，请检查后端服务');
        });
    });

    input.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown') {
            selectedIndex = (selectedIndex + 1) % medicineListItems.length;
            updateActiveItem();
        } else if (e.key === 'ArrowUp') {
            selectedIndex = (selectedIndex - 1 + medicineListItems.length) % medicineListItems.length;
            updateActiveItem();
        } else if (e.key === 'Enter' && medicineListItems.length > 0) {
            medicineListItems[selectedIndex].click();
            e.preventDefault();
        }
    });
}

function updateActiveItem() {
    medicineListItems.forEach((item, index) => {
        item.classList.toggle('active', index === selectedIndex);
    });
}

function deleteRow(button) {
    const row = button.closest('.row');
    if (row && row.id.startsWith('material-row-')) {
        row.remove(); // 删除该行
    } else if (row && row.id === 'material-row') {
        alert('不能删除初始行！');
    }
}

async function getMedicineCode(name, manufacturer, cas) {
    const response = await fetch(`/api/find_medicine_codes/?name=${encodeURIComponent(name)}&manufacturer=${encodeURIComponent(manufacturer)}&cas=${encodeURIComponent(cas)}`);
    const result = await response.json();
    return result.code;
}

// 提交记录生成表格并显示按钮
async function submitRecord() {
    const rows = document.querySelectorAll('#material-form .row');
    const data = [];

    for (let row of rows) {
        const nameInput = row.querySelector('input[type="text"]');
        const amountInput = row.querySelector('input[name="amount[]"]');
        const name = nameInput.value.trim();
        const amount = parseFloat(amountInput.value) || 0;

        if (name && amount > 0) {
            const parts = name.split('-');
            const namePart = parts[0] || '';
            const manufacturerPart = parts[1] || '';
            const casPart = parts.slice(2).join('-') || '';

            const codePart = await getMedicineCode(namePart, manufacturerPart, casPart);

            data.push({
                name: namePart,
                manufacturer: manufacturerPart || null,
                cas: casPart || null,
                code: codePart || namePart,
                amount: amount
            });
        }
    }

    if (data.length === 0) {
        alert('请至少输入一个材料和克数！');
        return;
    }

    // 生成两个表格
    for (let i = 0; i < 2; i++) {
        let tableId = `materials-table-${i}`;
        let buttonsId = `action-buttons-${i}`;
        const table = document.createElement('table');
        table.className = 'table table-bordered';
        table.id = tableId;
        const buttons = document.createElement('div');
        buttons.id = buttonsId;
        buttons.className = 'd-none mt-3';
        buttons.innerHTML = `
            <button class="btn btn-success" onclick="copyTable(${i})">复制表格</button>
            <button class="btn btn-info" onclick="copyTableAsImage(${i})">复制图片</button>
            <button class="btn btn-primary" onclick="downloadTableAsImage(${i})">下载图片</button>
        `;
        const title = document.createElement('h3');
        title.className = 'mb-3';
        const container = document.createElement('div');
        container.innerHTML = '';
        container.appendChild(title);
        container.appendChild(table);
        container.appendChild(buttons);
        document.querySelector('#materials-table').parentNode.appendChild(container);

        // ✅ 直接使用你构造的 data 来生成表格
        const resultTable = document.getElementById(tableId);
        resultTable.innerHTML = '';

        // 构建名称行
        const namesRow = document.createElement('tr');
        data.forEach(item => {
            const td = document.createElement('td');
            console.log(item);
            td.innerText = i === 1 ? [
                item.name,
                item.manufacturer,
                item.cas
            ].filter(Boolean).join('\n') : item.code;
            
            namesRow.appendChild(td);
        });
        const totalNameTd = document.createElement('td');
        totalNameTd.innerText = '总计';
        namesRow.appendChild(totalNameTd);
        resultTable.appendChild(namesRow);

        // 构建克数行
        const valuesRow = document.createElement('tr');
        data.forEach(item => {
            const td = document.createElement('td');
            td.innerText = item.amount;
            valuesRow.appendChild(td);
        });
        const totalTd = document.createElement('td');
        const totalAmount = data.reduce((sum, item) => sum + item.amount, 0);
        totalTd.innerText = totalAmount.toFixed(4);
        valuesRow.appendChild(totalTd);
        resultTable.appendChild(valuesRow);

        // 显示按钮
        const actionButtons = document.getElementById(buttonsId);
        if (actionButtons) {
            actionButtons.style.display = 'block';
            actionButtons.classList.remove('d-none');
        } else {
            console.error('未找到 action-buttons 元素，请检查 ID');
        }
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

let selectedMedicine = null;
let selectedManufacturer = null;
let selectedIndex = 0;
let medicineListItems = [];
function showMedicineList(inputElement, data) {
    const list = document.getElementById('custom-medicine-list');
    list.innerHTML = '';
    selectedIndex = 0;
    medicineListItems = [];

    if (!data || !Array.isArray(data)) {
        list.classList.add('d-none');
        return;
    }

    // 按拼音排序药品名
    const sortedMedicines = [...data].sort((a, b) => {
        return a.name.localeCompare(b.name);
    });

    sortedMedicines.forEach(medicine => {
        const item = document.createElement('div');
        item.className = 'p-2 hover-item';
        item.innerText = medicine.name;
        item.dataset.name = medicine.name;
        item.dataset.manufacturer_data = JSON.stringify(medicine.manufacturer_data);

        item.onclick = () => {
            selectedMedicineName = item.dataset.name;

            const manufacturerData = medicine.manufacturer_data;
            const validManufacturers = manufacturerData
                .filter(m => m.manufacturer && m.manufacturer.trim() !== '');

            if (validManufacturers.length === 0) {
                inputElement.value = medicine.name;
                closeAllPopups();
                return;
            }

            showManufacturerPopup(item, inputElement);
        };

        medicineListItems.push(item);
        list.appendChild(item);
    });

    const rect = inputElement.getBoundingClientRect();
    list.style.top = `${rect.bottom + window.scrollY}px`;
    list.style.left = `${rect.left + window.scrollX}px`;
    list.classList.remove('d-none');

    // ✅ 自动定位并高亮最匹配的药品名
    const searchValue = inputElement.value.trim().toLowerCase();
    if (searchValue) {
        const foundIndex = medicineListItems.findIndex(item =>
            item.innerText.toLowerCase().startsWith(searchValue)
        );
        if (foundIndex !== -1) {
            selectedIndex = foundIndex;
            medicineListItems.forEach((item, i) => {
                item.classList.toggle('active', i === selectedIndex);
            });
            // 滚动到匹配项
            medicineListItems[selectedIndex].scrollIntoView({ block: 'nearest' });
        }
    }
}

function showManufacturerPopup(item, inputElement) {
    const popup = document.getElementById('manufacturer-popup');
    popup.innerHTML = '';
    popup.classList.add('d-none');
    const manufacturerData = JSON.parse(item.dataset.manufacturer_data);
    const rect = item.getBoundingClientRect();

    manufacturerData.forEach(manufacturer => {
        const itemEl = document.createElement('div');
        itemEl.className = 'p-2 hover-item';
        itemEl.innerText = manufacturer.manufacturer;
        itemEl.dataset.name = item.dataset.name;
        itemEl.dataset.manufacturer = manufacturer.manufacturer;
        itemEl.dataset.cas_list = JSON.stringify(manufacturer.cas_list);

        itemEl.onclick = (e) => {
            e.stopPropagation();
            selectedManufacturer = {
                name: itemEl.dataset.name,
                manufacturer: itemEl.dataset.manufacturer,
                cas_list: JSON.parse(itemEl.dataset.cas_list)
            };

            if (selectedManufacturer.cas_list.length === 0) {
                // ✅ 修复：使用传进来的 inputElement
                inputElement.value = `${selectedManufacturer.name}-${selectedManufacturer.manufacturer}`;
                closeAllPopups();
                return;
            }

            // ✅ 修复：传递 inputElement
            showCASSelector(itemEl, inputElement);
        };

        popup.appendChild(itemEl);
    });

    popup.style.top = `${rect.top + window.scrollY}px`;
    popup.style.left = `${rect.right + window.scrollX + 10}px`;
    popup.classList.remove('d-none');
}

function showCASSelector(item, inputElement) {
    const popup = document.getElementById('cas-popup');
    popup.innerHTML = '';
    popup.classList.add('d-none');
    const rect = item.getBoundingClientRect();
    const cas_list = selectedManufacturer.cas_list;

    if (!cas_list || cas_list.length === 0) {
        return;
    }

    cas_list.forEach(cas => {
        const itemEl = document.createElement('div');
        itemEl.className = 'p-2 hover-item';
        itemEl.innerText = cas;
        itemEl.onclick = (e) => {
            e.stopPropagation();
            // ✅ 修复：使用传进来的 inputElement
            inputElement.value = `${selectedManufacturer.name}-${selectedManufacturer.manufacturer}-${cas}`;
            closeAllPopups();
        };
        popup.appendChild(itemEl);
    });

    popup.style.top = `${rect.top + window.scrollY}px`;
    popup.style.left = `${rect.right + window.scrollX + 10}px`;
    popup.classList.remove('d-none');
}

function closeAllPopups() {
    document.getElementById('custom-medicine-list').classList.add('d-none');
    document.getElementById('manufacturer-popup').classList.add('d-none');
    document.getElementById('cas-popup').classList.add('d-none');
}

setupMedicineInput(document.getElementById('medicine-search'));
// 搜索药品
// 点击输入框时自动展开药品列表
document.getElementById('medicine-search').addEventListener('focus', function () {
    if (this.value.trim() === '') {
        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.cookie.split('=')[1].split(';')[0]
            },
            body: JSON.stringify({ search: '' }) // 搜索空字符串，表示全部候选
        })
        .then(response => response.json())
        .then(data => {
            // ✅ 修复：传递 this 作为 inputElement
            showMedicineList(this, data);
        })
        .catch(err => {
            console.error('搜索药品失败:', err);
            alert('搜索药品失败，请检查后端服务');
        });
    }
});

document.addEventListener('click', function (e) {
    const target = e.target;

    // ✅ 如果点击的是药品输入框或药品下拉框中的项，不关闭
    if (target.matches('input[type="text"]') || target.closest('#custom-medicine-list')) {
        return;
    }

    // 否则关闭所有下拉框
    document.getElementById('custom-medicine-list').classList.add('d-none');
    document.getElementById('manufacturer-popup').classList.add('d-none');
    document.getElementById('cas-popup').classList.add('d-none');
});
