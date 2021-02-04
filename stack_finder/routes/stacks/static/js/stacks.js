function stack_click(name) {
    console.log(name);
    var url = window.location.href+"/"+name+"/outputs"
    url = url.replace('#', '');
    window.location = url; // this feels dirty, redo potentially
}