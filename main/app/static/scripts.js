$(document).ready(function() {
    $('a[href="' + this.location.pathname + '"]').parent().addClass('active');
});

function mailto(name, domain) {
    var mail='<a href="' + 'ma' + 'il' + 'to:' + name + '@' + domain + '">' + name + '@' + domain + '</a>';
    document.write(mail);
};