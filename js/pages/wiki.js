app.endpoint_handler('page', function() {
    

    var textarea = $('#content');
    var editdiv = $('<div>').css({minHeight: '200px'}).insertBefore(textarea);
    textarea.hide();

    var editor = ace.edit(editdiv[0]);
    editor.setTheme('ace/theme/textmate')
    editor.getSession().setValue(textarea.val())

    ace.config.setModuleUrl("mymarkdown", "/js/ace/mymarkdown.js")
    editor.getSession().setMode('ace/mode/markdown')

    editor.setOptions({
        maxLines: Infinity
    });

    var resize = function () {

        var newHeight =
            editor.getSession().getScreenLength()
            * editor.renderer.lineHeight
            + editor.renderer.scrollBar.getWidth();

        editdiv.height(newHeight);
        editor.resize();

    }

    editor.on('change', resize);
    resize()

    textarea.closest('form').submit(function() {
        textarea.val(editor.getSession().getValue());
    })


});