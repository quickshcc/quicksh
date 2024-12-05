function showRecvStatus(message) {
    butterup.toast({
        title: '',
        icon: true,
        type: 'pop-recv',
        message: message,
        dismissable: true,
        location: 'bottom-right',
    });
}

function showTransStatus(message) {
    butterup.toast({
        title: '',
        icon: true,
        type: 'pop-trans',
        message: message,
        dismissable: true,
        location: 'bottom-right',
    });
}
