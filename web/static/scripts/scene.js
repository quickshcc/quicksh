function updateTransferToResult(name, exp, code) {
    animTransfer();
    document.getElementById("share-url-code").innerText = code;

    document.getElementById("file-code").innerText = code;
    document.getElementById("file-name").innerText = name;
    document.getElementById("file-exp").innerText = exp;

    document.getElementById("transfer-body")?.remove();
    document.getElementById("transfer-success-body").style.display = "inline";

}


// -- QR CODE
const QR_WINDOW = document.getElementsByClassName("qr-code-container")[0];

function openQrWindow() {
    generateQr();
    QR_WINDOW.setAttribute("fold", "0");
}

function hideQrWindow() {
    QR_WINDOW.setAttribute("fold", "1");
}

function generateQr() {
    document.querySelector('#qr-code').innerHTML = "";
    const url = window.location.origin + "/" + document.getElementById("share-url-code").innerText;

    QrCreator.render({
        text: url,
        radius: 0.4, // 0.0 to 0.5
        ecLevel: 'H', // L, M, Q, H
        fill: '#fefefe', // foreground color
        background: null, // color or null for transparent
        size: 200 // in pixels
    }, document.querySelector('#qr-code'));
}


// -- HISTORY
const HISTORY_WINDOW = document.getElementsByClassName("uploads-history-container")[0];

function openHistoryWindow() {
    HISTORY_WINDOW.setAttribute("fold", "0");
}

function hideHistoryWindow() {
    HISTORY_WINDOW.setAttribute("fold", "1");
}

function flipHistoryWindow() {
    if (HISTORY_WINDOW.getAttribute("fold") == "0") {
        hideHistoryWindow();
    } else {
        openHistoryWindow();
    }
}


const HIST_ROWS_CONTAINER = document.getElementById("history-rows");

function addHistoryRow(code, name, expire) {
    if (name.length > 14) {
        name = name.substring(0, 13) + "…";
    }
    
    const row = document.createElement("div");
    row.className = "history-row";
    row.id = `${code}`;

    const row_data = document.createElement("div");
    row_data.className = "history-row-data";

    const span_code = document.createElement("span");
    span_code.className = "history-code";
    span_code.innerText = code;
    row_data.appendChild(span_code);
    
    const span_name = document.createElement("span");
    span_name.className = "history-name";
    span_name.innerText = name;
    row_data.appendChild(span_name);
    
    const span_expire = document.createElement("span");
    span_expire.className = "history-expire";
    span_expire.innerText = expire;
    row_data.appendChild(span_expire);

    row.appendChild(row_data);

    const rm_button = document.createElement("button");
    rm_button.className = "history-remove";
    rm_button.addEventListener("click", () => {removeTransfer(code)})
    rm_button.innerHTML = `<i class="fa-solid fa-trash-can"></i>`

    row.appendChild(rm_button);

    HIST_ROWS_CONTAINER.appendChild(row);
}

function removeHistoryRow(code) {
    document.getElementById(`${code}`)?.remove();
}


// -- AUTO FILL CODE
function checkPathForCode() {
    const code = window.location.pathname.substring(1);
    if (!code) { return; }
    
    if (code.length !== 5) {
        return showRecvStatus("Invalid code's length");
    }
    
    const codeInt = parseInt(code);
    if (isNaN(codeInt)) {
        return showRecvStatus("Invalid code.");
    }
    if (codeInt < 10000 || codeInt > 99999) {
        return showRecvStatus("Invalid code's length");
    }
    
    for (let i = 0; i < 5; i++) {
        const digit = code[i];
        document.getElementById(`${i + 1}`).value = digit;
    }
    showRecvStatus("Pasted code: " + code);

}

// updateTransferToResult("rufus.exe", "12/10/2024", 654732)
