const API = "https://quicksh.cc/api/";


function sendTransferFile() {
    if (selectedFile === null) { return; }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('expire', selectedDuration);

    const options = {
        method: 'POST',
        body: formData
    };

    fetch(API + "transfer", options)
        .then(response => response.json())
        .then(result => {
            if (!result.status) { return showTransStatus(result.error); }

            updateTransferToResult(selectedFile.name, result.expire, result.code);
            addHistoryRow(result.code, selectedFile.name, result.expire);

        })
        .catch(error => {
            console.error('Error while sending TRANSFER/ request', error);
            showTransStatus("Failed to transfer file.");
        });
    }
    

let downloadFilename = null;

function receiveFile(code) {
    try {
        code = parseInt(code);
        if (isNaN(code) || code < 10000 || code > 99999) { return showRecvStatus("Invalid code."); }
    } catch {
        return showRecvStatus("Invalid code.");
    }
    
    const options = {
        method: 'GET'
    };

    fetch(API + "receive/" + code, options)
        .then(result => {
            if (!result.ok) {
                return showRecvStatus("Invalid or expired code");
            }
            
            const contentDisposition = result.headers.get('content-disposition');

            const filenameRegex = /filename\*=(?:[^\']*)'[^']*'(.+)/;
            const filenameFallbackRegex = /filename="(.+?)"/;

            if (contentDisposition) {
                const filenameStarMatch = contentDisposition.match(filenameRegex);
                if (filenameStarMatch) {
                    downloadFilename = decodeURIComponent(filenameStarMatch[1]);
                } else {
                    const filenameMatch = contentDisposition.match(filenameFallbackRegex);
                    if (filenameMatch) {
                        downloadFilename = filenameMatch[1];
                    }
                }
            }
            
            if (downloadFilename === null) {
                downloadFilename = "file";
            }

            return result.blob();

        }).then(result => {
            if (result === undefined) { return; }
            
            const anchor = document.createElement('a');
            anchor.href = URL.createObjectURL(result);
            anchor.download = downloadFilename;
            anchor.click();
            URL.revokeObjectURL(anchor.href);
            downloadFilename = null;

            for (let i = 1; i <= 5; i++) {
                document.getElementById(`${i}`).value = "";
            }

            showRecvStatus(`Received ${downloadFilename}`);
            animReceive();
            
        })
        .catch(error => {
            console.error('Error while sending RECEIVE/ request', error);
            showRecvStatus("Failed to receive file.");
        });

}


function removeTransfer(code) {
    const options = {
        method: 'DELETE',
    };

    fetch(API + "delete/" + code, options)
        .then(response => response.json())
        .then(result => {
            if (result.status == false) {
                return showTransStatus(result.error);
            }

            removeHistoryRow(code);
            showTransStatus("Removed.")

        })
        .catch(error => {
            console.error('Error while sending DELETE/ request', error);
        });
}


function fetchOwnedCodes() {
    const options = {
        method: 'GET'
    };

    fetch(API + "owned-codes", options)
        .then(response => response.json())
        .then(result => {
            if (!result.status) { return showTransStatus(result.error); }
            
            for (const [code, data] of Object.entries(result.response)) {
                const name = data.file;
                const expire = data.expire;
                addHistoryRow(code, name, expire);
            }
            
        })
        .catch(error => {
            console.error('Error while sending OWNED-CODES/ request', error);
        });
}
