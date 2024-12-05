const CODES_KEY = "codes";

if (localStorage.getItem(CODES_KEY) === null) {
    localStorage.setItem(CODES_KEY, "");
    console.log("Initialized cache.");
}


function getSavedCodes() {
    const raw_codes = localStorage.getItem(CODES_KEY);
    let codes = raw_codes.split(",");
    let intCodes = [];

    codes.forEach(c => {
        const intVal = parseInt(c);
        if (!isNaN(intVal)) {
            intCodes.push(intVal);
        }
    })

    return intCodes;
}

function cacheCode(code) {
    if (getSavedCodes().includes(code)) {return;}
    
    let codes = localStorage.getItem(CODES_KEY);
    codes += `,${code}`;
    localStorage.setItem(CODES_KEY, codes);
}

function uncacheCode(code) {
    if (!getSavedCodes().includes(code)) {return;}
   
    const codes = getSavedCodes();
    let newCodes = [];

    codes.forEach(c => {
        if (c != code) {
            newCodes.push(c);
        }
    })

    localStorage.setItem(CODES_KEY, newCodes);
}

function clearCache() {
    localStorage.setItem(CODES_KEY, "");
}
