function uploadFile() {
    const dialog = document.getElementById('fileDialog')
    dialog.click();
    dialog.onchange = function () {
        setSelectedFile(dialog.files[0]);
    }
}

function removeDropFileText() {
    const el = document.getElementById("addFileView");
    if (el) {
        el.remove();
    }
}

function getSize(file) {
    const size_mb = Math.round(file.size / 1024 / 1024, 2);
    return `${size_mb} mb`
}

function setSelectedFile(file) {
    if (file === undefined) { return; }
    
    const MAX_FILE_SIZE = 500 * 1024 * 1024;  // 500mb
    if (file.size > MAX_FILE_SIZE) {
        return showTransStatus("Maximum file size is: 150mb!")
    }

    let name = file.name;
    if (name.length > 60) {
        name = name.substr(0, 57) + "...";
    }

    removeDropFileText();
    document.getElementById("selectedFileView").setAttribute("used", "1");
    document.getElementById("fileName").innerText = name;

    selectedFile = file;
}

const dropZone = document.getElementById('dropZone');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, e => e.preventDefault());
});

dropZone.addEventListener('dragover', () => {
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', event => {
    dropZone.classList.remove('dragover');

    const files = event.dataTransfer.files;
    if (files.length > 1) {
        return showTransStatus("Select only one file.");
    }
    setSelectedFile(files[0]);
});


function handleDigitInput(input, e) {
    let index = parseInt(input.id);

    if (e != null) {
        if (e.key == "Enter") {
            return document.getElementById("recv-get").click();
        }

        if (e.key == "Backspace" && index >= 1) {
            input.value = "";
            if (index > 1) { document.getElementById(--index).focus(); }
            return;
        }
    }
    
    let value = parseInt(input.value);
    
    if (isNaN(value) || (index == 1 && value == 0)) {
        input.value = "";
        return;
    }

    if (index < 5) {
        document.getElementById(++index).focus();
    }
}

const digitInputsContainer = document.getElementsByClassName("codeInputContainer")[0];
Array.from(digitInputsContainer.children).forEach(inputNode => {
    inputNode.value = "";
    inputNode.addEventListener("input", (e) => {handleDigitInput(inputNode, null)});
    inputNode.addEventListener("keydown", (e) => {handleDigitInput(inputNode, e)});
})


function getCode() {
    let code = "";

    Array.from(digitInputsContainer.children).forEach(inputNode => {
        let value = parseInt(inputNode.value);
        if (isNaN(value)) { return null; }
        code += inputNode.value;
    })

    return parseInt(code);
}

function copyResultCode() {
    const code = document.getElementById("file-code").innerText;
    window.navigator.clipboard.writeText(code);
    showTransStatus("Copied");
}

function copyResultUrl() {
    const url = window.location.origin + "/" + document.getElementById("share-url-code").innerText;
    window.navigator.clipboard.writeText(url);
    showTransStatus("Copied");
}

