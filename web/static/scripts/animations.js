
const style_root = document.querySelector(':root');

function animTransfer() {
    const default_angle = 135;
    let i = 0;

    for (let angle = default_angle; angle < (default_angle + 180); angle++) {
        setTimeout(() => {
            style_root.style.setProperty("--tran-angle", `${angle}deg`);
        }, (++i) * 3)
    }
    style_root.style.setProperty("--tran-angle", `${default_angle}deg`);
}

function animReceive() {
    const default_angle = -135;
    let i = 0;

    for (let angle = default_angle; angle > (default_angle - 180); angle--) {
        setTimeout(() => {
            style_root.style.setProperty("--recv-angle", `${angle}deg`);
        }, (++i) * 3)
    }
    style_root.style.setProperty("--recv-angle", `${default_angle}deg`);
}
